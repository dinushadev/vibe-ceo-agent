import asyncio
import os
from src.context import set_current_user_id, get_current_user_id
from src.tools.productivity_tools import collect_todo_item
from src.db.database import Database

async def verify_context():
    print("Verifying Context User ID...")
    
    # Use a temporary DB
    db_path = "/tmp/test_vibe_ceo_context.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    # Initialize DB (needed for tools)
    # We need to patch get_database to return our test db
    # But since get_database uses a global singleton, we can just initialize it first?
    # Actually, get_database in tools imports from src.db.database.
    # Let's just set the env var or rely on the fact that we can initialize it.
    
    # Better approach: Just use the real DB logic but with a test path
    # We need to make sure get_database returns our instance.
    # In src.db.database:
    # _db_instance = None
    # async def get_database(db_path=None):
    #     global _db_instance
    #     if _db_instance is None:
    #         _db_instance = Database(db_path)
    #         await _db_instance.connect()
    #     return _db_instance
    
    # So if we call get_database(test_path) first, it will set the singleton.
    from src.db import database
    
    try:
        # 1. Initialize DB with test path and set singleton
        db = Database(db_path)
        await db.connect()
        await db.initialize_schema()
        
        # Manually set the global singleton so get_database() returns this instance
        database.db_instance = db
        
        print("Database initialized.")
        
        # 2. Set a mock user ID in context
        mock_user_id = "test_user_999"
        set_current_user_id(mock_user_id)
        print(f"Context set to: {get_current_user_id()}")
        
        # 3. Call a tool
        print("Calling collect_todo_item...")
        result = await collect_todo_item(title="Test Task")
        
        # 4. Verify result
        if result["status"] == "success":
            task = result["task"]
            print(f"Task created: {task}")
            
            if task["user_id"] == mock_user_id:
                print("SUCCESS: Task created with correct user_id from context.")
            else:
                print(f"FAIL: Task created with user_id: {task['user_id']}, expected: {mock_user_id}")
        else:
            print(f"FAIL: Tool execution failed: {result}")
            
    except Exception as e:
        print(f"FAIL: Error during verification: {e}")
    finally:
        # Cleanup
        if 'db' in locals():
            await db.close()
        if os.path.exists(db_path):
            os.remove(db_path)

if __name__ == "__main__":
    asyncio.run(verify_context())
