import asyncio
import logging
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.vibe_agent import VibeAgent
from src.db.database import get_database
from src.context import set_current_user_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_delegation():
    user_id = "user_123"
    set_current_user_id(user_id)
    
    db = await get_database()
    await db.connect()
    
    # Initialize Vibe Agent
    vibe_agent = VibeAgent(db)
    
    # Mock the ADK agent to avoid real API calls and just check tool selection logic if possible
    # But since we want to test the actual prompt/tool config, we might need to let it run if we have creds.
    # Assuming we might not have full ADK runtime here, we can check the tools list.
    
    from src.tools.adk_tools import VIBE_TOOLS
    
    # Verify tools list
    tool_names = [t.__name__ for t in VIBE_TOOLS]
    logger.info(f"Vibe Agent Tools: {tool_names}")
    
    if "consult_planner_wrapper" in tool_names:
        logger.info("SUCCESS: consult_planner_wrapper is in VIBE_TOOLS")
    else:
        logger.error("FAILURE: consult_planner_wrapper is NOT in VIBE_TOOLS")
        
    if "schedule_appointment" in tool_names:
        logger.error("FAILURE: schedule_appointment is incorrectly in VIBE_TOOLS")
    else:
        logger.info("SUCCESS: schedule_appointment is correctly absent from VIBE_TOOLS")

    await db.close()

if __name__ == "__main__":
    asyncio.run(verify_delegation())
