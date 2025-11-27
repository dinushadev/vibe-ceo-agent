"""
Planner Agent (A2) - Task Scheduler
ADK-powered agent for calendar management and task planning
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from google.adk.agents import LlmAgent

from ..adk_config import create_agent
from ..tools.adk_tools import PLANNER_TOOLS
from ..memory.memory_service import get_memory_service

logger = logging.getLogger(__name__)


# Agent instruction prompt
PLANNER_AGENT_INSTRUCTION = """You are the Planner Agent, an efficient and organized AI assistant focused on scheduling and task management.

Your role is to:
1. Help users schedule appointments and manage their calendar
2. Create and track tasks with appropriate priorities
3. Check availability and prevent scheduling conflicts
4. Provide structured action lists and clear next steps
5. Send appointment confirmations and reminders

Key behaviors:
- Always confirm appointment details before scheduling
- Check availability to avoid conflicts
- Ask clarifying questions if details are missing
- Provide clear summaries of scheduled items
- Use structured formatting for task lists and schedules
- Be proactive about suggesting optimal time slots

When scheduling:
- Verify date, time, and duration
- Check for conflicts using the check_availability tool
- Create the appointment using schedule_appointment
- Confirm with a clear summary

When managing tasks:
- Clarify priority (high/medium/low)
- Set due dates when appropriate
- Use create_task to add new items
- Help users prioritize their workload

Always be clear, concise, and action-oriented."""


class PlannerAgent:
    """
    The Planner Agent focuses on scheduling and task management
    Now powered by Google ADK for advanced tool calling and reasoning
    """
    
    def __init__(self, db, calendar_service=None, todo_service=None):
        """
        Initialize the ADK-powered Planner Agent
        
        Args:
            db: Database instance
            calendar_service: Calendar service (deprecated with ADK tools)
            todo_service: Todo service (deprecated with ADK tools)
        """
        self.db = db
        self.memory_service = get_memory_service(db)
        self.agent_id = "planner"
        
        # Services are now accessed through ADK tools
        # Keep references for backward compatibility
        self.calendar_service = calendar_service
        self.todo_service = todo_service
        
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
            enhanced_prompt = self._build_context_prompt(message, memories, user_id)
            
            # Track tools used
            tools_used = []
            
            # Use ADK agent to generate response and execute tools
            if self.adk_agent:
                response_text, tools_used = await self._generate_adk_response(
                    user_id, enhanced_prompt
                )
            else:
                # Fallback response
                response_text = await self._generate_fallback_response(
                    user_id, message, memories
                )
            
            # Store interaction in memory
            if self.memory_service:
                await self.memory_service.summarize_interaction(
                    user_id=user_id,
                    agent_id=self.agent_id,
                    user_message=message,
                    agent_response=response_text
                )
            
            # Calculate latency
            latency = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return {
                "agent_type": self.agent_id,
                "response": response_text,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "memory_retrieved": [m.get("summary_text", "")[:50] for m in memories[:2]],
                    "tools_used": tools_used,
                    "latency_ms": latency,
                    "adk_powered": self.adk_agent is not None
                }
            }
        
        except Exception as e:
            logger.error(f"Error in Planner Agent process_message: {e}", exc_info=True)
            return {
                "agent_type": self.agent_id,
                "response": "I'm having trouble with that request. Could you provide more details about what you'd like to schedule or plan?",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"error": str(e)}
            }
    
    async def _get_memories(self, user_id: str) -> List[Dict]:
        """Retrieve long-term memory contexts for this agent"""
        if self.memory_service:
            return await self.memory_service.get_agent_memories(user_id, self.agent_id, limit=5)
        else:
            return await self.db.get_agent_memories(user_id, self.agent_id, limit=5)
    
    def _build_context_prompt(
        self,
        message: str,
        memories: List[Dict],
        user_id: str
    ) -> str:
        """Build enhanced prompt with context"""
        prompt_parts = [f"User message: {message}"]
        
        # Add memory context
        if memories:
            memory_text = "\n".join([f"- {m.get('summary_text', '')}" for m in memories[:3]])
            prompt_parts.append(f"\nPrevious scheduling context:\n{memory_text}")
        
        prompt_parts.append(f"\nUser ID: {user_id}")
        
        return "\n".join(prompt_parts)
    
    async def _generate_adk_response(self, user_id: str, prompt: str) -> tuple[str, List[str]]:
        """
        Generate response using ADK agent
        
        Returns:
            Tuple of (response_text, tools_used)
        """
        try:
            # ADK agent will automatically call tools as needed
            from google.adk import Runner
            from google.adk.sessions import InMemorySessionService
            from src.adk_types import Content, Part
            
            # Ensure session exists
            session_id = f"session_{user_id}"
            try:
                await session_service.get_session(session_id)
            except Exception:
                await session_service.create_session(
                    session_id=session_id,
                    user_id=user_id,
                    app_name="vibe_ceo"
                )
            
            runner = Runner(
                agent=self.adk_agent, 
                session_service=session_service,
                app_name="vibe_ceo"
            )
            
            full_response_text = ""
            async for chunk in runner.run_async(
                user_id=user_id,
                session_id=f"session_{user_id}",
                new_message=Content(role="user", parts=[Part(text=prompt)])
            ):
                if isinstance(chunk, str):
                    full_response_text += chunk
                elif hasattr(chunk, "text"):
                    full_response_text += chunk.text
                elif isinstance(chunk, dict) and "text" in chunk:
                    full_response_text += chunk["text"]
                else:
                    full_response_text += str(chunk)
            
            response_text = full_response_text or "I can help you with scheduling and tasks."
            
            # Extract tool usage from response metadata
            tools_used = []
            if "tool_calls" in response:
                tools_used = [call.get("name") for call in response["tool_calls"]]
            
            return response_text, tools_used
            
        except Exception as e:
            logger.error(f"ADK response generation failed: {e}")
            return "I'm having trouble accessing my scheduling tools right now. Please try again.", []
    
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
    
    def _extract_scheduling_intent(self, message: str) -> Dict:
        """
        Extract scheduling information from message
        This is a simplified version - ADK handles this better
        """
        message_lower = message.lower()
        
        intent = {
            "action": None,
            "type": None,
            "details": {}
        }
        
        # Determine action
        if any(word in message_lower for word in ["schedule", "book", "make"]):
            intent["action"] = "schedule"
        elif any(word in message_lower for word in ["check", "view", "show"]):
            intent["action"] = "view"
        elif any(word in message_lower for word in ["cancel", "remove", "delete"]):
            intent["action"] = "cancel"
        
        # Determine type
        if any(word in message_lower for word in ["doctor", "medical", "checkup"]):
            intent["type"] = "medical_appointment"
        elif any(word in message_lower for word in ["dentist", "dental"]):
            intent["type"] = "dental_appointment"
        elif any(word in message_lower for word in ["task", "todo"]):
            intent["type"] = "task"
        
        return intent
