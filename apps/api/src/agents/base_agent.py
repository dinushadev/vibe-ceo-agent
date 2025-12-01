"""
Base Agent Class - Common functionality for all ADK agents
Provides shared methods and patterns to reduce code duplication
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

from ..adk_utils import create_adk_runner, get_tool_tracker
from ..memory.memory_service import get_memory_service

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all ADK-powered agents
    """
    
    def __init__(self, db, agent_id: str, memory_service=None):
        # ... (init code remains same, just showing context)
        self.db = db
        self.agent_id = agent_id
        self.memory_service = memory_service or get_memory_service(db)
        self.adk_agent = None  # To be set by subclass
    
    async def _get_memories(self, user_id: str, query: str = None, limit: int = 5) -> List[Dict]:
        """
        Retrieve relevant memories for this agent
        """
        if not self.memory_service:
            return []
            
        return await self.memory_service.get_agent_memories(
            user_id=user_id,
            agent_id=self.agent_id,
            limit=limit,
            query=query
        )

    async def _get_personal_context(self, user_id: str) -> str:
        """
        Get comprehensive personal context (facts, prefs, medical, etc.)
        """
        if not self.memory_service:
            return ""
            
        return await self.memory_service.get_user_context(user_id)

    async def _store_interaction(self, user_id: str, message: str, response: str):
        """
        Store the interaction in memory
        """
        if self.memory_service:
            await self.memory_service.summarize_interaction(
                user_id=user_id,
                agent_id=self.agent_id,
                user_message=message,
                agent_response=response
            )

    async def _generate_adk_response(
        self,
        user_id: str,
        prompt: str,
        default_response: str = "I'm here to help."
    ) -> tuple[str, List[str]]:
        """
        Generate response using ADK agent
        """
        if not self.adk_agent:
            logger.warning(f"{self.agent_id} agent: ADK agent not initialized")
            return default_response, []
        
        try:
            # Clear tool tracker for new request
            get_tool_tracker().clear()
            
            response_text, tools_used = await create_adk_runner(
                agent=self.adk_agent,
                user_id=user_id,
                prompt=prompt
            )
            
            return response_text or default_response, tools_used
            
        except Exception as e:
            logger.error(f"ADK response generation failed for {self.agent_id}: {e}")
            return default_response, []
    

    
    def _build_response_dict(
        self,
        response_text: str,
        metadata: Dict,
        latency_ms: int
    ) -> Dict:
        """
        Build standardized response dictionary
        """
        # Get tool executions from tracker
        tool_executions = get_tool_tracker().get_executions()
        
        return {
            "agent_type": self.agent_id,
            "response": response_text,
            "timestamp": f"{datetime.utcnow().isoformat()}Z",
            "metadata": {
                **metadata,
                "latency_ms": latency_ms,
                "adk_powered": self.adk_agent is not None,
                "tool_executions": tool_executions # Include detailed tool logs
            }
        }
    
    def _build_error_response(self, error: Exception, custom_message: str = None) -> Dict:
        """
        Build standardized error response
        
        Args:
            error: Exception that occurred
            custom_message: Optional custom error message
            
        Returns:
            Error response dictionary
        """
        message = custom_message or "I encountered an issue processing your request. Please try again."
        
        return {
            "agent_type": self.agent_id,
            "response": message,
            "timestamp": f"{datetime.utcnow().isoformat()}Z",
            "metadata": {"error": str(error)}
        }
    
    @abstractmethod
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process user message - must be implemented by subclass
        
        Args:
            user_id: User identifier
            message: User's message
            context: Optional conversation context
            
        Returns:
            Response dictionary
        """
        pass
    
    async def _build_context_prompt(self, message: str, **kwargs) -> str:
        """
        Build context-enhanced prompt using shared utility
        
        Args:
            message: User message
            **kwargs: Additional context data (user_id, memories, health_data, personal_context)
            
        Returns:
            Enhanced prompt string
        """
        from .context_utils import build_context_prompt
        
        return await build_context_prompt(
            message=message,
            user_id=kwargs.get("user_id"),
            db=self.db,
            memories=kwargs.get("memories"),
            health_data=kwargs.get("health_data"),
            personal_context=kwargs.get("personal_context", "")
        )

