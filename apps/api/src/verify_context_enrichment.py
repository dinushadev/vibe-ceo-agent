import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db.database import Database
from src.memory.memory_service import ADKMemoryService
from src.agents.vibe_agent import VibeAgent
from src.agents.planner_agent import PlannerAgent
from src.agents.knowledge_agent import KnowledgeAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting Context Enrichment Verification...")
    
    # 1. Setup Test Data
    db = Database()
    await db.connect()
    
    user_id = "test_user_context"
    
    # Clean up previous test data
    # (In a real test we'd have a clean DB, but here we just overwrite)
    
    # Create User
    await db.create_user(user_id, "Test User", ["AI", "Health"])
    
    # Add Facts
    await db.save_user_fact("fact1", user_id, "personal", "nickname", "VibeTester")
    await db.save_user_fact("fact2", user_id, "work", "role", "CEO")
    
    # Add Preferences
    await db.save_user_preference("pref1", user_id, "communication", "style", "concise")
    
    # Add Medical Info
    await db.save_medical_condition("cond1", user_id, "Allergy", "Active", "Peanuts", ["EpiPen"])
    
    # Add Task
    await db.create_task("task1", user_id, "Review Q3 Reports", priority="high", due_date="2024-01-01")
    
    # Add Event
    tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
    await db.create_event("event1", user_id, "Board Meeting", tomorrow, tomorrow)
    
    logger.info("✅ Test data created")
    
    # 2. Verify Memory Service Context
    memory_service = ADKMemoryService(db)
    context = await memory_service.get_user_context(user_id)
    
    logger.info(f"\n--- Generated Context ---\n{context}\n-------------------------")
    
    if "VibeTester" in context and "CEO" in context:
        logger.info("✅ User Facts present")
    else:
        logger.error("❌ User Facts missing")
        
    if "concise" in context:
        logger.info("✅ User Preferences present")
    else:
        logger.error("❌ User Preferences missing")
        
    if "Peanuts" in context:
        logger.info("✅ Medical Info present")
    else:
        logger.error("❌ Medical Info missing")
        
    if "Review Q3 Reports" in context:
        logger.info("✅ Pending Tasks present")
    else:
        logger.error("❌ Pending Tasks missing")
        
    if "Board Meeting" in context:
        logger.info("✅ Upcoming Events present")
    else:
        logger.error("❌ Upcoming Events missing")
        
    # 3. Verify Agent Prompts (Mocking internal methods to inspect prompt)
    
    # Vibe Agent
    vibe_agent = VibeAgent(db)
    vibe_prompt = vibe_agent._build_context_prompt("Hello", [], user_id, personal_context=context)
    if "VibeTester" in vibe_prompt and "Peanuts" in vibe_prompt:
        logger.info("✅ Vibe Agent prompt enriched")
    else:
        logger.error("❌ Vibe Agent prompt missing context")
        
    # Planner Agent
    planner_agent = PlannerAgent(db)
    planner_prompt = planner_agent._build_context_prompt("Schedule meeting", [], user_id, personal_context=context)
    if "Review Q3 Reports" in planner_prompt:
        logger.info("✅ Planner Agent prompt enriched")
    else:
        logger.error("❌ Planner Agent prompt missing context")
        
    # Knowledge Agent
    knowledge_agent = KnowledgeAgent(db)
    knowledge_prompt = knowledge_agent._build_context_prompt("Learn about AI", [], user_id, personal_context=context)
    if "concise" in knowledge_prompt:
        logger.info("✅ Knowledge Agent prompt enriched")
    else:
        logger.error("❌ Knowledge Agent prompt missing context")

    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
