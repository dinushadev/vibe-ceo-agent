"""
Planner Tool (Agent-as-a-Tool)
Uses a secondary LLM to analyze calendar and health data to provide strategic planning advice.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

from google import genai
from google.genai import types

from src.db.database import get_database
from src.tools.mock_tools import get_calendar_service, get_todo_service
from src.memory.memory_service import get_memory_service

logger = logging.getLogger(__name__)

class PlannerTool:
    """
    Intelligent Planner Agent exposed as a tool.
    """
    
    def __init__(self):
        self.calendar_service = get_calendar_service()
        self.todo_service = get_todo_service()
        # Initialize Memory Service (with DB connection handled lazily or globally)
        # Note: get_memory_service requires a DB instance if not already initialized.
        # We'll assume it's initialized by the main app startup.
        self.memory_service = get_memory_service() 
        self.model_id = "gemini-2.0-flash-exp"
        self.model_id = "gemini-2.0-flash-exp"
        
        try:
            self.client = genai.Client(
                http_options={'api_version': 'v1alpha'}
            )
        except Exception as e:
            logger.error(f"Failed to initialize GenAI client for Planner: {e}")
            self.client = None

    async def consult_planner(self, user_request: str, user_id: str = "user_123") -> str:
        """
        Analyzes the user's schedule, tasks, and health logs to provide a strategic plan.
        
        Args:
            user_request: The user's natural language request (e.g., "I'm overwhelmed, fix my day")
            user_id: The ID of the user (defaulting for MVP)
            
        Returns:
            A text response containing the strategic plan.
        """
        logger.info(f"Planner Tool invoked for user {user_id}: {user_request}")
        
        # 1. Gather Context Data
        db = await get_database()
        
        # Get Memory Context
        short_term_context = ""
        long_term_memories = []
        if self.memory_service:
            short_term_context = self.memory_service.get_short_term_context(user_id)
            long_term_memories = await self.memory_service.get_agent_memories(user_id, "planner", query=user_request)
            
        # Get Calendar (Next 3 days)
        events = await self.calendar_service.get_upcoming_events(days_ahead=3)
        
        # Get Tasks
        tasks = await self.todo_service.get_tasks(status="pending")
        
        # Get Health Logs (Last 3 entries)
        health_logs = await db.get_user_health_logs(user_id, limit=3)
        
        # Format context for the LLM
        context_str = json.dumps({
            "current_time": datetime.now().isoformat(),
            "calendar_events": events,
            "pending_tasks": tasks,
            "recent_health_logs": health_logs
        }, indent=2)
        
        # Format memory string
        memory_str = ""
        if long_term_memories:
            memory_str = "\nRELEVANT PAST PLANS:\n" + "\n".join([f"- {m.get('summary_text', '')}" for m in long_term_memories[:3]])
        
        if short_term_context:
            memory_str += f"\n\nCURRENT CONVERSATION:\n{short_term_context}"
        
        # 2. Reasoning with Secondary LLM
        if not self.client:
            logger.error("Planner Tool: GenAI client not initialized")
            return "I'm having trouble accessing my planning brain right now. Please try again later."
            
        prompt = f"""
        You are the Planner Agent for the Personal Vibe CEO system.
        Your goal is to optimize the user's schedule for PRODUCTIVITY and WELL-BEING.
        
        USER REQUEST: "{user_request}"
        
        MEMORY CONTEXT:
        {memory_str}
        
        SYSTEM DATA:
        {context_str}
        
        INSTRUCTIONS:
        1. Analyze the schedule and health data. Look for conflicts, lack of breaks, or poor sleep.
        2. Consider the MEMORY CONTEXT to understand previous plans or preferences.
        3. Based on the user's request, propose a concrete plan.
        4. If they asked to book/change something, confirm exactly what you would do (simulated).
        5. Keep the response conversational but structured.
        6. Do not output JSON. Output natural language to be spoken back to the user.
        """
        
        logger.info(f"Planner Tool: Sending request to secondary model {self.model_id}")
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            
            plan = response.text
            logger.info("Planner Tool: Generated plan successfully")
            
            # 3. Store Interaction in Memory
            if self.memory_service:
                # Add to Short-Term
                self.memory_service.add_to_short_term(user_id, "user", user_request)
                self.memory_service.add_to_short_term(user_id, "model", plan)
                # Add to Long-Term
                await self.memory_service.summarize_interaction(user_id, "planner", user_request, plan)
            
            return plan
            
        except Exception as e:
            logger.error(f"Error in Planner LLM generation: {e}")
            return "I tried to analyze your schedule, but I encountered an error in my planning process."

# Global instance
_planner_tool = None

def get_planner_tool():
    global _planner_tool
    if _planner_tool is None:
        _planner_tool = PlannerTool()
    return _planner_tool

async def consult_planner_wrapper(user_request: str) -> str:
    """
    Use this tool to handle ANY request related to:
    - Scheduling or checking the calendar (e.g., "what's on my schedule", "book a meeting").
    - Managing tasks or todos (e.g., "add a todo", "what do I need to do").
    - Health or well-being planning (e.g., "plan a workout", "check my sleep").
    - General daily planning or organization.
    
    Args:
        user_request: The full natural language request from the user.
    """
    tool = get_planner_tool()
    # In a real app, we'd get user_id from the session context
    return await tool.consult_planner(user_request)
