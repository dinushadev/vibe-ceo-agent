import asyncio
import os
from src.db.database import Database

async def verify_schema():
    print("Verifying Database Schema fix...")
    
    # Use a temporary DB for testing migration
    db_path = "/tmp/test_vibe_ceo.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    db = Database(db_path=db_path)
    
    try:
        await db.connect()
        print("Database connected and initialized.")
        
        # Check if column exists
        async with db.connection.execute("PRAGMA table_info(calendar_events)") as cursor:
            columns = await cursor.fetchall()
            column_names = [col["name"] for col in columns]
            
            if "google_event_id" in column_names:
                print("SUCCESS: 'google_event_id' column found in 'calendar_events' table.")
            else:
                print(f"FAIL: 'google_event_id' column NOT found. Columns: {column_names}")
                
    except Exception as e:
        print(f"FAIL: Error verifying schema: {e}")
    finally:
        await db.close()
        if os.path.exists(db_path):
            os.remove(db_path)

if __name__ == "__main__":
    asyncio.run(verify_schema())
