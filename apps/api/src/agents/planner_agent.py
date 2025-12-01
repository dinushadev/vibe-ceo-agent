"""
Planner Agent (A2) - Task Scheduler
ADK-powered agent for calendar management and task planning
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from ..adk_config import create_agent
from ..tools.adk_tools import PLANNER_TOOLS
from .base_agent import BaseAgent
from .prompts import PLANNER_AGENT_INSTRUCTION

logger = logging.getLogger(__name__)





class PlannerAgent(BaseAgent):
    """
    The Planner Agent focuses on scheduling and task management
    Now powered by Google ADK for advanced tool calling and reasoning
    """
    
    def __init__(self, db, calendar_service=None, todo_service=None):
        """
        Initialize the ADK-powered Planner Agent
        
        Args:
            db: Database instance
            calendar_service: Deprecated - kept for backward compatibility
            todo_service: Deprecated - kept for backward compatibility
        """
        super().__init__(db, agent_id="planner")
        
        # Create ADK agent with planner tools
        try:
            self.adk_agent = create_agent(
                name="planner_agent",
                instruction=PLANNER_AGENT_INSTRUCTION,
                description="An organized agent for scheduling appointments and managing tasks",
                tools=PLANNER_TOOLS
            )
            logger.info("ADK Planner Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ADK Planner Agent: {e}")
            logger.warning("Planner Agent will operate with limited functionality")
            self.adk_agent = None
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process user message using ADK agent with tool calling
        
        Args:
            user_id: User identifier
            message: User's message
            context: Optional conversation context
            
        Returns:
            Response with agent metadata
        """
        start_time = datetime.now()
        
        try:
            # Retrieve relevant memories
            memories = await self._get_memories(user_id)
            
            # Build context-enhanced prompt
            enhanced_prompt = await self._build_context_prompt(
                message=message,
                memories=memories,
                user_id=user_id
            )
            
            # Use ADK agent to generate response and execute tools
            tools_used = []
            if self.adk_agent:
                response_text, tools_used = await self._generate_adk_response(
                    user_id, 
                    enhanced_prompt,
                    default_response="I'm having trouble accessing my scheduling tools right now. Please try again."
                )
            else:
                # Fallback response
                response_text = await self._generate_fallback_response(
                    user_id, message, memories
                )
            
            # Store interaction in memory
            await self._store_interaction(user_id, message, response_text)
            
            # Calculate latency
            latency = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return self._build_response_dict(
                response_text,
                {
                    "memory_retrieved": [m.get("summary_text", "")[:50] for m in memories[:2]],
                    "tools_used": tools_used
                },
                latency
            )
        
        except Exception as e:
            logger.error(f"Error in Planner Agent process_message: {e}", exc_info=True)
            return self._build_error_response(e, "I'm having trouble with that request. Could you provide more details about what you'd like to schedule or plan?")
    

    
    async def _generate_fallback_response(
        self,
        user_id: str,
        message: str,
        memories: List[Dict]
    ) -> str:
        """Fallback response when ADK is not available"""
        message_lower = message.lower()
        
        # Basic intent detection
        if any(word in message_lower for word in ["schedule", "book", "appointment"]):
            return (
                "I can help you schedule that. To book an appointment, I'll need:\n"
                "1. What type of appointment (e.g., doctor, dentist)\n"
                "2. Preferred date (YYYY-MM-DD)\n"
                "3. Preferred time\n"
                "4. Duration (if known)\n\n"
                "Please provide these details and I'll check availability."
            )
        
        elif any(word in message_lower for word in ["task", "todo", "remind"]):
            return (
                "I can create a task for you. Please tell me:\n"
                "1. What the task is\n"
                "2. Priority (high, medium, or low)\n"
                "3. Due date (if any)\n\n"
                "I'll add it to your task list."
            )
        
        elif any(word in message_lower for word in ["upcoming", "scheduled", "calendar"]):
            return (
                "I can check your upcoming appointments and tasks. "
                "Would you like to see:\n"
                "- Upcoming appointments\n"
                "- Pending tasks\n"
                "- Both?"
            )
        
        else:
            return (
                "I'm your Planner Agent. I can help you:\n"
                "- Schedule appointments\n"
                "- Manage tasks\n"
                "- Check your calendar\n"
                "- Set reminders\n\n"
                "What would you like to plan?"
            )
