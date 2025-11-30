
import asyncio
import os
import sys
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.db.database import Database
from src.tools.productivity_tools import _parse_time, book_calendar_event, get_upcoming_events

async def test_timezone_handling():
    print("Testing Timezone Handling...")
    
    # 1. Test _parse_time
    print("\n1. Testing _parse_time helper:")
    utc_now = datetime.now(ZoneInfo("UTC"))
    ny_tz = "America/New_York"
    
    # "Tomorrow at 10am" in NY
    parsed_ny = _parse_time("tomorrow at 10am", ny_tz)
    print(f"  'tomorrow at 10am' in NY: {parsed_ny} (tz={parsed_ny.tzinfo})")
    
    assert parsed_ny.tzinfo is not None, "Should be timezone aware"
    assert str(parsed_ny.tzinfo) == ny_tz or "New_York" in str(parsed_ny.tzinfo), f"Should be NY timezone, got {parsed_ny.tzinfo}"
    assert parsed_ny.hour == 10, f"Should be 10am, got {parsed_ny.hour}"
    
    # 2. Test DB Integration (Mocking DB context)
    print("\n2. Testing DB Integration (requires running DB):")
    db_path = "/tmp/test_vibe_ceo.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    db = Database(db_path)
    await db.connect()
    
    # Set user timezone
    user_id = "user_123"
    await db.create_user(user_id, "Test User")
    await db.save_user_preference("pref_1", user_id, "general", "timezone", "America/New_York")
    
    # We need to monkeypatch get_database to return our test db
    import src.tools.productivity_tools
    
    async def mock_get_db():
        return db
        
    src.tools.productivity_tools.get_database = mock_get_db
    
    # Book event: "2025-12-01 10:00" (NY time)
    # NY is UTC-5 in winter (Dec). So 10am NY = 3pm UTC (15:00)
    print("  Booking event for 2025-12-01 10:00 NY...")
    result = await book_calendar_event(
        title="Test Meeting",
        start_time="2025-12-01T10:00:00", # Treated as NY time by our tool logic
        duration_minutes=60
    )
    
    if result.get("status") == "error":
        print(f"  Error booking event: {result.get('message')}")
        return

    event = result["event"]
    print(f"  Event created: {event['start_time']} (Stored UTC)")
    
    # Verify stored UTC time
    # 2025-12-01 10:00 NY is 15:00 UTC
    assert "15:00" in event["start_time"], f"Expected 15:00 UTC, got {event['start_time']}"
    
    # Get upcoming events (should convert back to NY)
    print("  Fetching upcoming events (should convert back to NY)...")
    # We need to fake "now" to be before the event
    # But get_upcoming_events uses datetime.now(UTC), so we can't easily fake it without more mocking.
    # Instead, let's just check if the conversion logic works by calling the function.
    # Note: get_upcoming_events filters by "now", so if 2025 is far future, it works.
    
    events_result = await get_upcoming_events(days_ahead=3650) # 10 years ahead
    events = events_result["events"]
    
    found = False
    for e in events:
        if e["event_id"] == event["event_id"]:
            print(f"  Retrieved event start: {e['start_time']}")
            # Should be 10:00 in the string (isoformat with offset or just local time string depending on implementation)
            # Our implementation returns isoformat of the converted time.
            # 15:00 UTC converted to NY is 10:00.
            assert "10:00" in e["start_time"], f"Expected 10:00 in retrieved time, got {e['start_time']}"
            # Check offset if present (e.g. -05:00)
            assert "-05:00" in e["start_time"], f"Expected -05:00 offset, got {e['start_time']}"
            found = True
            break
            
    assert found, "Event not found in upcoming events"
    
    print("\nSUCCESS: Timezone handling verified!")
    await db.close()

if __name__ == "__main__":
    asyncio.run(test_timezone_handling())
