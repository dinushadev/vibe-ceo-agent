import asyncio
import logging
from src.agents.prompts import (
    VIBE_AGENT_INSTRUCTION,
    PLANNER_AGENT_INSTRUCTION,
    KNOWLEDGE_AGENT_INSTRUCTION,
    VOICE_SYSTEM_INSTRUCTION
)
from src.agents.context_utils import get_context_string, build_context_prompt
from src.db.database import get_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_prompts():
    logger.info("Verifying prompts...")
    assert VIBE_AGENT_INSTRUCTION, "Vibe instruction missing"
    assert PLANNER_AGENT_INSTRUCTION, "Planner instruction missing"
    assert KNOWLEDGE_AGENT_INSTRUCTION, "Knowledge instruction missing"
    assert VOICE_SYSTEM_INSTRUCTION, "Voice instruction missing"
    logger.info("Prompts verified.")

async def verify_context_utils():
    logger.info("Verifying context utils...")
    db = await get_database()
    user_id = "test_user_refactor"
    
    # Test get_context_string
    context = await get_context_string(
        user_id=user_id,
        db=db,
        memories=[{"summary_text": "User likes coding"}],
        personal_context="User is a developer",
        short_term_context="User: Hello\nAgent: Hi",
        include_time=True
    )
    
    logger.info(f"Context string:\n{context}")
    
    assert "User ID: test_user_refactor" in context
    assert "User is a developer" in context
    assert "User likes coding" in context
    assert "User: Hello" in context
    assert "Current User Time" in context or "Current UTC Time" in context
    
    # Test build_context_prompt
    prompt = await build_context_prompt(
        message="How are you?",
        user_id=user_id,
        db=db,
        personal_context="User is happy"
    )
    
    logger.info(f"Context prompt:\n{prompt}")
    assert "User message: How are you?" in prompt
    assert "User is happy" in prompt
    
    logger.info("Context utils verified.")

async def main():
    await verify_prompts()
    await verify_context_utils()
    logger.info("ALL CHECKS PASSED")

if __name__ == "__main__":
    asyncio.run(main())
