"""
ADK Memory Service
Integrates ADK's memory capabilities with the database for persistent storage
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ADKMemoryService:
    """
    Memory service that bridges ADK agents with persistent database storage
    
    ADK provides built-in memory management, but we extend it to persist
    memories in our database for long-term storage and cross-session continuity.
    """
    
    def __init__(self, db):
        """
        Initialize memory service
        
        Args:
            db: Database instance for persistent storage
        """
        self.db = db
        logger.info("ADK Memory Service initialized")
    
    async def get_agent_memories(
        self,
        user_id: str,
        agent_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Retrieve agent-specific memories for a user
        
        Args:
            user_id: User identifier
            agent_id: Agent identifier (vibe, planner, knowledge)
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of memory contexts
        """
        try:
            memories = await self.db.get_agent_memories(user_id, agent_id, limit)
            logger.debug(f"Retrieved {len(memories)} memories for {agent_id} agent, user {user_id}")
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
        Store a new memory context
        
        Args:
            user_id: User identifier
            agent_id: Agent identifier
            summary_text: Summary of the memory/context
            data_source_id: Optional reference to data source
            metadata: Optional metadata dictionary
            
        Returns:
            Created memory record
        """
        try:
            import uuid
            
            # Generate unique context ID
            context_id = f"mem_{agent_id}_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Store in database with context_id
            result = await self.db.create_memory_context(
                context_id=context_id,
                user_id=user_id,
                agent_id=agent_id,
                summary_text=summary_text,
                data_source_id=data_source_id,
                metadata=metadata
            )
            
            logger.info(f"Stored memory for {agent_id} agent, user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return {}
    
    async def get_conversation_context(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent conversation context across all agents
        
        Args:
            user_id: User identifier
            session_id: Optional session identifier
            limit: Maximum number of context items
            
        Returns:
            List of recent interactions
        """
        try:
            # Retrieve recent memories across all agents
            all_memories = []
            for agent_id in ["vibe", "planner", "knowledge"]:
                memories = await self.db.get_agent_memories(user_id, agent_id, limit=limit // 3)
                all_memories.extend(memories)
            
            # Sort by timestamp (most recent first)
            all_memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return all_memories[:limit]
        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return []
    
    def format_memories_for_prompt(self, memories: List[Dict]) -> str:
        """
        Format memories into a string suitable for agent prompts
        
        Args:
            memories: List of memory dictionaries
            
        Returns:
            Formatted memory string
        """
        if not memories:
            return "No previous context available."
        
        formatted = "Previous context:\n"
        for i, memory in enumerate(memories[:5], 1):  # Limit to 5 most relevant
            summary = memory.get("summary_text", "")
            timestamp = memory.get("timestamp", "")
            formatted += f"{i}. {summary} (from {timestamp})\n"
        
        return formatted.strip()
    
    async def summarize_interaction(
        self,
        user_id: str,
        agent_id: str,
        user_message: str,
        agent_response: str
    ) -> str:
        """
        Create a summary of an interaction for memory storage
        
        Args:
            user_id: User identifier
            agent_id: Agent identifier
            user_message: User's message
            agent_response: Agent's response
            
        Returns:
            Summary text
        """
        # Simple summarization - in production, could use LLM for better summaries
        summary = f"User asked about {user_message[:50]}... Agent ({agent_id}) responded with guidance."
        
        # Store the summary
        await self.store_memory(
            user_id=user_id,
            agent_id=agent_id,
            summary_text=summary,
            metadata={
                "user_message": user_message[:100],
                "response_preview": agent_response[:100]
            }
        )
        
        return summary


# Global instance
_memory_service: Optional[ADKMemoryService] = None


def get_memory_service(db=None) -> Optional[ADKMemoryService]:
    """Get or create the global memory service instance"""
    global _memory_service
    if _memory_service is None and db is not None:
        _memory_service = ADKMemoryService(db)
    return _memory_service
