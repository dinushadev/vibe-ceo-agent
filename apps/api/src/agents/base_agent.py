"""
Base Agent Class - Common functionality for all ADK agents
Provides shared methods and patterns to reduce code duplication
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

from ..adk_utils import create_adk_runner
from ..memory.memory_service import get_memory_service

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all ADK-powered agents
    
    Provides common functionality:
    - Memory retrieval
    - ADK response generation
    - Response formatting
    - Error handling
    """
    
    def __init__(self, db, agent_id: str, memory_service=None):
        """
        Initialize base agent
        
        Args:
            db: Database instance
            agent_id: Unique identifier for this agent type
            memory_service: Optional memory service instance
        """
        self.db = db
        self.agent_id = agent_id
        self.memory_service = memory_service or get_memory_service(db)
        self.adk_agent = None  # To be set by subclass
    
    async def _get_memories(self, user_id: str, limit: int = 5, query: str = None) -> List[Dict]:
        """
        Retrieve long-term memory contexts for this agent
        
        Args:
            user_id: User identifier
            limit: Maximum number of memories to retrieve
            query: Optional query for semantic search
            
        Returns:
            List of memory dictionaries
        """
        if self.memory_service:
            return await self.memory_service.get_agent_memories(
                user_id, self.agent_id, limit=limit, query=query
            )
        else:
            return await self.db.get_agent_memories(
                user_id, self.agent_id, limit=limit
            )
    
    async def _generate_adk_response(
        self,
        user_id: str,
        prompt: str,
        default_response: str = "I'm here to help."
    ) -> tuple[str, List[str]]:
        """
        Generate response using ADK agent
        
        Args:
            user_id: User identifier
            prompt: Enhanced prompt with context
            default_response: Fallback response if generation fails
            
        Returns:
            Tuple of (response_text, tools_used)
        """
        if not self.adk_agent:
            logger.warning(f"{self.agent_id} agent: ADK agent not initialized")
            return default_response, []
        
        try:
            response_text, tools_used = await create_adk_runner(
                agent=self.adk_agent,
                user_id=user_id,
                prompt=prompt
            )
            
            return response_text or default_response, tools_used
            
        except Exception as e:
            logger.error(f"ADK response generation failed for {self.agent_id}: {e}")
            return default_response, []
    
    async def _store_interaction(
        self,
        user_id: str,
        user_message: str,
        agent_response: str
    ):
        """
        Store interaction in memory service (Short-Term & Long-Term)
        
        Args:
            user_id: User identifier
            user_message: User's message
            agent_response: Agent's response
        """
        if self.memory_service:
            try:
                # 1. Add to Short-Term Memory
                self.memory_service.add_to_short_term(user_id, "user", user_message)
                self.memory_service.add_to_short_term(user_id, "model", agent_response)
                
                # 2. Add to Long-Term Memory (Summarized)
                await self.memory_service.summarize_interaction(
                    user_id=user_id,
                    agent_id=self.agent_id,
                    user_message=user_message,
                    agent_response=agent_response
                )
            except Exception as e:
                logger.error(f"Failed to store interaction in memory: {e}")
    
    def _build_response_dict(
        self,
        response_text: str,
        metadata: Dict,
        latency_ms: int
    ) -> Dict:
        """
        Build standardized response dictionary
        
        Args:
            response_text: Agent's response text
            metadata: Additional metadata
            latency_ms: Response latency in milliseconds
            
        Returns:
            Formatted response dictionary
        """
        return {
            "agent_type": self.agent_id,
            "response": response_text,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                **metadata,
                "latency_ms": latency_ms,
                "adk_powered": self.adk_agent is not None
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
            "timestamp": datetime.now().isoformat(),
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
    
    @abstractmethod
    def _build_context_prompt(self, message: str, **kwargs) -> str:
        """
        Build context-enhanced prompt - must be implemented by subclass
        
        Args:
            message: User message
            **kwargs: Additional context data
            
        Returns:
            Enhanced prompt string
        """
        pass
