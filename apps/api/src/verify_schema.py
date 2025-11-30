
import asyncio
import os
import sys
import aiosqlite

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.db.database import Database

async def verify_schema():
    print("Verifying Database Schema...")
    
    db = Database()
    await db.connect()
    
    tables_to_check = {
        "users": ["created_at", "updated_at"],
        "health_logs": ["timestamp"],
        "memory_contexts": ["timestamp"],
        "tool_action_logs": ["timestamp"],
        "user_facts": ["created_at", "updated_at"],
        "medical_profile": ["created_at", "updated_at"],
        "user_preferences": ["created_at", "updated_at"],
        "todos": ["due_date", "created_at", "completed_at", "updated_at"],
        "calendar_events": ["start_time", "end_time", "created_at", "updated_at"]
    }
    
    all_passed = True
    
    async with db.connection.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
        tables = await cursor.fetchall()
        table_names = [t[0] for t in tables]
        print(f"Found tables: {table_names}")
        
    for table, columns in tables_to_check.items():
        print(f"\nChecking table: {table}")
        async with db.connection.execute(f"PRAGMA table_info({table})") as cursor:
            info = await cursor.fetchall()
            # info row: (cid, name, type, notnull, dflt_value, pk)
            col_map = {row[1]: row[2] for row in info}
            
            for col in columns:
                col_type = col_map.get(col)
                if col_type == "TIMESTAMP":
                    print(f"  [PASS] {col}: {col_type}")
                else:
                    print(f"  [FAIL] {col}: Expected TIMESTAMP, got {col_type}")
                    all_passed = False
                    
    await db.close()
    
    if all_passed:
        print("\nSUCCESS: All checked columns are TIMESTAMP.")
    else:
        print("\nFAILURE: Some columns have incorrect types.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify_schema())
