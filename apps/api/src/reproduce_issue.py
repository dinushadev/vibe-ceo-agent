import asyncio
import logging
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools.planner_tool import consult_planner_wrapper
from src.db.database import get_database
from src.context import set_current_user_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reproduce():
    user_id = "user_123"
    set_current_user_id(user_id)
    
    db = await get_database()
    await db.connect()
    
    # Simulate the user request
    request = "Schedule 'learning ML tuning' for tomorrow from 9 AM to 11 AM"
    
    logger.info(f"Simulating request: {request}")
    
    response = await consult_planner_wrapper(request)
    
    logger.info(f"Planner Response: {response}")
    
    # Check if event was created
    events = await db.get_user_events(user_id)
    found = False
    for event in events:
        if "learning ML tuning" in event["title"]:
            logger.info(f"SUCCESS: Event found in DB: {event}")
            found = True
            break
            
    if not found:
        logger.error("FAILURE: Event NOT found in DB")
        
    await db.close()

if __name__ == "__main__":
    asyncio.run(reproduce())
