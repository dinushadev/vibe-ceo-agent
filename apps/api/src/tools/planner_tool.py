"""
Planner Tool (Agent-as-a-Tool)
Delegates planning and scheduling requests to the PlannerAgent.
"""

import logging
from typing import Dict, Any, Optional

from src.db.database import get_database
from src.agents.planner_agent import PlannerAgent

logger = logging.getLogger(__name__)

# Global instance
_planner_agent = None

async def get_planner_agent():
    global _planner_agent
    if _planner_agent is None:
        db = await get_database()
        _planner_agent = PlannerAgent(db)
    return _planner_agent

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
    logger.info(f"Consulting Planner Agent with request: {user_request}")
    
    try:
        agent = await get_planner_agent()
        # Use a fixed user_id for now, consistent with other parts of the system
        user_id = "user_123"
        
        response = await agent.process_message(user_id, user_request)
        
        # Extract the text response from the agent's result
        response_text = response.get("response", "I couldn't generate a plan.")
        
        logger.info("Planner Agent consulted successfully")
        return response_text
        
    except Exception as e:
        logger.error(f"Error consulting Planner Agent: {e}", exc_info=True)
        return "I encountered an error while trying to consult the planner."
