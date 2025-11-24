"""
Mock tool implementations for the Personal Vibe CEO System
These simulate external service calls for demonstration purposes
"""

import logging
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MockCalendarService:
    """
    Mock calendar service for the Planner Agent
    Simulates scheduling appointments and retrieving calendar events
    """
    
    def __init__(self):
        self.events: Dict[str, Dict] = {}
        logger.info("MockCalendarService initialized")
    
    async def schedule_event(
        self,
        title: str,
        description: str,
        start_time: str,
        duration_minutes: int = 60,
        location: str = None
    ) -> Dict:
        """
        Schedule a calendar event
        
        Args:
            title: Event title
            description: Event description
            start_time: Start time (ISO format or relative like "next week")
            duration_minutes: Duration in minutes
            location: Optional location
            
        Returns:
            Created event details
        """
        event_id = str(uuid.uuid4())
        
        # Parse relative time expressions
        scheduled_time = self._parse_time(start_time)
        end_time = scheduled_time + timedelta(minutes=duration_minutes)
        
        event = {
            "event_id": event_id,
            "title": title,
            "description": description,
            "start_time": scheduled_time.isoformat(),
            "end_time": end_time.isoformat(),
            "location": location,
            "status": "scheduled"
        }
        
        self.events[event_id] = event
        
        logger.info(f"Scheduled event: {title} at {scheduled_time}")
        
        return event
    
    async def get_upcoming_events(self, days_ahead: int = 7) -> List[Dict]:
        """Get upcoming events within specified days"""
        now = datetime.now()
        cutoff = now + timedelta(days=days_ahead)
        
        upcoming = [
            event for event in self.events.values()
            if now <= datetime.fromisoformat(event["start_time"]) <= cutoff
        ]
        
        # Sort by start time
        upcoming.sort(key=lambda e: e["start_time"])
        
        return upcoming
    
    async def cancel_event(self, event_id: str) -> bool:
        """Cancel an event"""
        if event_id in self.events:
            self.events[event_id]["status"] = "cancelled"
            logger.info(f"Cancelled event: {event_id}")
            return True
        return False
    
    def _parse_time(self, time_str: str) -> datetime:
        """Parse relative time expressions"""
        now = datetime.now()
        time_lower = time_str.lower()
        
        if "next week" in time_lower:
            return now + timedelta(days=7, hours=14)  # Next week at 2pm
        elif "tomorrow" in time_lower:
            return now + timedelta(days=1, hours=10)  # Tomorrow at 10am
        elif "next month" in time_lower:
            return now + timedelta(days=30, hours=14)
        else:
            # Try to parse as ISO format
            try:
                return datetime.fromisoformat(time_str)
            except:
                # Default to tomorrow
                return now + timedelta(days=1, hours=14)


class MockSearchService:
    """
    Mock search service for the Knowledge Agent
    Simulates web search and article retrieval
    """
    
    def __init__(self):
        # Pre-defined search results for common topics
        self.knowledge_base = {
            "ai": [
                {"title": "Introduction to Modern AI Systems", "url": "https://example.com/ai-intro", "snippet": "A comprehensive guide to artificial intelligence..."},
                {"title": "Machine Learning Best Practices", "url": "https://example.com/ml-practices", "snippet": "Essential practices for ML development..."},
                {"title": "AI Ethics and Responsible Development", "url": "https://example.com/ai-ethics", "snippet": "Exploring ethical considerations in AI..."},
            ],
            "health": [
                {"title": "Sleep Hygiene: The Complete Guide", "url": "https://example.com/sleep-guide", "snippet": "Improving sleep quality through better habits..."},
                {"title": "Screen Time and Well-being", "url": "https://example.com/screen-time", "snippet": "Understanding the impact of digital devices..."},
                {"title": "Work-Life Balance Strategies", "url": "https://example.com/work-life", "snippet": "Maintaining balance in modern life..."},
            ],
            "mindfulness": [
                {"title": "Mindfulness for Beginners", "url": "https://example.com/mindfulness-101", "snippet": "Getting started with mindfulness practice..."},
                {"title": "Meditation Techniques", "url": "https://example.com/meditation", "snippet": "Effective meditation methods for daily life..."},
                {"title": "Stress Reduction Through Awareness", "url": "https://example.com/stress-reduction", "snippet": "Using mindfulness to manage stress..."},
            ],
        }
        logger.info("MockSearchService initialized")
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for content based on query
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results with title, url, snippet
        """
        query_lower = query.lower()
        
        # Find relevant results based on keywords
        results = []
        for topic, articles in self.knowledge_base.items():
            if topic in query_lower:
                results.extend(articles)
        
        # If no specific match, return random results
        if not results:
            all_results = [article for articles in self.knowledge_base.values() for article in articles]
            results = random.sample(all_results, min(max_results, len(all_results)))
        
        # Add relevance scores
        for i, result in enumerate(results[:max_results]):
            result["relevance_score"] = round(1.0 - (i * 0.1), 2)
        
        logger.info(f"Search for '{query}' returned {len(results[:max_results])} results")
        
        return results[:max_results]
    
    async def get_article_summary(self, url: str) -> str:
        """Get a summary of an article by URL"""
        # Simulate fetching article content
        summaries = [
            "This article provides comprehensive coverage of the topic with practical examples and recent research findings.",
            "An in-depth exploration of key concepts with actionable insights for implementation.",
            "Expert analysis combining theoretical foundations with real-world applications.",
        ]
        return random.choice(summaries)


class MockTodoService:
    """
    Mock to-do list service for the Planner Agent
    Simulates task management functionality
    """
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        logger.info("MockTodoService initialized")
    
    async def create_task(
        self,
        title: str,
        description: str = None,
        priority: str = "medium",
        due_date: str = None
    ) -> Dict:
        """
        Create a new task
        
        Args:
            title: Task title
            description: Optional description
            priority: Priority level (low, medium, high)
            due_date: Optional due date
            
        Returns:
            Created task details
        """
        task_id = str(uuid.uuid4())
        
        task = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        self.tasks[task_id] = task
        
        logger.info(f"Created task: {title} (priority: {priority})")
        
        return task
    
    async def get_tasks(self, status: str = None) -> List[Dict]:
        """Get tasks, optionally filtered by status"""
        if status:
            return [task for task in self.tasks.values() if task["status"] == status]
        return list(self.tasks.values())
    
    async def complete_task(self, task_id: str) -> bool:
        """Mark a task as complete"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "completed"
            self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
            logger.info(f"Completed task: {task_id}")
            return True
        return False


# Global tool instances
_calendar_service = None
_search_service = None
_todo_service = None


def get_calendar_service() -> MockCalendarService:
    """Get or create the global calendar service instance"""
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = MockCalendarService()
    return _calendar_service


def get_search_service() -> MockSearchService:
    """Get or create the global search service instance"""
    global _search_service
    if _search_service is None:
        _search_service = MockSearchService()
    return _search_service


def get_todo_service() -> MockTodoService:
    """Get or create the global todo service instance"""
    global _todo_service
    if _todo_service is None:
        _todo_service = MockTodoService()
    return _todo_service
