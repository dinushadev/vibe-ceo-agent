"""
Knowledge Agent (A3) - Learning Digest Curator
ADK-powered agent for personalized learning content curation
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from ..adk_config import create_agent
from ..tools.adk_tools import KNOWLEDGE_TOOLS
from .base_agent import BaseAgent
from .prompts import KNOWLEDGE_AGENT_INSTRUCTION

logger = logging.getLogger(__name__)





class KnowledgeAgent(BaseAgent):
    """
    The Knowledge Agent focuses on learning content curation
    Now powered by Google ADK for advanced search and structured output
    """
    
    def __init__(self, db, search_service=None):
        """
        Initialize the ADK-powered Knowledge Agent
        
        Args:
            db: Database instance
            search_service: Deprecated - kept for backward compatibility
        """
        super().__init__(db, agent_id="knowledge")
        
        # Create ADK agent with knowledge tools
        try:
            self.adk_agent = create_agent(
                name="knowledge_agent",
                instruction=KNOWLEDGE_AGENT_INSTRUCTION,
                description="A curator for personalized learning digests and research",
                tools=KNOWLEDGE_TOOLS
            )
            logger.info("ADK Knowledge Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ADK Knowledge Agent: {e}")
            logger.warning("Knowledge Agent will operate with limited functionality")
            self.adk_agent = None
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process user message using ADK agent with search tools
        
        Args:
            user_id: User identifier
            message: User's message
            context: Optional conversation context
            
        Returns:
            Response with agent metadata
        """
        start_time = datetime.now()
        
        try:
            # Retrieve relevant memories and profile (Proactive Search)
            memories = await self._get_memories(user_id, query=message)
            user_profile = await self._get_user_profile(user_id)
            
            # Build context-enhanced prompt
            # Format user profile as personal context
            personal_context = ""
            if user_profile:
                interests = user_profile.get("learning_interests", [])
                personal_context = f"User Interests: {', '.join(interests)}"
            
            enhanced_prompt = await self._build_context_prompt(
                message=message,
                memories=memories,
                user_id=user_id,
                personal_context=personal_context
            )
            
            # Use ADK agent to generate response and execute tools
            tools_used = []
            if self.adk_agent:
                response_text, tools_used = await self._generate_adk_response(
                    user_id, 
                    enhanced_prompt,
                    default_response="Error: Search unavailable."
                )
            else:
                # Fallback response
                response_text = await self._generate_fallback_response(
                    user_id, message, memories, user_profile
                )
            
            # Store interaction in memory
            await self._store_interaction(user_id, message, response_text)
            
            # Calculate latency
            latency = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return self._build_response_dict(
                response_text,
                {
                    "memory_retrieved": [m.get("summary_text", "")[:50] for m in memories[:2]],
                    "tools_used": tools_used,
                    "learning_interests": user_profile.get("learning_interests", []) if user_profile else []
                },
                latency
            )
        
        except Exception as e:
            logger.error(f"Error in Knowledge Agent process_message: {e}", exc_info=True)
            return self._build_error_response(e, "Error: Curation failed.")
    
    async def _get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile with learning interests"""
        try:
            return await self.db.get_user(user_id)
        except Exception:
            return None
    

    
    async def _generate_fallback_response(
        self,
        user_id: str,
        message: str,
        memories: List[Dict],
        user_profile: Optional[Dict]
    ) -> str:
        """Fallback response when ADK is not available"""
        message_lower = message.lower()
        
        # Basic topic extraction
        topic = "that topic"
        if "about" in message_lower:
            parts = message_lower.split("about", 1)
            if len(parts) > 1:
                topic = parts[1].strip().strip("?.!")
        
        return f"Researching: {topic}..."
