"""
Productivity Tools
Tools for the Vibe Agent to manage tasks and calendar events.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from src.db.database import get_database

logger = logging.getLogger(__name__)

async def collect_todo_item(
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[str] = None
) -> Dict:
    """
    Collect a new todo item or task from the user.
    
    Args:
        title: The main title or action of the task (e.g., "Buy milk", "Email John").
        description: Additional details about the task.
        priority: Priority level ("low", "medium", "high").
        due_date: Due date for the task (e.g., "2023-12-31", "tomorrow").
    """
    try:
        db = await get_database()
        user_id = "user_123" # Default for MVP
        task_id = str(uuid.uuid4())
        
        task = await db.create_task(
            task_id=task_id,
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        return {"status": "success", "task": task}
    except Exception as e:
        logger.error(f"Error collecting todo item: {e}")
        return {"status": "error", "message": str(e)}

async def book_calendar_event(
    title: str,
    start_time: str,
    description: str = "",
    duration_minutes: int = 60,
    location: Optional[str] = None
) -> Dict:
    """
    Book a new event or meeting on the user's calendar.
    
    Args:
        title: Title of the event (e.g., "Meeting with Sarah", "Dentist Appointment").
        start_time: Start time of the event. Can be specific ISO format or relative (e.g., "tomorrow at 2pm").
        description: Description or agenda for the event.
        duration_minutes: Duration of the event in minutes.
        location: Location of the event.
    """
    try:
        db = await get_database()
        user_id = "user_123" # Default for MVP
        event_id = str(uuid.uuid4())
        
        # Simple parsing for relative time if needed, but ideally LLM passes ISO
        # For now, we assume the LLM or a helper handles parsing, or we pass as is if valid
        # If start_time is "tomorrow at 2pm", we might need a parser.
        # Let's add a basic parser similar to the mock one for robustness
        parsed_start_time = _parse_time(start_time)
        end_time = parsed_start_time + timedelta(minutes=duration_minutes)
        
        event = await db.create_event(
            event_id=event_id,
            user_id=user_id,
            title=title,
            start_time=parsed_start_time.isoformat(),
            end_time=end_time.isoformat(),
            description=description,
            location=location
        )
        return {"status": "success", "event": event}
    except Exception as e:
        logger.error(f"Error booking calendar event: {e}")
        return {"status": "error", "message": str(e)}

async def get_upcoming_events(days_ahead: int = 7) -> Dict:
    """
    Get upcoming calendar events.
    
    Args:
        days_ahead: Number of days to look ahead.
    """
    try:
        db = await get_database()
        user_id = "user_123"
        
        # Calculate start_after (now)
        start_after = datetime.utcnow().isoformat()
        
        events = await db.get_user_events(user_id, start_after=start_after)
        
        # Filter by days_ahead (simple in-memory filter for now as DB query is open-ended)
        cutoff = datetime.utcnow() + timedelta(days=days_ahead)
        filtered_events = [
            e for e in events 
            if datetime.fromisoformat(e["start_time"]) <= cutoff
        ]
        
        return {"status": "success", "events": filtered_events}
    except Exception as e:
        logger.error(f"Error getting upcoming events: {e}")
        return {"status": "error", "message": str(e)}

async def check_availability(date: str, start_time: str, end_time: str) -> Dict:
    """
    Check if a time slot is available.
    
    Args:
        date: YYYY-MM-DD
        start_time: HH:MM
        end_time: HH:MM
    """
    try:
        db = await get_database()
        user_id = "user_123"
        
        # Construct ISO timestamps
        try:
            start_iso = f"{date}T{start_time}:00"
            end_iso = f"{date}T{end_time}:00"
            # Validate format
            datetime.fromisoformat(start_iso)
            datetime.fromisoformat(end_iso)
        except ValueError:
             return {"status": "error", "message": "Invalid date/time format. Use YYYY-MM-DD and HH:MM"}

        # Get events overlapping with this day
        # For simplicity, get all future events and filter
        # In production, DB query should be more specific
        events = await db.get_user_events(user_id)
        
        conflicts = []
        requested_start = datetime.fromisoformat(start_iso)
        requested_end = datetime.fromisoformat(end_iso)
        
        for event in events:
            event_start = datetime.fromisoformat(event["start_time"])
            event_end = datetime.fromisoformat(event["end_time"])
            
            # Check overlap
            if (requested_start < event_end) and (requested_end > event_start):
                conflicts.append(event)
                
        if conflicts:
            return {"status": "conflict", "available": False, "conflicts": conflicts}
        
        return {"status": "success", "available": True}
        
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        return {"status": "error", "message": str(e)}

async def get_pending_tasks(priority: Optional[str] = None) -> Dict:
    """
    Get pending tasks.
    
    Args:
        priority: Optional priority filter.
    """
    try:
        db = await get_database()
        user_id = "user_123"
        
        tasks = await db.get_user_tasks(user_id, status="pending")
        
        if priority:
            tasks = [t for t in tasks if t["priority"] == priority]
            
        return {"status": "success", "tasks": tasks}
    except Exception as e:
        logger.error(f"Error getting pending tasks: {e}")
        return {"status": "error", "message": str(e)}

async def complete_task(task_id: str) -> Dict:
    """
    Mark a task as complete.
    
    Args:
        task_id: The ID of the task.
    """
    try:
        db = await get_database()
        
        task = await db.update_task_status(task_id, status="completed")
        
        if task:
            return {"status": "success", "task": task}
        else:
            return {"status": "error", "message": "Task not found"}
            
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return {"status": "error", "message": str(e)}

def _parse_time(time_str: str) -> datetime:
    """Helper to parse time strings (basic implementation)"""
    now = datetime.now()
    time_lower = time_str.lower()
    
    if "next week" in time_lower:
        return now + timedelta(days=7, hours=14)
    elif "tomorrow" in time_lower:
        return now + timedelta(days=1, hours=10)
    elif "next month" in time_lower:
        return now + timedelta(days=30, hours=14)
    else:
        try:
            return datetime.fromisoformat(time_str)
        except:
            # Fallback
            return now + timedelta(days=1, hours=14)
