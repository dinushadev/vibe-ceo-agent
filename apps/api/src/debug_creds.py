import asyncio
import logging
import json
from src.db.database import get_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_creds():
    user_id = "user_123"
    db = await get_database()
    await db.connect()
    
    integration = await db.get_integration(user_id, "google_calendar")
    if integration:
        creds_json = integration["credentials_json"]
        creds = json.loads(creds_json)
        logger.info(f"Stored Credentials Keys: {list(creds.keys())}")
        logger.info(f"Has Refresh Token: {'refresh_token' in creds and bool(creds['refresh_token'])}")
        logger.info(f"Has Client ID: {'client_id' in creds and bool(creds['client_id'])}")
        logger.info(f"Has Client Secret: {'client_secret' in creds and bool(creds['client_secret'])}")
        logger.info(f"Has Token URI: {'token_uri' in creds and bool(creds['token_uri'])}")
    else:
        logger.info("No integration found.")
        
    await db.close()

if __name__ == "__main__":
    asyncio.run(check_creds())
