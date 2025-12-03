import asyncio
import logging
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
# Add apps/api to path for src imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from unittest.mock import MagicMock, AsyncMock
import sys

# Mock VectorStore to avoid google dependency
mock_vector_store = MagicMock()
sys.modules["apps.api.src.memory.vector_store"] = mock_vector_store
sys.modules["src.memory.vector_store"] = mock_vector_store

# Mock Database to avoid aiosqlite dependency
mock_db_module = MagicMock()
async def mock_get_db_func():
    return MagicMock()
mock_db_module.get_database.side_effect = mock_get_db_func

sys.modules["apps.api.src.db.database"] = mock_db_module
sys.modules["src.db.database"] = mock_db_module
sys.modules["aiosqlite"] = MagicMock()

print(f"DEBUG: sys.path: {sys.path}")

from src.memory.memory_service import SessionMemory, ADKMemoryService
from src.tools.memory_tools import search_memory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_memory_optimization():
    print("--- Verifying Memory Optimization ---")
    
    # 1. Verify Session Summarization
    print("\n[Check 1] Session Summarization")
    session = SessionMemory(max_turns=4) # Small limit for testing
    user_id = "test_user"
    
    # Add messages
    messages = ["Hello", "How are you?", "I'm good", "What's up?", "Not much", "Cool"]
    for i, msg in enumerate(messages):
        session.add_message(user_id, "user" if i % 2 == 0 else "agent", msg)
        
    history = session.get_history(user_id)
    summary = session.get_summary(user_id)
    
    print(f"History length: {len(history)}")
    print(f"Summary: {summary}")
    
    if len(history) <= 4 and summary:
        print("✅ Session summarization working (history truncated, summary created).")
    else:
        print("❌ Session summarization failed.")

    # 2. Verify Reactive Memory Tool
    print("\n[Check 2] Reactive Memory Tool (search_memory)")
    
    # Mock dependencies
    with patch('src.tools.memory_tools.get_database') as mock_get_db, \
         patch('src.tools.memory_tools.get_memory_service') as mock_get_service, \
         patch('src.tools.memory_tools.get_current_user_id') as mock_get_user:
        
        mock_user_id = "user_123"
        mock_get_user.return_value = mock_user_id
        
        mock_service = MagicMock()
        async def mock_get_memories(*args, **kwargs):
            return [
                {"summary_text": "User likes blue", "created_at": "2023-01-01"},
                {"summary_text": "User has a dog", "created_at": "2023-01-02"}
            ]
        mock_service.get_agent_memories = mock_get_memories
        mock_get_service.return_value = mock_service
        
        # Call tool
        results = await search_memory("What do I like?")
        
        if len(results) == 2 and results[0]['summary'] == "User likes blue":
            print("✅ Reactive memory tool working.")
        else:
            print("❌ Reactive memory tool failed.")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(verify_memory_optimization())
