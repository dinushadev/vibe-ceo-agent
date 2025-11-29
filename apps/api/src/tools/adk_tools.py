"""
ADK Tool Definitions
Converts tools to ADK-compatible format using FunctionTool
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from google.adk.tools import FunctionTool

# Import productivity tools (DB-backed)
from .productivity_tools import (
    book_calendar_event,
    get_upcoming_events as get_events_impl,
    check_availability as check_avail_impl,
    collect_todo_item,
    get_pending_tasks as get_tasks_impl,
    complete_task as complete_task_impl
)

from .memory_tools import (
    save_user_fact,
    get_user_profile,
    save_medical_info,
    get_medical_profile,
    save_user_preference
)

# Import mock search for now (until we have a real one)
from .mock_tools import get_search_service

logger = logging.getLogger(__name__)

# Initialize services
_search_service = None

def _get_search():
    """Lazy initialization of search service"""
    global _search_service
    if _search_service is None:
        _search_service = get_search_service()
    return _search_service


# ============================================================================
# Calendar Tools
# ============================================================================


async def schedule_appointment(
    title: str,
    date: str,
    time: str,
    duration_minutes: int = 60,
    description: str = ""
) -> Dict:
    """
    Schedule a new appointment in the calendar.
    
    Args:
        title: Appointment title/name
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format (24-hour)
        duration_minutes: Duration in minutes (default: 60)
        description: Optional appointment description
        
    Returns:
        Confirmation with appointment ID and details
    """
    try:
        # Combine date and time for book_calendar_event
        start_time = f"{date}T{time}:00"
        
        result = await book_calendar_event(
            title=title,
            start_time=start_time,
            description=description,
            duration_minutes=duration_minutes
        )
        logger.info(f"Scheduled appointment: {title} on {date} at {time}")
        return result
    except Exception as e:
        logger.error(f"Failed to schedule appointment: {e}")
        return {"error": str(e), "success": False}



async def get_upcoming_appointments(days_ahead: int = 7) -> List[Dict]:
    """
    Retrieve upcoming appointments from the calendar.
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
        
    Returns:
        List of upcoming appointments
    """
    try:
        result = await get_events_impl(days_ahead=days_ahead)
        if result.get("status") == "success":
            return result.get("events", [])
        return []
    except Exception as e:
        logger.error(f"Failed to get appointments: {e}")
        return []



async def check_availability(date: str, start_time: str, end_time: str) -> Dict:
    """
    Check if a time slot is available in the calendar.
    
    Args:
        date: Date in YYYY-MM-DD format
        start_time: Start time in HH:MM format
        end_time: End time in HH:MM format
        
    Returns:
        Availability status and conflicting appointments if any
    """
    try:
        result = await check_avail_impl(date, start_time, end_time)
        return result
    except Exception as e:
        logger.error(f"Failed to check availability: {e}")
        return {"available": False, "error": str(e)}


# ============================================================================
# Todo/Task Tools
# ============================================================================


async def create_task(title: str, priority: str = "medium", due_date: Optional[str] = None) -> Dict:
    """
    Create a new task in the todo list.
    
    Args:
        title: Task title/description
        priority: Priority level: "high", "medium", or "low" (default: "medium")
        due_date: Optional due date in YYYY-MM-DD format
        
    Returns:
        Created task details with task ID
    """
    try:
        result = await collect_todo_item(
            title=title,
            priority=priority,
            due_date=due_date
        )
        logger.info(f"Created task: {title} (priority: {priority})")
        return result
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        return {"error": str(e), "success": False}



async def get_pending_tasks(priority: Optional[str] = None) -> List[Dict]:
    """
    Get all pending tasks from the todo list.
    
    Args:
        priority: Optional priority filter: "high", "medium", or "low"
        
    Returns:
        List of pending tasks
    """
    try:
        result = await get_tasks_impl(priority=priority)
        if result.get("status") == "success":
            return result.get("tasks", [])
        return []
    except Exception as e:
        logger.error(f"Failed to get tasks: {e}")
        return []



async def complete_task(task_id: str) -> Dict:
    """
    Mark a task as completed.
    
    Args:
        task_id: The ID of the task to complete
        
    Returns:
        Confirmation of task completion
    """
    try:
        result = await complete_task_impl(task_id)
        logger.info(f"Completed task: {task_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to complete task: {e}")
        return {"error": str(e), "success": False}


# ============================================================================
# Search/Knowledge Tools
# ============================================================================


def search_learning_content(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search for learning content and articles on a topic.
    
    Args:
        query: Search query or topic
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        List of articles/content with titles, URLs, and summaries
    """
    try:
        search = _get_search()
        results = search.search(query=query, max_results=max_results)
        logger.info(f"Found {len(results)} learning resources for: {query}")
        return results
    except Exception as e:
        logger.error(f"Failed to search content: {e}")
        return []


# ============================================================================
# Health Data Tools (for Vibe Agent)
# ============================================================================


async def get_health_data(user_id: str, days: int = 7) -> List[Dict]:
    """
    Retrieve user's health and wellness data from the database.
    
    Args:
        user_id: User identifier
        days: Number of days of history to retrieve (default: 7)
        
    Returns:
        List of health logs with sleep, screen time, and imbalance scores
    """
    try:
        # Import here to avoid circular dependencies
        from ..db.database import get_database
        
        db = await get_database()
        health_logs = await db.get_user_health_logs(user_id, limit=days)
        logger.info(f"Retrieved {len(health_logs)} health logs for user {user_id}")
        return health_logs
    except Exception as e:
        logger.error(f"Failed to get health data: {e}")
        return []


# ============================================================================
# Tool Collections
# ============================================================================

# Tools for Planner Agent
PLANNER_TOOLS = [
    schedule_appointment,
    get_upcoming_appointments,
    check_availability,
    create_task,
    get_pending_tasks,
    complete_task
]

# Tools for Knowledge Agent
KNOWLEDGE_TOOLS = [
    search_learning_content
]

# Tools for Vibe Agent
VIBE_TOOLS = [
    get_health_data,
    save_user_fact,
    get_user_profile,
    save_medical_info,
    get_medical_profile,
    save_user_preference
]

# All available tools
ALL_TOOLS = PLANNER_TOOLS + KNOWLEDGE_TOOLS + VIBE_TOOLS
