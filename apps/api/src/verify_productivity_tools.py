import asyncio
import logging
from src.tools.productivity_tools import collect_todo_item, book_calendar_event
from src.tools.mock_tools import get_todo_service, get_calendar_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_tools():
    logger.info("Starting verification of productivity tools...")

    # 1. Verify collect_todo_item
    logger.info("Testing collect_todo_item...")
    todo_result = await collect_todo_item(
        title="Buy groceries",
        description="Milk, eggs, bread",
        priority="high",
        due_date="tomorrow"
    )
    
    if todo_result["status"] == "success":
        logger.info(f"✅ collect_todo_item success: {todo_result['task']}")
    else:
        logger.error(f"❌ collect_todo_item failed: {todo_result}")

    # Verify it's in the mock service
    todo_service = get_todo_service()
    tasks = await todo_service.get_tasks()
    if any(t["title"] == "Buy groceries" for t in tasks):
        logger.info("✅ Verified task exists in MockTodoService")
    else:
        logger.error("❌ Task not found in MockTodoService")

    # 2. Verify book_calendar_event
    logger.info("Testing book_calendar_event...")
    calendar_result = await book_calendar_event(
        title="Team Sync",
        start_time="tomorrow at 10am",
        description="Weekly sync",
        duration_minutes=30
    )

    if calendar_result["status"] == "success":
        logger.info(f"✅ book_calendar_event success: {calendar_result['event']}")
    else:
        logger.error(f"❌ book_calendar_event failed: {calendar_result}")

    # Verify it's in the mock service
    calendar_service = get_calendar_service()
    events = await calendar_service.get_upcoming_events()
    if any(e["title"] == "Team Sync" for e in events):
        logger.info("✅ Verified event exists in MockCalendarService")
    else:
        logger.error("❌ Event not found in MockCalendarService")

if __name__ == "__main__":
    asyncio.run(verify_tools())
