#!/usr/bin/env python3
"""
Quick test script for the Personal Vibe CEO System API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    data = response.json()
    print(json.dumps(data, indent=2))
    print()

def main():
    print("\n🚀 Testing Personal Vibe CEO System API\n")
    
    # Test 1: Health check
    print("Test 1: Health Check")
    response = requests.get(f"{BASE_URL}/")
    print_response("Health Check", response)
    
    # Test 2: Vibe Agent (emotional well-being)
    print("Test 2: Vibe Agent - Emotional Check-In")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "user_id": "demo-user-001",
            "message": "I'm feeling really stressed and tired",
            "context": {}
        }
    )
    print_response("Vibe Agent Response", response)
    
    # Test 3: Planner Agent (scheduling)
    print("Test 3: Planner Agent - Schedule Appointment")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "user_id": "demo-user-001",
            "message": "Schedule a doctor checkup for next week",
            "context": {}
        }
    )
    print_response("Planner Agent Response", response)
    
    # Test 4: Knowledge Agent (learning digest)
    print("Test 4: Knowledge Agent - Learning Digest")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "user_id": "demo-user-001",
            "message": "Create a learning digest about AI",
            "context": {}
        }
    )
    print_response("Knowledge Agent Response", response)
    
    # Test 5: Proactive check-in
    print("Test 5: Proactive Check-In Trigger")
    response = requests.post(
        f"{BASE_URL}/api/proactive-check",
        params={"user_id": "demo-user-001"}
    )
    print_response("Proactive Check Result", response)
    
    # Test 6: Get user config
    print("Test 6: Get User Configuration")
    response = requests.get(
        f"{BASE_URL}/api/config/user",
        params={"user_id": "demo-user-001"}
    )
    print_response("User Config", response)
    
    print("\n✅ All tests completed!\n")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the backend is running:")
        print("  cd /Users/nandika/WS/ADK_capstone/vibe_ceo/apps/api")
        print("  python api.py\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
