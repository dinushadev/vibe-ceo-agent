"""
Productivity Tools
Tools for the Vibe Agent to manage tasks and calendar events.
"""

import logging
import uuid
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo # Fallback for older python
from typing import Dict, Optional, List
from src.db.database import get_database
from src.context import get_current_user_id

logger = logging.getLogger(__name__)

async def _get_user_timezone(user_id: str) -> str:
    """Get user's timezone from preferences, default to UTC"""
    try:
        db = await get_database()
        pref = await db.get_user_preference(user_id, "general", "timezone")
        if pref:
            return pref["pref_value"]
    except Exception as e:
        logger.warning(f"Failed to fetch timezone for {user_id}: {e}")
    return "UTC"

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
        user_id = get_current_user_id()
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
        user_id = get_current_user_id()
        event_id = str(uuid.uuid4())
        
        # Get user timezone
        user_tz_str = await _get_user_timezone(user_id)
        
        # Parse start time with timezone awareness
        parsed_start_time = _parse_time(start_time, user_tz_str)
        end_time = parsed_start_time + timedelta(minutes=duration_minutes)
        
        # Convert to UTC for storage
        start_utc = parsed_start_time.astimezone(ZoneInfo("UTC"))
        end_utc = end_time.astimezone(ZoneInfo("UTC"))
        
        event = await db.create_event(
            event_id=event_id,
            user_id=user_id,
            title=title,
            start_time=start_utc.isoformat(),
            end_time=end_utc.isoformat(),
            description=description,
            location=location
        )
        
        # Sync to Google Calendar (Synchronous)
        try:
            from src.services.google_calendar_service import GoogleCalendarService
            gcal_service = GoogleCalendarService(user_id)
            
            # Prepare event data for Google Calendar
            gcal_event_data = {
                "title": title,
                "description": description,
                "location": location,
                "start_time": start_utc.isoformat(),
                "end_time": end_utc.isoformat()
            }
            
            gcal_result = await gcal_service.create_event(gcal_event_data)
            
            if gcal_result.get("status") == "success":
                logger.info(f"Synced event to Google Calendar: {gcal_result.get('link')}")
                event["google_link"] = gcal_result.get("link")
            else:
                logger.warning(f"Failed to sync to Google Calendar: {gcal_result.get('message')}")
                # We don't fail the operation, just log the warning
                
        except Exception as e:
            logger.error(f"Error syncing to Google Calendar: {e}")
        
        return {"status": "success", "event": event}
    except Exception as e:
        logger.error(f"Error booking calendar event: {e}")
        return {"status": "error", "message": str(e)}

async def update_calendar_event(
    event_id: str,
    title: Optional[str] = None,
    start_time: Optional[str] = None,
    description: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    location: Optional[str] = None
) -> Dict:
    """
    Update an existing calendar event.
    
    Args:
        event_id: The ID of the event to update.
        title: New title.
        start_time: New start time.
        description: New description.
        duration_minutes: New duration in minutes (requires start_time).
        location: New location.
    """
    try:
        db = await get_database()
        user_id = get_current_user_id()
        
        # Get existing event
        existing_event = await db.get_event(event_id)
        if not existing_event:
            return {"status": "error", "message": "Event not found"}
            
        if existing_event["user_id"] != user_id:
             return {"status": "error", "message": "Unauthorized"}
        
        # Prepare updates
        updates = {}
        if title:
            updates["title"] = title
        if description is not None:
            updates["description"] = description
        if location is not None:
            updates["location"] = location
            
        start_utc = None
        end_utc = None
        
        if start_time:
            # Get user timezone
            user_tz_str = await _get_user_timezone(user_id)
            
            # Parse start time
            parsed_start_time = _parse_time(start_time, user_tz_str)
            
            # Calculate end time
            if duration_minutes:
                end_time = parsed_start_time + timedelta(minutes=duration_minutes)
            else:
                # Keep existing duration
                old_start = datetime.fromisoformat(existing_event["start_time"])
                old_end = datetime.fromisoformat(existing_event["end_time"])
                duration = old_end - old_start
                end_time = parsed_start_time + duration
            
            start_utc = parsed_start_time.astimezone(ZoneInfo("UTC"))
            end_utc = end_time.astimezone(ZoneInfo("UTC"))
            
            updates["start_time"] = start_utc.isoformat()
            updates["end_time"] = end_utc.isoformat()
        
        elif duration_minutes:
             # Update end time only based on existing start
             old_start = datetime.fromisoformat(existing_event["start_time"])
             if old_start.tzinfo is None:
                 old_start = old_start.replace(tzinfo=ZoneInfo("UTC"))
                 
             end_time = old_start + timedelta(minutes=duration_minutes)
             end_utc = end_time.astimezone(ZoneInfo("UTC"))
             updates["end_time"] = end_utc.isoformat()

        # Update local DB
        updated_event = await db.update_event(event_id, **updates)
        
        # Sync to Google Calendar
        if existing_event.get("google_event_id"):
            try:
                from src.services.google_calendar_service import GoogleCalendarService
                gcal_service = GoogleCalendarService(user_id)
                
                gcal_updates = updates.copy()
                # Ensure we send what Google expects if we updated times
                
                gcal_result = await gcal_service.update_event(existing_event["google_event_id"], gcal_updates)
                
                if gcal_result.get("status") == "success":
                    logger.info(f"Synced update to Google Calendar: {gcal_result.get('link')}")
                else:
                    logger.warning(f"Failed to sync update to Google Calendar: {gcal_result.get('message')}")
                    
            except Exception as e:
                logger.error(f"Error syncing update to Google Calendar: {e}")
        
        return {"status": "success", "event": updated_event}
    except Exception as e:
        logger.error(f"Error updating calendar event: {e}")
        return {"status": "error", "message": str(e)}

