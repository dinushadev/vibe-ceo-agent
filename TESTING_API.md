# Testing the Personal Vibe CEO System API

This guide shows you how to interact with the backend API.

## Method 1: Swagger UI (Interactive Documentation) 🎯

**Easiest way to test!**

1. Make sure the backend is running:
   ```bash
   cd /Users/nandika/WS/ADK_capstone/vibe_ceo/apps/api
   python api.py
   ```

2. Open in your browser:
   ```
   http://localhost:8000/docs
   ```

3. You'll see an interactive API documentation page where you can:
   - Click on any endpoint
   - Click "Try it out"
   - Fill in the request body
   - Click "Execute"
   - See the response

### Example: Test the Chat Endpoint

1. Go to http://localhost:8000/docs
2. Find `POST /api/chat`
3. Click "Try it out"
4. Use this request body:
   ```json
   {
     "user_id": "demo-user-001",
     "message": "I'm feeling stressed about work",
     "context": {}
   }
   ```
5. Click "Execute"
6. You'll see the Vibe Agent's response!

## Method 2: Using curl (Command Line)

### Test 1: Health Check
```bash
curl http://localhost:8000/
```

### Test 2: Chat with Vibe Agent
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo-user-001",
    "message": "I feel tired and overwhelmed",
    "context": {}
  }'
```

### Test 3: Schedule Appointment (Planner Agent)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo-user-001",
    "message": "Schedule a doctor checkup for next week",
    "context": {}
  }'
```

### Test 4: Learning Digest (Knowledge Agent)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo-user-001",
    "message": "Create a learning digest about AI",
    "context": {}
  }'
```

### Test 5: Proactive Check-In
```bash
curl -X POST "http://localhost:8000/api/proactive-check?user_id=demo-user-001"
```

### Test 6: Get User Config
```bash
curl "http://localhost:8000/api/config/user?user_id=demo-user-001"
```

## Method 3: Using Python Requests

Create a test script `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Test 1: Health check
response = requests.get(f"{BASE_URL}/")
print("Health Check:", response.json())

# Test 2: Chat with Vibe Agent
chat_request = {
    "user_id": "demo-user-001",
    "message": "I'm feeling stressed",
    "context": {}
}
response = requests.post(f"{BASE_URL}/api/chat", json=chat_request)
print("\nVibe Agent Response:")
print(json.dumps(response.json(), indent=2))

# Test 3: Schedule appointment (Planner Agent)
schedule_request = {
    "user_id": "demo-user-001",
    "message": "Schedule a dentist appointment",
    "context": {}
}
response = requests.post(f"{BASE_URL}/api/chat", json=schedule_request)
print("\nPlanner Agent Response:")
print(json.dumps(response.json(), indent=2))

# Test 4: Learning digest (Knowledge Agent)
learning_request = {
    "user_id": "demo-user-001",
    "message": "Create a learning digest",
    "context": {}
}
response = requests.post(f"{BASE_URL}/api/chat", json=learning_request)
print("\nKnowledge Agent Response:")
print(json.dumps(response.json(), indent=2))

# Test 5: Proactive check
response = requests.post(f"{BASE_URL}/api/proactive-check", params={"user_id": "demo-user-001"})
print("\nProactive Check:")
print(json.dumps(response.json(), indent=2))
```

Run it:
```bash
python test_api.py
```

## Method 4: From Frontend (JavaScript/React)

When you build the frontend, you'll use this pattern:

```javascript
// In a React component or API service file
async function sendMessage(userId, message) {
  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      message: message,
      context: {}
    })
  });
  
  const data = await response.json();
  return data;
}

// Usage
const result = await sendMessage('demo-user-001', 'I feel stressed');
console.log(result.response);
```

## Testing Different Agents

The orchestrator automatically routes to the right agent based on keywords:

| Message Keywords              | Routes To           | Example                             |
| ----------------------------- | ------------------- | ----------------------------------- |
| feel, stressed, tired, sleep  | **Vibe Agent**      | "I feel tired and stressed"         |
| schedule, appointment, doctor | **Planner Agent**   | "Schedule a doctor appointment"     |
| learn, research, find, digest | **Knowledge Agent** | "Create a learning digest about AI" |

## Example Test Scenarios

### Scenario 1: Emotional Check-In (Vibe Agent)
```json
{
  "user_id": "demo-user-001",
  "message": "I'm feeling really overwhelmed with work",
  "context": {}
}
```

**Expected Response:** Empathetic response referencing health data and memories

### Scenario 2: Schedule Appointment (Planner Agent)
```json
{
  "user_id": "demo-user-001",
  "message": "Book a medical checkup next week",
  "context": {}
}
```

**Expected Response:** Confirmation of scheduled event with structured action list

### Scenario 3: Learning Digest (Knowledge Agent)
```json
{
  "user_id": "demo-user-001",
  "message": "Create a learning digest about machine learning",
  "context": {}
}
```

**Expected Response:** Structured digest with articles and key points

### Scenario 4: Force Specific Agent
```json
{
  "user_id": "demo-user-001",
  "message": "Hello",
  "context": {
    "agent_preference": "knowledge"
  }
}
```

**Expected Response:** Knowledge Agent handles it regardless of message content

## Troubleshooting

**Error: Connection refused**
- Make sure backend is running: `python api.py`
- Check it's on port 8000: `http://localhost:8000`

**Error: User not found**
- Use the demo user ID: `demo-user-001`
- Or check what users exist: Look in `data/vibe_ceo.db`

**No response / timeout**
- Check backend logs in terminal
- Ensure database file exists: `ls -la data/vibe_ceo.db`

## Quick Start Commands

```bash
# Terminal 1: Start backend
cd /Users/nandika/WS/ADK_capstone/vibe_ceo/apps/api
python api.py

# Terminal 2: Test with curl
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo-user-001", "message": "I feel stressed", "context": {}}'

# Or just open browser to:
# http://localhost:8000/docs
```

**Pro Tip:** The Swagger UI at `/docs` is the fastest way to test! 🚀
