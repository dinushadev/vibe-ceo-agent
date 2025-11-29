import sys
import os
import asyncio

# Add project root to path
# Current file: apps/api/src/verify_path.py
# Root: apps/api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db.database import Database

async def main():
    # Unset env var if set to test default behavior
    if "DATABASE_PATH" in os.environ:
        del os.environ["DATABASE_PATH"]
        
    db = Database()
    print(f"Resolved DB Path: {db.db_path}")
    
    # Check if path is absolute
    if not os.path.isabs(db.db_path):
        print("❌ Path is NOT absolute")
        return

    expected_suffix = "apps/api/data/vibe_ceo.db"
    if db.db_path.endswith(expected_suffix):
        print("✅ Path resolution correct")
    else:
        print(f"❌ Path resolution incorrect. Expected suffix: {expected_suffix}")

if __name__ == "__main__":
    asyncio.run(main())
