import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.tools import productivity_tools

class TestCalendarSync(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_db.get_event = AsyncMock()
        self.mock_db.update_event = AsyncMock()
        self.mock_db.get_user_preference = AsyncMock(return_value={"pref_value": "UTC"})
        
        self.mock_gcal_service = MagicMock()
        self.mock_gcal_service.update_event = AsyncMock(return_value={"status": "success", "link": "http://google.com/event"})

    @patch("src.tools.productivity_tools.get_database")
    @patch("src.tools.productivity_tools.get_current_user_id")
    @patch("src.services.google_calendar_service.GoogleCalendarService")
    def test_update_calendar_event_sync(self, mock_gcal_cls, mock_get_user_id, mock_get_db):
        async def run_test():
            user_id = "test_user_123"
            event_id = "event_123"
            google_event_id = "g_event_123"
            
            mock_get_user_id.return_value = user_id
            mock_get_db.return_value = self.mock_db
            
            # Mock existing event
            self.mock_db.get_event.return_value = {
                "event_id": event_id,
                "user_id": user_id,
                "title": "Old Title",
                "start_time": "2023-12-01T10:00:00+00:00",
                "end_time": "2023-12-01T11:00:00+00:00",
                "google_event_id": google_event_id
            }
            
            # Mock Google Service instance
            mock_gcal_cls.return_value = self.mock_gcal_service
            
            # Call update tool
            result = await productivity_tools.update_calendar_event(
                event_id=event_id,
                title="New Title",
                location="New Location"
            )
            
            # Verify DB update
            self.mock_db.update_event.assert_called_once()
            call_args = self.mock_db.update_event.call_args
            self.assertEqual(call_args[0][0], event_id)
            self.assertEqual(call_args[1]["title"], "New Title")
            self.assertEqual(call_args[1]["location"], "New Location")
            
            # Verify Google Sync
            self.mock_gcal_service.update_event.assert_called_once()
            gcal_args = self.mock_gcal_service.update_event.call_args
            self.assertEqual(gcal_args[0][0], google_event_id)
            self.assertEqual(gcal_args[0][1]["title"], "New Title")
            self.assertEqual(gcal_args[0][1]["location"], "New Location")
            
            self.assertEqual(result["status"], "success")

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
