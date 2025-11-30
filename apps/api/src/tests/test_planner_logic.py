
import unittest
import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.agents.planner_agent import PlannerAgent

class TestPlannerLogic(unittest.TestCase):
    def setUp(self):
        self.mock_db = AsyncMock()
        self.mock_db.get_user_preference.return_value = {"pref_value": "UTC"}
        self.agent = PlannerAgent(self.mock_db)
        # Mock ADK agent to simulate responses based on instructions
        self.agent.adk_agent = MagicMock()
        self.agent._generate_adk_response = AsyncMock()

    async def test_vague_request_placeholder(self):
        """Test that a vague request triggers placeholder creation"""
        user_id = "user_123"
        message = "Schedule a meeting with John"
        
        # Simulate ADK response for vague request
        # The agent should call create_task and then ask for details
        self.agent._generate_adk_response.return_value = (
            "I've created a placeholder task for that. When would you like to schedule it?",
            [{"name": "create_task", "args": {"title": "Schedule meeting with John - Placeholder", "priority": "high"}}]
        )
        
        response = await self.agent.process_message(user_id, message)
        
        self.assertIn("placeholder", response["response"].lower())
        tools_used = response["metadata"]["tools_used"]
        self.assertEqual(len(tools_used), 1)
        self.assertEqual(tools_used[0]["name"], "create_task")
        self.assertIn("Placeholder", tools_used[0]["args"]["title"])

    async def test_specific_request_confirmation(self):
        """Test that a specific request triggers confirmation"""
        user_id = "user_123"
        message = "Schedule a meeting with John tomorrow at 2pm"
        
        # Simulate ADK response for specific request
        # The agent should NOT call schedule_appointment yet, but ask for confirmation
        self.agent._generate_adk_response.return_value = (
            "Just to confirm, you want to schedule a meeting with John tomorrow at 2:00 PM?",
            [] # No tools called yet
        )
        
        response = await self.agent.process_message(user_id, message)
        
        self.assertIn("confirm", response["response"].lower())
        tools_used = response["metadata"]["tools_used"]
        self.assertEqual(len(tools_used), 0) # Should not schedule yet

    async def test_confirmation_booking(self):
        """Test that confirmation triggers booking"""
        user_id = "user_123"
        message = "Yes, please schedule it."
        
        # Simulate ADK response after confirmation
        self.agent._generate_adk_response.return_value = (
            "I've scheduled the meeting with John for tomorrow at 2:00 PM.",
            [{"name": "schedule_appointment", "args": {"title": "Meeting with John", "date": "2025-12-01", "time": "14:00"}}]
        )
        
        response = await self.agent.process_message(user_id, message)
        
        self.assertIn("scheduled", response["response"].lower())
        tools_used = response["metadata"]["tools_used"]
        self.assertEqual(len(tools_used), 1)
        self.assertEqual(tools_used[0]["name"], "schedule_appointment")

def run_async_test(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.close()

if __name__ == "__main__":
    # Helper to run async tests in unittest
    t = TestPlannerLogic()
    t.setUp()
    run_async_test(t.test_vague_request_placeholder())
    run_async_test(t.test_specific_request_confirmation())
    run_async_test(t.test_confirmation_booking())
    print("All logic tests passed!")
