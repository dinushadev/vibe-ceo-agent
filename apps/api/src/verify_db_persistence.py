import asyncio
import logging
import os
from src.tools.productivity_tools import collect_todo_item, book_calendar_event
from src.db.database import get_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_db_persistence():
    logger.info("Starting verification of database persistence...")
    
    # Ensure DB path is set for testing if needed, or rely on default
    # os.environ["DATABASE_PATH"] = "./data/vibe_ceo_test.db"

    # 1. Verify collect_todo_item
    logger.info("Testing collect_todo_item (DB)...")
    todo_result = await collect_todo_item(
        title="DB Persistence Test Task",
        description="Testing SQLite storage",
        priority="high",
        due_date="tomorrow"
    )
    
    if todo_result["status"] == "success":
        task_id = todo_result["task"]["task_id"]
        logger.info(f"✅ collect_todo_item success. Task ID: {task_id}")
        
        # Verify in DB directly
        db = await get_database()
        saved_task = await db.get_task(task_id)
        if saved_task and saved_task["title"] == "DB Persistence Test Task":
             logger.info("✅ Verified task exists in SQLite DB")
        else:
             logger.error("❌ Task not found in SQLite DB")
    else:
        logger.error(f"❌ collect_todo_item failed: {todo_result}")

    # 2. Verify book_calendar_event
    logger.info("Testing book_calendar_event (DB)...")
    calendar_result = await book_calendar_event(
        title="DB Persistence Test Event",
        start_time="tomorrow at 3pm",
        description="Testing SQLite storage for events",
        duration_minutes=45
    )

    if calendar_result["status"] == "success":
        event_id = calendar_result["event"]["event_id"]
        logger.info(f"✅ book_calendar_event success. Event ID: {event_id}")
        
        # Verify in DB directly
        db = await get_database()
        saved_event = await db.get_event(event_id)
        if saved_event and saved_event["title"] == "DB Persistence Test Event":
             logger.info("✅ Verified event exists in SQLite DB")
        else:
             logger.error("❌ Event not found in SQLite DB")
    else:
        logger.error(f"❌ book_calendar_event failed: {calendar_result}")

if __name__ == "__main__":
    asyncio.run(verify_db_persistence())
