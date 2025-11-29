"""
ADK Memory Service
Integrates ADK's memory capabilities with the database for persistent storage
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


from .vector_store import VectorStore
from collections import deque
import uuid

class SessionMemory:
    """
    Short-term memory management using sliding window
    """
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.history: Dict[str, deque] = {}  # user_id -> deque of messages

    def add_message(self, user_id: str, role: str, content: str):
        if user_id not in self.history:
            self.history[user_id] = deque(maxlen=self.max_turns)
        
        self.history[user_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_history(self, user_id: str) -> List[Dict]:
        if user_id not in self.history:
            return []
        return list(self.history[user_id])


class ADKMemoryService:
    """
    Memory service that bridges ADK agents with persistent storage.
    Combines Short-Term (Session) and Long-Term (Vector) memory.
    """
    
    def __init__(self, db):
        self.db = db
        self.vector_store = VectorStore()
        self.session_memory = SessionMemory()
        logger.info("ADK Memory Service initialized with Vector Store")
    
    async def get_agent_memories(
        self,
        user_id: str,
        agent_id: str,
        limit: int = 5,
        query: str = None
    ) -> List[Dict]:
        """
        Retrieve agent-specific memories using Semantic Search (Long-Term)
        """
        if query:
            # Semantic search
            results = await self.vector_store.search(query, user_id, agent_id, limit)
            return results
        else:
            # Fallback to recent memories from DB if no query
            try:
                memories = await self.db.get_agent_memories(user_id, agent_id, limit)
                return memories
            except Exception as e:
                logger.error(f"Failed to retrieve memories: {e}")
                return []
    
    async def store_memory(
        self,
        user_id: str,
        agent_id: str,
        summary_text: str,
        data_source_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Store a new memory context in Vector Store (Long-Term)
        """
        try:
            context_id = f"mem_{agent_id}_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # 1. Store in SQL DB (for backup/admin view)
            await self.db.create_memory_context(
                context_id=context_id,
                user_id=user_id,
                agent_id=agent_id,
                summary_text=summary_text,
                data_source_id=data_source_id,
                metadata=metadata
            )
            
            # 2. Store in Vector DB (for semantic recall)
            await self.vector_store.add_document(
                doc_id=context_id,
                content=summary_text,
                metadata=metadata or {},
                user_id=user_id,
                agent_id=agent_id
            )
            
            logger.info(f"Stored memory for {agent_id} agent, user {user_id}")
            return {"id": context_id, "summary": summary_text}
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return {}
    
    def add_to_short_term(self, user_id: str, role: str, content: str):
        """Add message to short-term session memory"""
        self.session_memory.add_message(user_id, role, content)

    def get_short_term_context(self, user_id: str) -> str:
        """Get formatted short-term history"""
        history = self.session_memory.get_history(user_id)
        if not history:
            return ""
        
        formatted = "Current Conversation:\n"
        for msg in history:
            formatted += f"{msg['role']}: {msg['content']}\n"
        return formatted

    async def summarize_interaction(
        self,
        user_id: str,
        agent_id: str,
        user_message: str,
        agent_response: str
    ) -> str:
        """
        Create a summary of an interaction for memory storage
        """
        # In a real app, use an LLM to summarize. For now, simple truncation.
        summary = f"User asked: {user_message[:50]}... Agent ({agent_id}) replied: {agent_response[:50]}..."
        
        await self.store_memory(
            user_id=user_id,
            agent_id=agent_id,
            summary_text=summary,
            metadata={
                "user_message": user_message[:200],
                "response_preview": agent_response[:200],
                "timestamp": datetime.now().isoformat()
            }
        )
        return summary

    async def get_user_context(self, user_id: str) -> str:
        """
        Get comprehensive user context including facts, preferences, medical info, and activities
        
        Args:
            user_id: User identifier
            
        Returns:
            Formatted context string with all personal data
        """
        context_parts = []
        
        try:
            # 1. User Facts
            facts = await self.db.get_user_facts(user_id)
            if facts:
                context_parts.append("USER FACTS:")
                for fact in facts:
                    context_parts.append(f"  - {fact['fact_key']}: {fact['fact_value']}")
            
            # 2. User Preferences
            preferences = await self.db.get_user_preferences(user_id)
            if preferences:
                context_parts.append("\nUSER PREFERENCES:")
                for pref in preferences:
                    context_parts.append(f"  - {pref['pref_key']}: {pref['pref_value']}")
            
            # 3. Medical Profile
            medical_profile = await self.db.get_user_medical_profile(user_id)
            if medical_profile:
                context_parts.append("\nMEDICAL PROFILE:")
                for condition in medical_profile:
                    context_parts.append(f"  - {condition['condition_name']} ({condition['status']})")
                    if condition.get('medications'):
                        meds = ", ".join(condition['medications'])
                        context_parts.append(f"    Medications: {meds}")
            
            # 4. Pending Tasks
            tasks = await self.db.get_user_tasks(user_id, status="pending")
            if tasks:
                context_parts.append("\nPENDING TASKS:")
                for task in tasks[:5]:  # Limit to 5 most recent
                    priority_marker = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
                    due = f" (Due: {task['due_date']})" if task.get('due_date') else ""
                    context_parts.append(f"  {priority_marker} {task['title']}{due}")
            
            # 5. Upcoming Events
            from datetime import datetime
            now = datetime.utcnow().isoformat()
            events = await self.db.get_user_events(user_id, start_after=now)
            if events:
                context_parts.append("\nUPCOMING EVENTS:")
                for event in events[:5]:  # Limit to 5 upcoming
                    start = event['start_time'][:16].replace('T', ' ')  # Format: YYYY-MM-DD HH:MM
                    context_parts.append(f"  📅 {event['title']} - {start}")
            
            if context_parts:
                return "\n".join(context_parts)
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Failed to get user context: {e}")
            return ""



# Global instance
_memory_service: Optional[ADKMemoryService] = None


def get_memory_service(db=None) -> Optional[ADKMemoryService]:
    """Get or create the global memory service instance"""
    global _memory_service
    if _memory_service is None and db is not None:
        _memory_service = ADKMemoryService(db)
    return _memory_service
