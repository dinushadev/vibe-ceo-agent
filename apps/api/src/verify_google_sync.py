import asyncio
import logging
import os
from src.db.database import get_database
from src.services.google_calendar_service import GoogleCalendarService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_and_sync_events():
    """
    Verify all local events are synced to Google Calendar.
    If not, sync them and update the local DB.
    """
    user_id = os.getenv("TEST_USER_ID", "user_123") # Default user for local testing
    
    logger.info("Starting Google Calendar Sync Verification...")
    
    db = await get_database()
    await db.connect()
    
    # Check if user is connected
    integration = await db.get_integration(user_id, "google_calendar")
    if not integration:
        logger.error("User is NOT connected to Google Calendar. Please connect via Settings first.")
        await db.close()
        return

    logger.info("User is connected to Google Calendar.")
    
    # Get all future events
    events = await db.get_user_events(user_id)
    logger.info(f"Found {len(events)} local events.")
    
    gcal_service = GoogleCalendarService(user_id)
    synced_count = 0
    failed_count = 0
    skipped_count = 0
    
    for event in events:
        event_id = event["event_id"]
        title = event["title"]
        google_id = event.get("google_event_id")
        
        if google_id:
            logger.info(f"Event '{title}' is already synced (ID: {google_id}). Skipping.")
            skipped_count += 1
            continue
            
        logger.info(f"Event '{title}' is NOT synced. Syncing now...")
        
        # Prepare event data
        gcal_event_data = {
            "title": title,
            "description": event.get("description", ""),
            "location": event.get("location", ""),
            "start_time": event["start_time"],
            "end_time": event["end_time"]
        }
        
        result = await gcal_service.create_event(gcal_event_data)
        
        if result.get("status") == "success":
            new_google_id = result.get("google_event_id")
            link = result.get("link")
            
            # Update local DB
            await db.update_event_google_id(event_id, new_google_id)
            logger.info(f"Successfully synced '{title}'. Link: {link}")
            synced_count += 1
        else:
            logger.error(f"Failed to sync '{title}': {result.get('message')}")
            failed_count += 1
            
    logger.info("="*50)
    logger.info(f"Verification Complete.")
    logger.info(f"Total Events: {len(events)}")
    logger.info(f"Already Synced: {skipped_count}")
    logger.info(f"Newly Synced: {synced_count}")
    logger.info(f"Failed: {failed_count}")
    logger.info("="*50)
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(verify_and_sync_events())
