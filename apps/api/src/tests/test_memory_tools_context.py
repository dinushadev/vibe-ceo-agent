import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.tools import memory_tools

class TestMemoryToolsContext(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_db.save_user_fact = AsyncMock(return_value={"status": "success"})
        self.mock_db.get_user_facts = AsyncMock(return_value=[])
        self.mock_db.get_user_preferences = AsyncMock(return_value=[])
        self.mock_db.save_medical_condition = AsyncMock(return_value={"status": "success"})
        self.mock_db.get_user_medical_profile = AsyncMock(return_value=[])
        self.mock_db.save_user_preference = AsyncMock(return_value={"status": "success"})

    @patch("src.tools.memory_tools.get_database")
    @patch("src.tools.memory_tools.get_current_user_id")
    def test_save_user_fact(self, mock_get_user_id, mock_get_db):
        async def run_test():
            mock_get_user_id.return_value = "test_user_123"
            mock_get_db.return_value = self.mock_db

            await memory_tools.save_user_fact(
                category="personal",
                fact_key="hobby",
                fact_value="coding"
            )

            self.mock_db.save_user_fact.assert_called_once()
            call_args = self.mock_db.save_user_fact.call_args[1]
            self.assertEqual(call_args["user_id"], "test_user_123")
            self.assertEqual(call_args["category"], "personal")
            self.assertEqual(call_args["fact_key"], "hobby")
            self.assertEqual(call_args["fact_value"], "coding")

        asyncio.run(run_test())

    @patch("src.tools.memory_tools.get_database")
    @patch("src.tools.memory_tools.get_current_user_id")
    def test_get_user_profile(self, mock_get_user_id, mock_get_db):
        async def run_test():
            mock_get_user_id.return_value = "test_user_123"
            mock_get_db.return_value = self.mock_db

            await memory_tools.get_user_profile()

            self.mock_db.get_user_facts.assert_called_once_with("test_user_123")
            self.mock_db.get_user_preferences.assert_called_once_with("test_user_123")

        asyncio.run(run_test())

    @patch("src.tools.memory_tools.get_database")
    @patch("src.tools.memory_tools.get_current_user_id")
    def test_save_medical_info(self, mock_get_user_id, mock_get_db):
        async def run_test():
            mock_get_user_id.return_value = "test_user_123"
            mock_get_db.return_value = self.mock_db

            await memory_tools.save_medical_info(
                condition_name="flu",
                status="active"
            )

            self.mock_db.save_medical_condition.assert_called_once()
            call_args = self.mock_db.save_medical_condition.call_args[1]
            self.assertEqual(call_args["user_id"], "test_user_123")
            self.assertEqual(call_args["condition_name"], "flu")
            self.assertEqual(call_args["status"], "active")

        asyncio.run(run_test())

    @patch("src.tools.memory_tools.get_database")
    @patch("src.tools.memory_tools.get_current_user_id")
    def test_get_medical_profile(self, mock_get_user_id, mock_get_db):
        async def run_test():
            mock_get_user_id.return_value = "test_user_123"
            mock_get_db.return_value = self.mock_db

            await memory_tools.get_medical_profile()

            self.mock_db.get_user_medical_profile.assert_called_once_with("test_user_123")

        asyncio.run(run_test())

    @patch("src.tools.memory_tools.get_database")
    @patch("src.tools.memory_tools.get_current_user_id")
    def test_save_user_preference(self, mock_get_user_id, mock_get_db):
        async def run_test():
            mock_get_user_id.return_value = "test_user_123"
            mock_get_db.return_value = self.mock_db

            await memory_tools.save_user_preference(
                category="ui",
                pref_key="theme",
                pref_value="dark"
            )

            self.mock_db.save_user_preference.assert_called_once()
            call_args = self.mock_db.save_user_preference.call_args[1]
            self.assertEqual(call_args["user_id"], "test_user_123")
            self.assertEqual(call_args["category"], "ui")
            self.assertEqual(call_args["pref_key"], "theme")
            self.assertEqual(call_args["pref_value"], "dark")

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
