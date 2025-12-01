import logging
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from src.db.database import get_database

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.service = None

    async def authenticate(self):
        """Authenticate using stored credentials"""
        db = await get_database()
        integration = await db.get_integration(self.user_id, "google_calendar")
        
        if not integration:
            logger.warning(f"No Google Calendar integration found for user {self.user_id}")
            return False

        try:
            creds_data = json.loads(integration["credentials_json"])
            credentials = Credentials.from_authorized_user_info(creds_data)
            
            # Re-save if refreshed (not fully implemented here without a refresh flow loop, 
            # but google library handles refresh if we provide client config)
            # For now, we assume credentials are valid or auto-refreshed by the library if we had the request object
            
            self.service = build('calendar', 'v3', credentials=credentials)
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate Google Calendar: {e}")
            return False

    async def create_event(self, event_data: dict):
        """Create an event in Google Calendar"""
        if not self.service:
            success = await self.authenticate()
            if not success:
                return {"status": "error", "message": "Not authenticated with Google Calendar"}

        try:
            # Map our event data to Google Calendar format
            # event_data comes from our DB model or tool input
            # Expected keys: title, description, start_time (ISO), end_time (ISO), location
            
            gcal_event = {
                'summary': event_data.get('title'),
                'description': event_data.get('description', ''),
                'location': event_data.get('location', ''),
                'start': {
                    'dateTime': event_data.get('start_time'),
                    'timeZone': 'UTC', # We store in UTC, let Google handle display
                },
                'end': {
                    'dateTime': event_data.get('end_time'),
                    'timeZone': 'UTC',
                },
            }

            event = self.service.events().insert(calendarId='primary', body=gcal_event).execute()
            logger.info(f"Created Google Calendar event: {event.get('htmlLink')}")
            return {"status": "success", "google_event_id": event.get('id'), "link": event.get('htmlLink')}
            
        except Exception as e:
            logger.error(f"Failed to create Google Calendar event: {e}")
            return {"status": "error", "message": str(e)}

    async def update_event(self, google_event_id: str, event_data: dict):
        """Update an event in Google Calendar"""
        if not self.service:
            success = await self.authenticate()
            if not success:
                return {"status": "error", "message": "Not authenticated with Google Calendar"}

        try:
            # First get the existing event to preserve other fields
            event = self.service.events().get(calendarId='primary', eventId=google_event_id).execute()
            
            # Update fields
            if 'title' in event_data:
                event['summary'] = event_data['title']
            if 'description' in event_data:
                event['description'] = event_data['description']
            if 'location' in event_data:
                event['location'] = event_data['location']
            if 'start_time' in event_data:
                event['start'] = {
                    'dateTime': event_data['start_time'],
                    'timeZone': 'UTC',
                }
            if 'end_time' in event_data:
                event['end'] = {
                    'dateTime': event_data['end_time'],
                    'timeZone': 'UTC',
                }

            updated_event = self.service.events().update(
                calendarId='primary', 
                eventId=google_event_id, 
                body=event
            ).execute()
            
            logger.info(f"Updated Google Calendar event: {updated_event.get('htmlLink')}")
            return {"status": "success", "link": updated_event.get('htmlLink')}
            
        except Exception as e:
            logger.error(f"Failed to update Google Calendar event: {e}")
            return {"status": "error", "message": str(e)}
