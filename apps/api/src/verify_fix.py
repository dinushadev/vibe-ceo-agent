import asyncio
from unittest.mock import MagicMock
from src.agents.knowledge_agent import KnowledgeAgent

async def verify_fix():
    print("Verifying KnowledgeAgent fix...")
    
    # Mock DB
    mock_db = MagicMock()
    mock_db.get_agent_memories.return_value = []
    mock_db.get_user_context.return_value = "User context"
    
    # Instantiate Agent
    try:
        agent = KnowledgeAgent(db=mock_db)
        print("KnowledgeAgent initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize KnowledgeAgent: {e}")
        return

    # Check for methods
    if not hasattr(agent, '_get_memories'):
        print("FAIL: _get_memories method missing.")
        return
    if not hasattr(agent, '_get_personal_context'):
        print("FAIL: _get_personal_context method missing.")
        return
    if not hasattr(agent, '_store_interaction'):
        print("FAIL: _store_interaction method missing.")
        return

    print("All missing methods are present.")
    
    # Test method call (mocking memory service behavior)
    # We need to mock the memory_service attribute which is set in BaseAgent.__init__
    # Since we passed a mock DB, get_memory_service might have been called.
    # Let's mock the memory_service on the agent instance directly to be sure.
    mock_memory_service = MagicMock()
    
    async def mock_get_memories(*args, **kwargs):
        return [{"summary_text": "Test memory"}]
    
    async def mock_get_context(*args, **kwargs):
        return "Test Context"
        
    async def mock_summarize(*args, **kwargs):
        return "Summary"

    mock_memory_service.get_agent_memories.side_effect = mock_get_memories
    mock_memory_service.get_user_context.side_effect = mock_get_context
    mock_memory_service.summarize_interaction.side_effect = mock_summarize
    
    agent.memory_service = mock_memory_service
    
    try:
        memories = await agent._get_memories("user123")
        print(f"Method _get_memories called successfully. Result: {memories}")
        
        context = await agent._get_personal_context("user123")
        print(f"Method _get_personal_context called successfully. Result: {context}")
        
        await agent._store_interaction("user123", "hi", "hello")
        print("Method _store_interaction called successfully.")
        
        print("\nSUCCESS: Verification passed!")
        
    except Exception as e:
        print(f"\nFAIL: Method execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_fix())
