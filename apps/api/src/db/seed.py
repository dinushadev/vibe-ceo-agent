"""
Seed database with simulated data for demo purposes
"""

import asyncio
import uuid
import random
from datetime import datetime, timedelta
from database import Database, get_database


async def seed_database():
    """Seed the database with sample data"""
    db = await get_database()
    
    # Create demo user
    user_id = "demo-user-001"
    
    try:
        user = await db.create_user(
            user_id=user_id,
            name="Alex Johnson",
            learning_interests=["AI", "Machine Learning", "Health Tech", "Mindfulness"]
        )
        print(f"✅ Created user: {user['name']}")
    except Exception as e:
        print(f"User may already exist: {e}")
        user = await db.get_user(user_id)
    
    # Create simulated health logs for the past week
    print("\n📊 Creating health logs...")
    for days_ago in range(7, 0, -1):
        log_date = datetime.utcnow() - timedelta(days=days_ago)
        
        # Simulate varying health data
        sleep_hours = random.uniform(5.5, 8.5)
        screen_time = random.uniform(4.0, 12.0)
        
        # Calculate imbalance score (higher = more imbalanced)
        imbalance_score = 0
        if sleep_hours < 7:
            imbalance_score += (7 - sleep_hours) * 10
        if screen_time > 8:
            imbalance_score += (screen_time - 8) * 5
        
        log_id = str(uuid.uuid4())
        await db.create_health_log(
            log_id=log_id,
            user_id=user_id,
            sleep_hours=round(sleep_hours, 1),
            screen_time=round(screen_time, 1),
            imbalance_score=round(imbalance_score, 1),
            notes=f"Simulated data for {days_ago} days ago"
        )
        
        print(f"  ✓ Health log for {log_date.strftime('%Y-%m-%d')}: "
              f"sleep={sleep_hours:.1f}h, screen={screen_time:.1f}h, "
              f"imbalance={imbalance_score:.1f}")
    
    # Create sample memory contexts for Vibe Agent
    print("\n🧠 Creating memory contexts...")
    memory_contexts = [
        {
            "agent_id": "vibe",
            "summary_text": "User expressed feeling stressed about work-life balance last week",
            "metadata": {"emotion": "stressed", "topic": "work-life-balance"}
        },
        {
            "agent_id": "vibe",
            "summary_text": "User mentioned wanting to improve sleep schedule",
            "metadata": {"goal": "better-sleep", "priority": "high"}
        },
        {
            "agent_id": "planner",
            "summary_text": "User has recurring doctor checkup scheduled monthly",
            "metadata": {"event_type": "health-checkup", "frequency": "monthly"}
        },
        {
            "agent_id": "knowledge",
            "summary_text": "User interested in learning about AI ethics and applications",
            "metadata": {"topic": "ai-ethics", "learning_level": "intermediate"}
        }
    ]
    
    for context_data in memory_contexts:
        context_id = str(uuid.uuid4())
        await db.create_memory_context(
            context_id=context_id,
            user_id=user_id,
            agent_id=context_data["agent_id"],
            summary_text=context_data["summary_text"],
            metadata=context_data["metadata"]
        )
        print(f"  ✓ Memory for {context_data['agent_id']} agent: "
              f"{context_data['summary_text'][:50]}...")
    
    # Create sample tool action logs
    print("\n🔧 Creating tool action logs...")
    tool_logs = [
        {
            "tool_name": "calendar_service",
            "input_query": "Schedule dentist appointment for next week",
            "output_result": "Appointment scheduled for Nov 30, 2025 at 2:00 PM",
            "success": True,
            "execution_time_ms": 245
        },
        {
            "tool_name": "search_api",
            "input_query": "Latest developments in AI reasoning",
            "output_result": "Found 5 relevant articles from top sources",
            "success": True,
            "execution_time_ms": 1320
        },
        {
            "tool_name": "todo_service",
            "input_query": "Add meditation practice to daily routine",
            "output_result": "Task added to daily routine checklist",
            "success": True,
            "execution_time_ms": 180
        }
    ]
    
    for log_data in tool_logs:
        log_id = str(uuid.uuid4())
        await db.log_tool_action(
            log_id=log_id,
            user_id=user_id,
            tool_name=log_data["tool_name"],
            input_query=log_data["input_query"],
            output_result=log_data["output_result"],
            success=log_data["success"],
            execution_time_ms=log_data["execution_time_ms"]
        )
        print(f"  ✓ Tool log: {log_data['tool_name']} - {log_data['input_query'][:40]}...")
    
    print("\n✅ Database seeding complete!")
    print(f"\nDemo user ID: {user_id}")
    print("You can use this user ID to test the API endpoints.")
    
    await db.close()


if __name__ == "__main__":
    print("🌱 Seeding Personal Vibe CEO System database...\n")
    asyncio.run(seed_database())
