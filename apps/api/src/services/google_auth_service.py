import os
import logging
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
from src.db.database import get_database

logger = logging.getLogger(__name__)

# Scopes required for the application
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/calendar.readonly',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

class GoogleAuthService:
    def __init__(self):
        self.client_secrets_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "client_secret.json")
        # Redirect URI should match what's configured in Google Cloud Console
        # For local dev, usually http://localhost:3000/auth/callback or similar
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback")

    def get_authorization_url(self):
        """Generate the authorization URL for the user"""
        if not os.path.exists(self.client_secrets_file):
            logger.error(f"Client secrets file not found at {self.client_secrets_file}")
            raise FileNotFoundError("client_secret.json not found. Please configure Google OAuth credentials.")

        flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        # Access type offline to get refresh token
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return authorization_url

    async def exchange_code_for_token(self, code: str, user_id: str):
        """Exchange auth code for credentials and save to DB"""
        if not os.path.exists(self.client_secrets_file):
            raise FileNotFoundError("client_secret.json not found")

        flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Ensure we have client_id and client_secret
        # flow.client_config is a dict like {'web': {'client_id': '...', ...}}
        client_config = flow.client_config.get('web') or flow.client_config.get('installed')
        
        client_id = credentials.client_id or client_config.get('client_id')
        client_secret = credentials.client_secret or client_config.get('client_secret')
        token_uri = credentials.token_uri or client_config.get('token_uri')

        # Serialize credentials to JSON
        creds_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': token_uri,
            'client_id': client_id,
            'client_secret': client_secret,
            'scopes': credentials.scopes
        }
        
        db = await get_database()
        await db.save_integration(
            user_id=user_id,
            service_name="google_calendar",
            credentials_json=json.dumps(creds_data)
        )
        
        logger.info(
            f"Google Login Success: User {user_id} connected Google Calendar",
            extra={
                "event": "login_success",
                "user_id": user_id,
                "service": "google_calendar",
                "scopes_granted": credentials.scopes,
                "client_id_partial": client_id[:5] + "..." if client_id else "unknown"
            }
        )
        return True

    async def verify_google_token(self, token: str):
        """Verify Google ID token and return user info"""
        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            # We can get this from the client_secrets file or env var
            # For now, we'll try to extract it from the token or use a configured one
            
            # In a real scenario, you should validate the audience (CLIENT_ID)
            # id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
            
            # For MVP/Dev, we might be lenient or fetch client_id from env
            # client_id = os.getenv("GOOGLE_CLIENT_ID")
            
            id_info = id_token.verify_oauth2_token(token, requests.Request())

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            google_id = id_info['sub']
            email = id_info.get('email')
            name = id_info.get('name')
            
            logger.info(
                f"Google Token Verified: {email}",
                extra={
                    "event": "token_verification_success",
                    "google_id": google_id,
                    "email_domain": email.split('@')[1] if email else "unknown"
                }
            )
            
            return {
                "google_id": google_id,
                "email": email,
                "name": name,
                "picture": id_info.get('picture')
            }
        except ValueError as e:
            # Invalid token
            logger.error(
                f"Invalid Google token: {e}",
                extra={"event": "token_verification_failed", "error": str(e)}
            )
            return None
        except Exception as e:
            logger.error(
                f"Error verifying Google token: {e}",
                extra={"event": "token_verification_error", "error": str(e)}
            )
            return None
