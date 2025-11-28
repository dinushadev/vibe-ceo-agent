import asyncio
import logging
import os
from apps.api.src.db.database import get_database
from apps.api.src.tools.memory_tools import (
    save_user_fact,
    get_user_profile,
    save_medical_info,
    save_user_preference
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_memory_system():
    logger.info("Starting Memory System Verification...")
    
    # Initialize DB
    db = await get_database()
    await db.initialize_schema()
    
    user_id = "test_user_123"
    
    # 1. Test User Facts
    logger.info("Testing User Facts...")
    await save_user_fact(user_id, "family", "spouse_name", "Sarah")
    await save_user_fact(user_id, "work", "job_title", "Software Engineer")
    
    profile = await get_user_profile(user_id)
    facts = profile["facts"]
    logger.info(f"Retrieved facts: {facts}")
    
    assert any(f["fact_key"] == "spouse_name" and f["fact_value"] == "Sarah" for f in facts)
    assert any(f["fact_key"] == "job_title" and f["fact_value"] == "Software Engineer" for f in facts)
    logger.info("User Facts Verified ✅")
    
    # 2. Test Medical Info
    logger.info("Testing Medical Info...")
    await save_medical_info(
        user_id, 
        "Asthma", 
        "active", 
        "Mild symptoms in winter", 
        ["Albuterol"]
    )
    
    # Verify via DB directly or tool
    med_profile = await db.get_user_medical_profile(user_id)
    logger.info(f"Retrieved medical profile: {med_profile}")
    
    assert len(med_profile) > 0
    assert med_profile[0]["condition_name"] == "Asthma"
    assert "Albuterol" in med_profile[0]["medications"]
    logger.info("Medical Info Verified ✅")
    
    # 3. Test Preferences
    logger.info("Testing Preferences...")
    await save_user_preference(user_id, "communication", "style", "concise")
    
    profile = await get_user_profile(user_id)
    prefs = profile["preferences"]
    logger.info(f"Retrieved preferences: {prefs}")
    
    assert any(p["pref_key"] == "style" and p["pref_value"] == "concise" for p in prefs)
    logger.info("Preferences Verified ✅")
    
    logger.info("All Memory Systems Verified Successfully! 🎉")

if __name__ == "__main__":
    # Set DB path to a test file
    os.environ["DATABASE_PATH"] = "./test_memory.db"
    asyncio.run(test_memory_system())
