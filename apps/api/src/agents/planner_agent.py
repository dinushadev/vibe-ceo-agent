"""
Planner Agent (A2) - Task and Calendar Management
Handles scheduling and task management with tool calling
"""

import logging
import uuid
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PlannerAgent:
    """
    The Planner Agent manages tasks and calendar events
    
    Features:
    - Schedules appointments and tasks
    - Calls external tools (calendar, todo services)
    - Generates structured action lists (O2)
    - Logs tool actions for observability (NFR3)
    """
    
    def __init__(self, db, calendar_service, todo_service):
        """
        Initialize the Planner Agent
        
        Args:
            db: Database instance for logging
            calendar_service: Calendar tool service
            todo_service: Todo list tool service
        """
        self.db = db
        self.calendar_service = calendar_service
        self.todo_service = todo_service
        self.agent_id = "planner"
        logger.info("PlannerAgent initialized")
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process user message and handle scheduling requests
        
        Args:
            user_id: User identifier
            message: User's message
            context: Optional conversation context
            
        Returns:
            Response with tool execution results
        """
        start_time = datetime.now()
        tools_used = []
        
        # Determine intent: schedule vs query vs task
        intent = self._classify_planning_intent(message)
        
        if intent == "schedule_event":
            result = await self._handle_scheduling(user_id, message)
            tools_used.append("calendar_service")
        
        elif intent == "create_task":
            result = await self._handle_task_creation(user_id, message)
            tools_used.append("todo_service")
        
        elif intent == "query_schedule":
            result = await self._handle_schedule_query(user_id, message)
            tools_used.append("calendar_service")
        
        else:
            result = {
                "response": "I can help you schedule appointments, create tasks, or check your calendar. What would you like to do?",
                "action_list": []
            }
        
        # Calculate latency
        latency = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return {
            "agent_type": self.agent_id,
            "response": result["response"],
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "tools_used": tools_used,
                "action_list": result.get("action_list", []),
                "latency_ms": latency
            }
        }
    
    async def _handle_scheduling(self, user_id: str, message: str) -> Dict:
        """
        Handle appointment scheduling (FR3)
        
        This demonstrates tool calling capability
        """
        # Extract scheduling details (simplified - in production use NLU)
        message_lower = message.lower()
        
        # Determine appointment type and time
        if "doctor" in message_lower or "checkup" in message_lower or "medical" in message_lower:
            title = "Medical Check-up"
            description = "Regular health check-up appointment"
            start_time = "next week"
        elif "dentist" in message_lower:
            title = "Dentist Appointment"
            description = "Dental check-up"
            start_time = "next week"
        else:
            title = "Appointment"
            description = "Scheduled appointment"
            start_time = "tomorrow"
        
        # Call calendar service tool
        tool_start = datetime.now()
        
        try:
            event = await self.calendar_service.schedule_event(
                title=title,
                description=description,
                start_time=start_time,
                duration_minutes=60
            )
            
            tool_time = int((datetime.now() - tool_start).total_seconds() * 1000)
            
            # Log tool action for observability (NFR3)
            await self.db.log_tool_action(
                log_id=str(uuid.uuid4()),
                user_id=user_id,
                tool_name="calendar_service.schedule_event",
                input_query=message,
                output_result=f"Scheduled: {event['title']} at {event['start_time']}",
                success=True,
                execution_time_ms=tool_time
            )
            
            # Generate structured action list (O2)
            action_list = [
                {
                    "action": "scheduled_event",
                    "event_id": event["event_id"],
                    "title": event["title"],
                    "time": event["start_time"],
                    "status": "confirmed"
                }
            ]
            
            response = (
                f"✅ I've scheduled your {title} for {event['start_time']}. "
                f"The appointment is confirmed and has been added to your calendar."
            )
            
            return {
                "response": response,
                "action_list": action_list
            }
        
        except Exception as e:
            logger.error(f"Error scheduling event: {e}")
            
            await self.db.log_tool_action(
                log_id=str(uuid.uuid4()),
                user_id=user_id,
                tool_name="calendar_service.schedule_event",
                input_query=message,
                output_result=f"Error: {str(e)}",
                success=False,
                execution_time_ms=int((datetime.now() - tool_start).total_seconds() * 1000)
            )
            
            return {
                "response": "I encountered an issue scheduling the appointment. Please try again.",
                "action_list": []
            }
    
    async def _handle_task_creation(self, user_id: str, message: str) -> Dict:
        """Handle creating tasks"""
        message_lower = message.lower()
        
        # Extract task details
        if "meditation" in message_lower or "mindful" in message_lower:
            title = "Daily Meditation Practice"
            priority = "high"
        elif "exercise" in message_lower or "workout" in message_lower:
            title = "Regular Exercise"
            priority = "high"
        else:
            title = "New Task"
            priority = "medium"
        
        tool_start = datetime.now()
        
        try:
            task = await self.todo_service.create_task(
                title=title,
                description=f"Task created from: {message}",
                priority=priority
            )
            
            tool_time = int((datetime.now() - tool_start).total_seconds() * 1000)
            
            # Log tool action
            await self.db.log_tool_action(
                log_id=str(uuid.uuid4()),
                user_id=user_id,
                tool_name="todo_service.create_task",
                input_query=message,
                output_result=f"Created task: {task['title']}",
                success=True,
                execution_time_ms=tool_time
            )
            
            action_list = [
                {
                    "action": "created_task",
                    "task_id": task["task_id"],
                    "title": task["title"],
                    "priority": task["priority"],
                    "status": "pending"
                }
            ]
            
            return {
                "response": f"✅ I've added '{title}' to your to-do list with {priority} priority.",
                "action_list": action_list
            }
        
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return {
                "response": "I had trouble creating that task. Please try again.",
                "action_list": []
            }
    
    async def _handle_schedule_query(self, user_id: str, message: str) -> Dict:
        """Query upcoming schedule"""
        try:
            events = await self.calendar_service.get_upcoming_events(days_ahead=7)
            
            if not events:
                return {
                    "response": "You don't have any upcoming appointments in the next week.",
                    "action_list": []
                }
            
            event_summaries = [
                f"- {event['title']} on {event['start_time']}"
                for event in events[:5]
            ]
            
            response = "Here are your upcoming appointments:\n" + "\n".join(event_summaries)
            
            return {
                "response": response,
                "action_list": [{"action": "listed_events", "count": len(events)}]
            }
        
        except Exception as e:
            logger.error(f"Error querying schedule: {e}")
            return {
                "response": "I couldn't retrieve your schedule right now.",
                "action_list": []
            }
    
    def _classify_planning_intent(self, message: str) -> str:
        """Classify the type of planning request"""
        message_lower = message.lower()
        
        # Check for scheduling keywords
        schedule_keywords = ["schedule", "book", "appointment", "doctor", "dentist", "checkup"]
        if any(kw in message_lower for kw in schedule_keywords):
            return "schedule_event"
        
        # Check for task keywords
        task_keywords = ["task", "todo", "add", "remind", "meditation", "exercise"]
        if any(kw in message_lower for kw in task_keywords):
            return "create_task"
        
        # Check for query keywords
        query_keywords = ["what's", "check", "upcoming", "calendar", "schedule"]
        if any(kw in message_lower for kw in query_keywords) and "my" in message_lower:
            return "query_schedule"
        
        return "general"