async def get_upcoming_events(days_ahead: int = 7) -> Dict:
    """
    Get upcoming calendar events.
    
    Args:
        days_ahead: Number of days to look ahead.
    """
    try:
        db = await get_database()
        user_id = get_current_user_id()
        
        # Get user timezone
        user_tz_str = await _get_user_timezone(user_id)
        user_tz = ZoneInfo(user_tz_str)
        
        # Calculate start_after (now in UTC)
        start_after = datetime.now(ZoneInfo("UTC")).isoformat()
        
        events = await db.get_user_events(user_id, start_after=start_after)
        
        # Filter by days_ahead and convert to user timezone for display
        cutoff = datetime.now(ZoneInfo("UTC")) + timedelta(days=days_ahead)
        
        filtered_events = []
        for e in events:
            # Parse stored UTC time
            start_utc = datetime.fromisoformat(e["start_time"])
            # Ensure it has timezone info (if stored without 'Z')
            if start_utc.tzinfo is None:
                start_utc = start_utc.replace(tzinfo=ZoneInfo("UTC"))
                
            if start_utc <= cutoff:
                # Convert to user timezone
                start_local = start_utc.astimezone(user_tz)
                end_local = datetime.fromisoformat(e["end_time"]).replace(tzinfo=ZoneInfo("UTC")).astimezone(user_tz)
                
                # Update event with local times for the user
                e_local = e.copy()
                e_local["start_time"] = start_local.isoformat()
                e_local["end_time"] = end_local.isoformat()
                filtered_events.append(e_local)
        
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
        user_id = get_current_user_id()
        
        # Get user timezone
        user_tz_str = await _get_user_timezone(user_id)
        user_tz = ZoneInfo(user_tz_str)

        # Construct ISO timestamps in user timezone
        try:
            # Parse date and time in user's timezone
            start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M").replace(tzinfo=user_tz)
            end_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M").replace(tzinfo=user_tz)
            
            # Convert to UTC for comparison
            requested_start = start_dt.astimezone(ZoneInfo("UTC"))
            requested_end = end_dt.astimezone(ZoneInfo("UTC"))
            
        except ValueError:
             return {"status": "error", "message": "Invalid date/time format. Use YYYY-MM-DD and HH:MM"}

        # Get events overlapping with this day
        # For simplicity, get all future events and filter
        # In production, DB query should be more specific
        events = await db.get_user_events(user_id)
        
        conflicts = []
        
        for event in events:
            # Parse stored UTC time
            event_start = datetime.fromisoformat(event["start_time"])
            if event_start.tzinfo is None:
                event_start = event_start.replace(tzinfo=ZoneInfo("UTC"))
                
            event_end = datetime.fromisoformat(event["end_time"])
            if event_end.tzinfo is None:
                event_end = event_end.replace(tzinfo=ZoneInfo("UTC"))
            
            # Check overlap
            if (requested_start < event_end) and (requested_end > event_start):
                # Convert conflict to user time for display
                event_local = event.copy()
                event_local["start_time"] = event_start.astimezone(user_tz).isoformat()
                event_local["end_time"] = event_end.astimezone(user_tz).isoformat()
                conflicts.append(event_local)
                
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
        user_id = get_current_user_id()
        
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

def _parse_time(time_str: str, timezone_str: str = "UTC") -> datetime:
    """Helper to parse time strings with timezone awareness"""
    tz = ZoneInfo(timezone_str)
    now = datetime.now(tz)
    time_lower = time_str.lower()
    
    if "next week" in time_lower:
        dt = now + timedelta(days=7)
        return dt.replace(hour=14, minute=0, second=0, microsecond=0)
    elif "tomorrow" in time_lower:
        dt = now + timedelta(days=1)
        return dt.replace(hour=10, minute=0, second=0, microsecond=0)
    elif "next month" in time_lower:
        dt = now + timedelta(days=30)
        return dt.replace(hour=14, minute=0, second=0, microsecond=0)
    else:
        try:
            # Try ISO format first
            dt = datetime.fromisoformat(time_str)
            # If naive, assume user timezone
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz)
            return dt
        except:
            # Fallback
            dt = now + timedelta(days=1)
            return dt.replace(hour=14, minute=0, second=0, microsecond=0)
