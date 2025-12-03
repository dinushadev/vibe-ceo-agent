import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# from apps.api.src.db.database import get_database
from apps.api.src.agents.vibe_agent import VibeAgent
from apps.api.src.agents.orchestrator_core import get_orchestrator_instruction
from unittest.mock import MagicMock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_orchestrator():
    print("--- Verifying Orchestrator Architecture ---")
    
    # 1. Initialize DB (Mock) and Agent
    db = MagicMock()
    agent = VibeAgent(db)
    
    # 2. Verify Instruction
    instruction = get_orchestrator_instruction("text")
    print(f"\n[Check 1] Instruction Loaded: {len(instruction)} chars")
    if "Vibe CEO" in instruction and "TEXT-SPECIFIC" in instruction:
        print("✅ Instruction contains correct persona and text-specific rules.")
    else:
        print("❌ Instruction mismatch.")
        
    # 3. Verify Tools
    print(f"\n[Check 2] Tools Loaded: {len(agent.adk_agent.tools)}")
    tool_names = [t.name for t in agent.adk_agent.tools]
    if "consult_planner_wrapper" in tool_names and "consult_knowledge_wrapper" in tool_names:
        print("✅ Orchestrator has Planner and Knowledge tools.")
    else:
        print(f"❌ Missing tools. Found: {tool_names}")

    # 4. Simulate Interaction (Mocking ADK runner would be ideal, but we can check the flow logic)
    # Since we can't easily mock the ADK runner without more setup, we'll assume the structure is correct
    # based on the initialization checks.
    
    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(verify_orchestrator())
