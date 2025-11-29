import asyncio
import logging
from src.tools.adk_tools import (
    schedule_appointment,
    get_upcoming_appointments,
    check_availability,
    create_task,
    get_pending_tasks,
    complete_task
)
from src.db.database import get_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_text_tools():
    logger.info("Starting verification of text interface tools...")
    
    # 1. Verify Task Tools
    logger.info("Testing Task Tools...")
    
    # Create Task
    task_result = await create_task(
        title="Text Interface Test Task",
        priority="high",
        due_date="2023-12-31"
    )
    if task_result.get("status") == "success":
        task_id = task_result["task"]["task_id"]
        logger.info(f"✅ create_task success. Task ID: {task_id}")
        
        # Get Pending Tasks
        pending = await get_pending_tasks(priority="high")
        found = any(t["task_id"] == task_id for t in pending)
        if found:
            logger.info(f"✅ get_pending_tasks success. Found task {task_id}")
        else:
            logger.error(f"❌ get_pending_tasks failed. Task {task_id} not found")
            
        # Complete Task
        complete_result = await complete_task(task_id)
        if complete_result.get("status") == "success":
             logger.info(f"✅ complete_task success. Task {task_id} completed")
        else:
             logger.error(f"❌ complete_task failed: {complete_result}")
             
    else:
        logger.error(f"❌ create_task failed: {task_result}")

    # 2. Verify Calendar Tools
    logger.info("Testing Calendar Tools...")
    
    # Schedule Appointment
    appt_result = await schedule_appointment(
        title="Text Interface Test Meeting",
        date="2023-12-25",
        time="10:00",
        duration_minutes=30
    )
    
    if appt_result.get("status") == "success":
        event_id = appt_result["event"]["event_id"]
        logger.info(f"✅ schedule_appointment success. Event ID: {event_id}")
        
        # Check Availability
        avail_result = await check_availability("2023-12-25", "10:00", "10:30")
        if avail_result.get("status") == "conflict":
             logger.info("✅ check_availability success. Correctly identified conflict.")
        else:
             logger.error(f"❌ check_availability failed. Expected conflict, got: {avail_result}")
             
        # Get Upcoming Appointments
        # Note: get_upcoming_appointments looks ahead from NOW. 
        # Since we booked for 2023 (past) or future depending on current date, this might vary.
        # Let's book one for tomorrow to be safe.
        
        import datetime
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow_str = tomorrow.isoformat()
        
        appt_result_2 = await schedule_appointment(
            title="Future Test Meeting",
            date=tomorrow_str,
            time="14:00"
        )
        
        if appt_result_2.get("status") == "success":
            upcoming = await get_upcoming_appointments(days_ahead=7)
            found_future = any(e["title"] == "Future Test Meeting" for e in upcoming)
            if found_future:
                 logger.info("✅ get_upcoming_appointments success. Found future event.")
            else:
                 logger.error("❌ get_upcoming_appointments failed. Event not found.")
        
    else:
        logger.error(f"❌ schedule_appointment failed: {appt_result}")

if __name__ == "__main__":
    asyncio.run(verify_text_tools())
