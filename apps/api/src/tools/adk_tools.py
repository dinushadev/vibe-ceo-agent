"""
ADK Tool Definitions
Converts mock tools to ADK-compatible format using FunctionTool
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from google.adk.tools import FunctionTool

# Import mock services for business logic
from .mock_tools import get_calendar_service, get_search_service, get_todo_service

logger = logging.getLogger(__name__)

# Initialize services
_calendar_service = None
_search_service = None
_todo_service = None


def _get_calendar():
    """Lazy initialization of calendar service"""
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = get_calendar_service()
    return _calendar_service


def _get_search():
    """Lazy initialization of search service"""
    global _search_service
    if _search_service is None:
        _search_service = get_search_service()
    return _search_service


def _get_todo():
    """Lazy initialization of todo service"""
    global _todo_service
    if _todo_service is None:
        _todo_service = get_todo_service()
    return _todo_service


# ============================================================================
# Calendar Tools
# ============================================================================


def schedule_appointment(
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
        calendar = _get_calendar()
        result = calendar.schedule_appointment(
            title=title,
            date=date,
            time=time,
            duration_minutes=duration_minutes,
            description=description
        )
        logger.info(f"Scheduled appointment: {title} on {date} at {time}")
        return result
    except Exception as e:
        logger.error(f"Failed to schedule appointment: {e}")
        return {"error": str(e), "success": False}



def get_upcoming_appointments(days_ahead: int = 7) -> List[Dict]:
    """
    Retrieve upcoming appointments from the calendar.
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
        
    Returns:
        List of upcoming appointments
    """
    try:
        calendar = _get_calendar()
        appointments = calendar.get_upcoming_appointments(days_ahead)
        logger.info(f"Retrieved {len(appointments)} upcoming appointments")
        return appointments
    except Exception as e:
        logger.error(f"Failed to get appointments: {e}")
        return []



def check_availability(date: str, start_time: str, end_time: str) -> Dict:
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
        calendar = _get_calendar()
        result = calendar.check_availability(date, start_time, end_time)
        logger.info(f"Checked availability for {date} {start_time}-{end_time}: {result['available']}")
        return result
    except Exception as e:
        logger.error(f"Failed to check availability: {e}")
        return {"available": False, "error": str(e)}


# ============================================================================
# Todo/Task Tools
# ============================================================================


def create_task(title: str, priority: str = "medium", due_date: Optional[str] = None) -> Dict:
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
        todo = _get_todo()
        result = todo.add_task(title=title, priority=priority, due_date=due_date)
        logger.info(f"Created task: {title} (priority: {priority})")
        return result
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        return {"error": str(e), "success": False}



def get_pending_tasks(priority: Optional[str] = None) -> List[Dict]:
    """
    Get all pending tasks from the todo list.
    
    Args:
        priority: Optional priority filter: "high", "medium", or "low"
        
    Returns:
        List of pending tasks
    """
    try:
        todo = _get_todo()
        tasks = todo.get_pending_tasks(priority_filter=priority)
        logger.info(f"Retrieved {len(tasks)} pending tasks")
        return tasks
    except Exception as e:
        logger.error(f"Failed to get tasks: {e}")
        return []



def complete_task(task_id: str) -> Dict:
    """
    Mark a task as completed.
    
    Args:
        task_id: The ID of the task to complete
        
    Returns:
        Confirmation of task completion
    """
    try:
        todo = _get_todo()
        result = todo.complete_task(task_id)
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
    get_health_data
]

# All available tools
ALL_TOOLS = PLANNER_TOOLS + KNOWLEDGE_TOOLS + VIBE_TOOLS
