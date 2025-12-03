"""
Memory Tools
Tools for the Vibe Agent to interact with persistent user memory (facts, medical, preferences).
"""

import logging
import uuid
from typing import Dict, List, Optional

from ..db.database import get_database
from ..memory.memory_service import get_memory_service
from src.context import get_current_user_id

logger = logging.getLogger(__name__)

# ============================================================================
# Tool Functions
# ============================================================================

async def save_user_fact(
    category: str,
    fact_key: str,
    fact_value: str
) -> Dict:
    """
    Save a persistent fact about the user.
    Use this to remember important details like family members, job, birthday, etc.
    
    Args:
        category: Category of the fact (e.g., "personal", "work", "family", "interests").
        fact_key: Specific key for the fact (e.g., "spouse_name", "job_title").
        fact_value: The value of the fact.
    """
    try:
        db = await get_database()
        user_id = get_current_user_id()
        # Generate a deterministic ID based on user, category, key to ensure uniqueness/updates
        fact_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id}:{category}:{fact_key}"))
        
        result = await db.save_user_fact(
            fact_id=fact_id,
            user_id=user_id,
            category=category,
            fact_key=fact_key,
            fact_value=fact_value
        )
        return {"status": "success", "fact": result}
    except Exception as e:
        logger.error(f"Error saving user fact: {e}")
        return {"status": "error", "message": str(e)}

async def get_user_profile(categories: Optional[List[str]] = None) -> Dict:
    """
    Retrieve the user's persistent profile (facts and preferences).
    
    Args:
        categories: Optional list of categories to filter by.
    """
    try:
        db = await get_database()
        user_id = get_current_user_id()
        
        facts = []
        if categories:
            for cat in categories:
                cat_facts = await db.get_user_facts(user_id, category=cat)
                facts.extend(cat_facts)
        else:
            facts = await db.get_user_facts(user_id)
            
        preferences = await db.get_user_preferences(user_id)
        
        return {
            "status": "success",
            "facts": facts,
            "preferences": preferences
        }
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return {"status": "error", "message": str(e)}

async def save_medical_info(
    condition_name: str,
    status: str,
    notes: Optional[str] = None,
    medications: Optional[List[str]] = None
) -> Dict:
    """
    Save medical information to the user's profile.
    
    Args:
        condition_name: Name of the medical condition.
        status: Status of the condition (e.g., "active", "managed", "history").
        notes: Additional notes.
        medications: List of medications associated with this condition.
    """
    try:
        db = await get_database()
        user_id = get_current_user_id()
        # Generate deterministic ID
        condition_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id}:medical:{condition_name}"))
        
        result = await db.save_medical_condition(
            condition_id=condition_id,
            user_id=user_id,
            condition_name=condition_name,
            status=status,
            notes=notes,
            medications=medications
        )
        return {"status": "success", "condition": result}
    except Exception as e:
        logger.error(f"Error saving medical info: {e}")
        return {"status": "error", "message": str(e)}

async def get_medical_profile() -> Dict:
    """
    Retrieve the user's medical profile.
    """
    try:
        db = await get_database()
        user_id = get_current_user_id()
        conditions = await db.get_user_medical_profile(user_id)
        return {"status": "success", "conditions": conditions}
    except Exception as e:
        logger.error(f"Error getting medical profile: {e}")
        return {"status": "error", "message": str(e)}

async def save_user_preference(
    category: str,
    pref_key: str,
    pref_value: str
) -> Dict:
    """
    Save a user preference.
    
    Args:
        category: Category (e.g., "communication", "ui", "notifications").
        pref_key: Specific preference key.
        pref_value: Preference value.
    """
    try:
        db = await get_database()
        user_id = get_current_user_id()
        # Generate deterministic ID
        pref_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id}:pref:{category}:{pref_key}"))
        
        result = await db.save_user_preference(
            pref_id=pref_id,
            user_id=user_id,
            category=category,
            pref_key=pref_key,
            pref_value=pref_value
        )
        return {"status": "success", "preference": result}
    except Exception as e:
        logger.error(f"Error saving user preference: {e}")
        return {"status": "error", "message": str(e)}


async def search_memory(query: str) -> List[Dict]:
    """
    Search for past memories and conversations related to a specific topic.
    Use this when you need to recall details that are not in the current context.
    
    Args:
        query: The search query (e.g., "what did we discuss about the project", "details about my trip").
    """
    try:
        db = await get_database()
        memory_service = get_memory_service(db)
        user_id = get_current_user_id()
        
        results = await memory_service.get_agent_memories(
            user_id=user_id,
            agent_id="vibe", # Search across vibe agent memories by default
            query=query,
            limit=5
        )
        
        return [
            {"summary": r.get("summary_text"), "timestamp": r.get("created_at")} 
            for r in results
        ]
    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        return []


