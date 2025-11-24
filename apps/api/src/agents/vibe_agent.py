"""
Vibe Agent (A1) - Proactive Balance Check
Monitors emotional and health well-being, uses long-term memory
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class VibeAgent:
    """
    The Vibe Agent focuses on emotional well-being and proactive check-ins
    
    Features:
    - Monitors health data (sleep, screen time)
    - Uses long-term memory to recall context
    - Initiates proactive conversations when imbalance detected
    - Employs empathetic language (FR6)
    """
    
    def __init__(self, db, memory_service=None):
        """
        Initialize the Vibe Agent
        
        Args:
            db: Database instance for health logs
            memory_service: Optional memory service for long-term context
        """
        self.db = db
        self.memory_service = memory_service
        self.agent_id = "vibe"
        logger.info("VibeAgent initialized")
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process user message and generate empathetic response
        
        Args:
            user_id: User identifier
            message: User's message
            context: Optional conversation context
            
        Returns:
            Response with agent metadata
        """
        start_time = datetime.now()
        
        # Retrieve user's memory context
        memories = await self._get_memories(user_id)
        
        # Get recent health data
        health_logs = await self.db.get_user_health_logs(user_id, limit=3)
        
        # Generate empathetic response
        response_text = await self._generate_response(
            user_id,
            message,
            memories,
            health_logs
        )
        
        # Calculate latency
        latency = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return {
            "agent_type": self.agent_id,
            "response": response_text,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "memory_retrieved": [m.get("summary_text") for m in memories[:2]],
                "tools_used": [],
                "latency_ms": latency,
                "health_assessment": self._assess_health(health_logs) if health_logs else None
            }
        }
    
    async def check_for_proactive_outreach(self, user_id: str) -> Optional[Dict]:
        """
        Check if proactive check-in is needed (FR1)
        
        Args:
            user_id: User identifier
            
        Returns:
            Proactive message if needed, None otherwise
        """
        # Get recent health data
        health_logs = await self.db.get_user_health_logs(user_id, limit=7)
        
        if not health_logs:
            return None
        
        # Calculate average imbalance score
        avg_imbalance = sum(log["imbalance_score"] for log in health_logs) / len(health_logs)
        
        # Trigger proactive check-in if imbalance is high
        if avg_imbalance > 10.0:
            memories = await self._get_memories(user_id)
            
            message = await self._generate_proactive_message(
                user_id,
                health_logs,
                memories
            )
            
            logger.info(f"Proactive check-in triggered for user {user_id} (imbalance: {avg_imbalance:.1f})")
            
            return {
                "agent_type": self.agent_id,
                "response": message,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "proactive": True,
                    "trigger": "high_imbalance",
                    "imbalance_score": round(avg_imbalance, 1),
                    "memory_retrieved": [m.get("summary_text") for m in memories[:2]]
                }
            }
        
        return None
    
    async def _get_memories(self, user_id: str) -> List[Dict]:
        """Retrieve long-term memory contexts for this agent"""
        if self.memory_service:
            # Use Google ADK memory service
            return await self.memory_service.get_agent_memories(user_id, self.agent_id)
        else:
            # Fallback to database
            return await self.db.get_agent_memories(user_id, self.agent_id, limit=5)
    
    async def _generate_response(
        self,
        user_id: str,
        message: str,
        memories: List[Dict],
        health_logs: List[Dict]
    ) -> str:
        """
        Generate empathetic response based on context
        
        This is a simplified version. In production, this would use
        Google ADK's generative capabilities.
        """
        # Analyze message sentiment
        message_lower = message.lower()
        
        # Build context-aware response
        response_parts = []
        
        # Acknowledge user's feelings
        if any(word in message_lower for word in ["stressed", "tired", "overwhelmed"]):
            response_parts.append("I hear that you're feeling stressed. That's completely understandable.")
        elif any(word in message_lower for word in ["good", "great", "better"]):
            response_parts.append("I'm glad to hear you're feeling positive!")
        
        # Reference memory if relevant
        if memories and any(word in message_lower for word in ["work", "balance", "sleep"]):
            memory_text = memories[0].get("summary_text", "")
            if "work-life" in memory_text or "sleep" in memory_text:
                response_parts.append(f"I remember we talked about this before. {memory_text}")
        
        # Provide health insights if available
        if health_logs:
            latest_log = health_logs[0]
            if latest_log["imbalance_score"] > 10:
                response_parts.append(
                    f"I've noticed your recent sleep has been around {latest_log['sleep_hours']}hours, "
                    f"which might be contributing to how you feel. How about we work on improving that together?"
                )
        
        # Always end with supportive message
        response_parts.append("I'm here to support you. What would help you most right now?")
        
        return " ".join(response_parts)
    
    async def _generate_proactive_message(
        self,
        user_id: str,
        health_logs: List[Dict],
        memories: List[Dict]
    ) -> str:
        """Generate proactive check-in message (FR1)"""
        latest_log = health_logs[0] if health_logs else None
        
        # Build personalized proactive message
        message_parts = [
            "Hey! I wanted to check in with you.",
        ]
        
        if latest_log:
            if latest_log["sleep_hours"] < 7:
                message_parts.append(
                    f"I noticed you've been getting around {latest_log['sleep_hours']} hours of sleep lately, "
                    "which is less than ideal."
                )
            
            if latest_log["screen_time"] > 8:
                message_parts.append(
                    f"Also, your screen time has been around {latest_log['screen_time']} hours, "
                    "which might be affecting your well-being."
                )
        
        # Reference relevant memories
        if memories:
            for memory in memories[:1]:
                summary = memory.get("summary_text", "")
                if "stress" in summary or "balance" in summary:
                    message_parts.append(f"Considering what we discussed earlier about {summary.lower()}, ")
                    message_parts.append("I thought it might be a good time to see how you're managing.")
        
        message_parts.append("How are you feeling about things? Is there anything I can help with?")
        
        return " ".join(message_parts)
    
    def _assess_health(self, health_logs: List[Dict]) -> Dict:
        """Assess health status from logs"""
        if not health_logs:
            return {"status": "no_data"}
        
        latest = health_logs[0]
        avg_sleep = sum(log["sleep_hours"] for log in health_logs) / len(health_logs)
        avg_screen = sum(log["screen_time"] for log in health_logs) / len(health_logs)
        
        status = "good"
        if latest["imbalance_score"] > 15:
            status = "needs_attention"
        elif latest["imbalance_score"] > 10:
            status = "moderate"
        
        return {
            "status": status,
            "avg_sleep_hours": round(avg_sleep, 1),
            "avg_screen_hours": round(avg_screen, 1),
            "current_imbalance": round(latest["imbalance_score"], 1)
        }
