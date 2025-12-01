"""
Shared context utilities for building enhanced prompts with memory, health data, and user preferences.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

async def get_context_string(
    user_id: str,
    db,
    memories: List[Dict] = None,
    health_data: Optional[Dict] = None,
    personal_context: str = "",
    short_term_context: str = "",
    include_time: bool = True
) -> str:
    """
    Generate context string (Time, Personal, Health, Memory) without user message.
    """
    parts = []
    
    # 1. Add Time Context
    if include_time:
        try:
            pref = await db.get_user_preference(user_id, "general", "timezone")
            tz_str = pref["pref_value"] if pref else "UTC"
            user_tz = ZoneInfo(tz_str)
            now_local = datetime.now(user_tz)
            parts.append(f"Current User Time: {now_local.strftime('%Y-%m-%d %H:%M')} ({tz_str})")
        except Exception as e:
            logger.warning(f"Failed to get user timezone context: {e}")
            parts.append(f"Current UTC Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}")
    
    # 2. Add Personal Context (Facts, Prefs, Medical, Tasks, Events)
    if personal_context:
        parts.append(f"\n{personal_context}")
    
    # 3. Add Health Data
    if health_data:
        parts.append(f"\nRecent health metrics:")
        parts.append(f"- Sleep: {health_data.get('sleep_hours', 'N/A')} hours")
        parts.append(f"- Screen time: {health_data.get('screen_time', 'N/A')} hours")
        parts.append(f"- Balance score: {health_data.get('imbalance_score', 'N/A')}/10")
    
    # 4. Add Memory Context
    if memories:
        memory_text = "\n".join([f"- {m.get('summary_text', '')}" for m in memories[:3]])
        parts.append(f"\nPrevious interactions/context:\n{memory_text}")

    # 5. Add Short-Term Context (Session)
    if short_term_context:
        parts.append(f"\nRecent Conversation History:\n{short_term_context}")
    
    # 6. Add User ID (for tracking)
    parts.append(f"\nUser ID: {user_id}")
    
    return "\n".join(parts)

async def build_context_prompt(
    message: str,
    user_id: str,
    db,
    memories: List[Dict] = None,
    health_data: Optional[Dict] = None,
    personal_context: str = "",
    short_term_context: str = "",
    include_time: bool = True
) -> str:
    """
    Build a comprehensive context prompt for agents.
    """
    context = await get_context_string(
        user_id=user_id,
        db=db,
        memories=memories,
        health_data=health_data,
        personal_context=personal_context,
        short_term_context=short_term_context,
        include_time=include_time
    )
    
    return f"User message: {message}\n{context}"
