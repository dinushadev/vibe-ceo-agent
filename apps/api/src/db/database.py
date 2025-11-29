"""
Database models and initialization for the Personal Vibe CEO System
"""

import sqlite3
import aiosqlite
import logging
from datetime import datetime
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)


class Database:
    """Database manager for SQLite"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        if db_path is None:
            # Resolve absolute path to ensure persistence across restarts
            # Current file: apps/api/src/db/database.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # API root: apps/api
            api_root = os.path.dirname(os.path.dirname(current_dir))
            data_dir = os.path.join(api_root, "data")
            
            # Ensure data directory exists
            os.makedirs(data_dir, exist_ok=True)
            
            default_path = os.path.join(data_dir, "vibe_ceo.db")
            db_path = os.getenv("DATABASE_PATH", default_path)
        
        self.db_path = db_path
        self.connection = None
        logger.info(f"Initialized database at {self.db_path}")
    
    async def connect(self):
        """Establish async database connection"""
        # Ensure the directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")
        
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self.initialize_schema()
        logger.info("Database connected and schema initialized")
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")
    
    async def initialize_schema(self):
        """Create database tables if they don't exist"""
        schema = """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            learning_interests TEXT,  -- JSON array as string
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        
        -- Health logs table
        CREATE TABLE IF NOT EXISTS health_logs (
            log_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            sleep_hours REAL NOT NULL,
            screen_time REAL NOT NULL,
            imbalance_score REAL NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        
        -- Memory contexts table for long-term agent memory
        CREATE TABLE IF NOT EXISTS memory_contexts (
            context_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            data_source_id TEXT,
            summary_text TEXT NOT NULL,
            embedding_vector TEXT,  -- JSON array as string
            timestamp TEXT NOT NULL,
            metadata TEXT,  -- JSON object as string
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        
        -- Tool action logs for observability
        CREATE TABLE IF NOT EXISTS tool_action_logs (
            log_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            input_query TEXT NOT NULL,
            output_result TEXT NOT NULL,
            success INTEGER NOT NULL,  -- 0 or 1 (boolean)
            execution_time_ms INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        
        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_health_logs_user_timestamp 
            ON health_logs(user_id, timestamp);
        
        CREATE INDEX IF NOT EXISTS idx_memory_contexts_user_agent 
            ON memory_contexts(user_id, agent_id);
        
        CREATE INDEX IF NOT EXISTS idx_tool_logs_user_timestamp 
            ON tool_action_logs(user_id, timestamp);

        -- User Facts table
        CREATE TABLE IF NOT EXISTS user_facts (
            fact_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            category TEXT NOT NULL,
            fact_key TEXT NOT NULL,
            fact_value TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        -- Medical Profile table
        CREATE TABLE IF NOT EXISTS medical_profile (
            condition_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            condition_name TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            medications TEXT,  -- JSON array
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        -- User Preferences table
        CREATE TABLE IF NOT EXISTS user_preferences (
            pref_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            category TEXT NOT NULL,
            pref_key TEXT NOT NULL,
            pref_value TEXT NOT NULL, -- JSON value
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        -- Indexes for new tables
        CREATE INDEX IF NOT EXISTS idx_user_facts_user_category 
            ON user_facts(user_id, category);
            
        CREATE INDEX IF NOT EXISTS idx_medical_profile_user 
            ON medical_profile(user_id);
            
        CREATE INDEX IF NOT EXISTS idx_user_preferences_user_category 
            ON user_preferences(user_id, category);

        -- Todos table
        CREATE TABLE IF NOT EXISTS todos (
            task_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'medium',
            due_date TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            completed_at TEXT,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        -- Calendar Events table
        CREATE TABLE IF NOT EXISTS calendar_events (
            event_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            location TEXT,
            status TEXT DEFAULT 'scheduled',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        -- Indexes for productivity tables
        CREATE INDEX IF NOT EXISTS idx_todos_user_status 
            ON todos(user_id, status);
            
        CREATE INDEX IF NOT EXISTS idx_calendar_events_user_time 
            ON calendar_events(user_id, start_time);
        """
        
        await self.connection.executescript(schema)
        await self.connection.commit()
        logger.info("Database schema initialized")
    
    # ========================================================================
    # User operations
    # ========================================================================
    
    async def create_user(
        self,
        user_id: str,
        name: str,
        learning_interests: List[str] = None
    ) -> Dict:
        """Create a new user"""
        import json
        
        now = datetime.utcnow().isoformat()
        interests_json = json.dumps(learning_interests or [])
        
        await self.connection.execute(
            """
            INSERT INTO users (user_id, name, learning_interests, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, name, interests_json, now, now)
        )
        await self.connection.commit()
        
        return await self.get_user(user_id)
    
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        import json
        
        async with self.connection.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "user_id": row["user_id"],
                    "name": row["name"],
                    "learning_interests": json.loads(row["learning_interests"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
        return None
    
    async def update_user(
        self,
        user_id: str,
        name: str = None,
        learning_interests: List[str] = None
    ) -> Dict:
        """Update user information"""
        import json
        
        updates = []
        params = []
        
        if name:
            updates.append("name = ?")
            params.append(name)
        
        if learning_interests is not None:
            updates.append("learning_interests = ?")
            params.append(json.dumps(learning_interests))
        
        updates.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        
        params.append(user_id)
        
        await self.connection.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?",
            params
        )
        await self.connection.commit()
        
        return await self.get_user(user_id)
    
    # ========================================================================
    # Health log operations
    # ========================================================================
    
    async def create_health_log(
        self,
        log_id: str,
        user_id: str,
        sleep_hours: float,
        screen_time: float,
        imbalance_score: float,
        notes: str = None
    ) -> Dict:
        """Create a health log entry"""
        timestamp = datetime.utcnow().isoformat()
        
        await self.connection.execute(
            """
            INSERT INTO health_logs 
            (log_id, user_id, timestamp, sleep_hours, screen_time, imbalance_score, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (log_id, user_id, timestamp, sleep_hours, screen_time, imbalance_score, notes)
        )
        await self.connection.commit()
        
        return await self.get_health_log(log_id)
    
    async def get_health_log(self, log_id: str) -> Optional[Dict]:
        """Get health log by ID"""
        async with self.connection.execute(
            "SELECT * FROM health_logs WHERE log_id = ?",
            (log_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
        return None
    
    async def get_user_health_logs(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get recent health logs for a user"""
        async with self.connection.execute(
            """
            SELECT * FROM health_logs 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """,
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # ========================================================================
    # Memory context operations
    # ========================================================================
    
    async def create_memory_context(
        self,
        context_id: str,
        user_id: str,
        agent_id: str,
        summary_text: str,
        data_source_id: str = None,
        embedding_vector: List[float] = None,
        metadata: Dict = None
    ) -> Dict:
        """Create a memory context entry"""
        import json
        
        timestamp = datetime.utcnow().isoformat()
        embedding_json = json.dumps(embedding_vector) if embedding_vector else None
        metadata_json = json.dumps(metadata) if metadata else None
        
        await self.connection.execute(
            """
            INSERT INTO memory_contexts 
            (context_id, user_id, agent_id, data_source_id, summary_text, 
             embedding_vector, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (context_id, user_id, agent_id, data_source_id, summary_text,
             embedding_json, timestamp, metadata_json)
        )
        await self.connection.commit()
        
        return await self.get_memory_context(context_id)
    
    async def get_memory_context(self, context_id: str) -> Optional[Dict]:
        """Get memory context by ID"""
        import json
        
        async with self.connection.execute(
            "SELECT * FROM memory_contexts WHERE context_id = ?",
            (context_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "context_id": row["context_id"],
                    "user_id": row["user_id"],
                    "agent_id": row["agent_id"],
                    "data_source_id": row["data_source_id"],
                    "summary_text": row["summary_text"],
                    "embedding_vector": json.loads(row["embedding_vector"]) if row["embedding_vector"] else None,
                    "timestamp": row["timestamp"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else None
                }
        return None
    
    async def get_agent_memories(
        self,
        user_id: str,
        agent_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """Get recent memory contexts for a specific agent and user"""
        import json
        
        async with self.connection.execute(
            """
            SELECT * FROM memory_contexts 
            WHERE user_id = ? AND agent_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """,
            (user_id, agent_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "context_id": row["context_id"],
                    "user_id": row["user_id"],
                    "agent_id": row["agent_id"],
                    "data_source_id": row["data_source_id"],
                    "summary_text": row["summary_text"],
                    "embedding_vector": json.loads(row["embedding_vector"]) if row["embedding_vector"] else None,
                    "timestamp": row["timestamp"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else None
                }
                for row in rows
            ]
    
    # ========================================================================
    # Tool action log operations
    # ========================================================================
    
    async def log_tool_action(
        self,
        log_id: str,
        user_id: str,
        tool_name: str,
        input_query: str,
        output_result: str,
        success: bool,
        execution_time_ms: int
    ) -> Dict:
        """Log a tool action for observability"""
        timestamp = datetime.utcnow().isoformat()
        
        await self.connection.execute(
            """
            INSERT INTO tool_action_logs 
            (log_id, user_id, tool_name, timestamp, input_query, 
             output_result, success, execution_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (log_id, user_id, tool_name, timestamp, input_query,
             output_result, int(success), execution_time_ms)
        )
        await self.connection.commit()
        
        return await self.get_tool_log(log_id)
    
    async def get_tool_log(self, log_id: str) -> Optional[Dict]:
        """Get tool log by ID"""
        async with self.connection.execute(
            "SELECT * FROM tool_action_logs WHERE log_id = ?",
            (log_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                result = dict(row)
                result["success"] = bool(result["success"])
                return result
        return None
    
    async def get_user_tool_logs(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict]:
        """Get recent tool logs for a user"""
        async with self.connection.execute(
            """
            SELECT * FROM tool_action_logs 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """,
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            results = [dict(row) for row in rows]
            for result in results:
                result["success"] = bool(result["success"])
            return results
    
    # ========================================================================
    # User Facts operations
    # ========================================================================

    async def save_user_fact(
        self,
        fact_id: str,
        user_id: str,
        category: str,
        fact_key: str,
        fact_value: str
    ) -> Dict:
        """Save or update a user fact"""
        now = datetime.utcnow().isoformat()
        
        # Check if exists to preserve created_at or just use UPSERT logic
        # For simplicity using INSERT OR REPLACE but we want to track created_at vs updated_at
        
        async with self.connection.execute(
            "SELECT created_at FROM user_facts WHERE user_id = ? AND category = ? AND fact_key = ?",
            (user_id, category, fact_key)
        ) as cursor:
            row = await cursor.fetchone()
            created_at = row["created_at"] if row else now

        await self.connection.execute(
            """
            INSERT OR REPLACE INTO user_facts 
            (fact_id, user_id, category, fact_key, fact_value, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (fact_id, user_id, category, fact_key, fact_value, created_at, now)
        )
        await self.connection.commit()
        
        return await self.get_user_fact(user_id, category, fact_key)

    async def get_user_fact(self, user_id: str, category: str, fact_key: str) -> Optional[Dict]:
        """Get a specific user fact"""
        async with self.connection.execute(
            "SELECT * FROM user_facts WHERE user_id = ? AND category = ? AND fact_key = ?",
            (user_id, category, fact_key)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_user_facts(self, user_id: str, category: str = None) -> List[Dict]:
        """Get all facts for a user, optionally filtered by category"""
        query = "SELECT * FROM user_facts WHERE user_id = ?"
        params = [user_id]
        
        if category:
            query += " AND category = ?"
            params.append(category)
            
        async with self.connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ========================================================================
    # Medical Profile operations
    # ========================================================================

    async def save_medical_condition(
        self,
        condition_id: str,
        user_id: str,
        condition_name: str,
        status: str,
        notes: str = None,
        medications: List[str] = None
    ) -> Dict:
        """Save or update a medical condition"""
        import json
        now = datetime.utcnow().isoformat()
        meds_json = json.dumps(medications or [])
        
        async with self.connection.execute(
            "SELECT created_at FROM medical_profile WHERE condition_id = ?",
            (condition_id,)
        ) as cursor:
            row = await cursor.fetchone()
            created_at = row["created_at"] if row else now

        await self.connection.execute(
            """
            INSERT OR REPLACE INTO medical_profile 
            (condition_id, user_id, condition_name, status, notes, medications, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (condition_id, user_id, condition_name, status, notes, meds_json, created_at, now)
        )
        await self.connection.commit()
        
        return await self.get_medical_condition(condition_id)

    async def get_medical_condition(self, condition_id: str) -> Optional[Dict]:
        """Get a specific medical condition"""
        import json
        async with self.connection.execute(
            "SELECT * FROM medical_profile WHERE condition_id = ?",
            (condition_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                res = dict(row)
                res["medications"] = json.loads(res["medications"])
                return res
            return None

    async def get_user_medical_profile(self, user_id: str) -> List[Dict]:
        """Get all medical conditions for a user"""
        import json
        async with self.connection.execute(
            "SELECT * FROM medical_profile WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            results = []
            for row in rows:
                res = dict(row)
                res["medications"] = json.loads(res["medications"])
                results.append(res)
            return results

    # ========================================================================
    # User Preferences operations
    # ========================================================================

    async def save_user_preference(
        self,
        pref_id: str,
        user_id: str,
        category: str,
        pref_key: str,
        pref_value: str
    ) -> Dict:
        """Save or update a user preference"""
        now = datetime.utcnow().isoformat()
        
        async with self.connection.execute(
            "SELECT created_at FROM user_preferences WHERE user_id = ? AND category = ? AND pref_key = ?",
            (user_id, category, pref_key)
        ) as cursor:
            row = await cursor.fetchone()
            created_at = row["created_at"] if row else now

        await self.connection.execute(
            """
            INSERT OR REPLACE INTO user_preferences 
            (pref_id, user_id, category, pref_key, pref_value, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (pref_id, user_id, category, pref_key, pref_value, created_at, now)
        )
        await self.connection.commit()
        
        return await self.get_user_preference(user_id, category, pref_key)

    async def get_user_preference(self, user_id: str, category: str, pref_key: str) -> Optional[Dict]:
        """Get a specific user preference"""
        async with self.connection.execute(
            "SELECT * FROM user_preferences WHERE user_id = ? AND category = ? AND pref_key = ?",
            (user_id, category, pref_key)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_user_preferences(self, user_id: str, category: str = None) -> List[Dict]:
        """Get all preferences for a user"""
        query = "SELECT * FROM user_preferences WHERE user_id = ?"
        params = [user_id]
        
        if category:
            query += " AND category = ?"
            params.append(category)
            
        async with self.connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


    # ========================================================================
    # Todo operations
    # ========================================================================

    async def create_task(
        self,
        task_id: str,
        user_id: str,
        title: str,
        description: str = None,
        priority: str = "medium",
        due_date: str = None
    ) -> Dict:
        """Create a new task"""
        now = datetime.utcnow().isoformat()
        
        await self.connection.execute(
            """
            INSERT INTO todos 
            (task_id, user_id, title, description, priority, due_date, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
            """,
            (task_id, user_id, title, description, priority, due_date, now, now)
        )
        await self.connection.commit()
        
        return await self.get_task(task_id)

    async def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task by ID"""
        async with self.connection.execute(
            "SELECT * FROM todos WHERE task_id = ?",
            (task_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_user_tasks(self, user_id: str, status: str = None) -> List[Dict]:
        """Get tasks for a user, optionally filtered by status"""
        query = "SELECT * FROM todos WHERE user_id = ?"
        params = [user_id]
        
        if status:
            query += " AND status = ?"
            params.append(status)
            
        query += " ORDER BY created_at DESC"
        
        async with self.connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def update_task_status(self, task_id: str, status: str) -> Optional[Dict]:
        """Update task status"""
        now = datetime.utcnow().isoformat()
        completed_at = now if status == "completed" else None
        
        await self.connection.execute(
            """
            UPDATE todos 
            SET status = ?, updated_at = ?, completed_at = ?
            WHERE task_id = ?
            """,
            (status, now, completed_at, task_id)
        )
        await self.connection.commit()
        
        return await self.get_task(task_id)

    # ========================================================================
    # Calendar Event operations
    # ========================================================================

    async def create_event(
        self,
        event_id: str,
        user_id: str,
        title: str,
        start_time: str,
        end_time: str,
        description: str = None,
        location: str = None
    ) -> Dict:
        """Create a new calendar event"""
        now = datetime.utcnow().isoformat()
        
        await self.connection.execute(
            """
            INSERT INTO calendar_events 
            (event_id, user_id, title, description, start_time, end_time, location, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'scheduled', ?, ?)
            """,
            (event_id, user_id, title, description, start_time, end_time, location, now, now)
        )
        await self.connection.commit()
        
        return await self.get_event(event_id)

    async def get_event(self, event_id: str) -> Optional[Dict]:
        """Get event by ID"""
        async with self.connection.execute(
            "SELECT * FROM calendar_events WHERE event_id = ?",
            (event_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_user_events(self, user_id: str, start_after: str = None) -> List[Dict]:
        """Get upcoming events for a user"""
        query = "SELECT * FROM calendar_events WHERE user_id = ? AND status != 'cancelled'"
        params = [user_id]
        
        if start_after:
            query += " AND start_time >= ?"
            params.append(start_after)
            
        query += " ORDER BY start_time ASC"
        
        async with self.connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def cancel_event(self, event_id: str) -> bool:
        """Cancel an event"""
        now = datetime.utcnow().isoformat()
        
        await self.connection.execute(
            """
            UPDATE calendar_events 
            SET status = 'cancelled', updated_at = ?
            WHERE event_id = ?
            """,
            (now, event_id)
        )
        await self.connection.commit()
        return True

# Global database instance
db_instance = None


async def get_database() -> Database:
    """Get or create the global database instance"""
    global db_instance
    if db_instance is None:
        db_instance = Database()
        await db_instance.connect()
    return db_instance
