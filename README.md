# Personal Vibe CEO System

A capstone project demonstrating advanced multi-agent AI architecture using Google ADK (Agent Development Kit). The system features three specialized AI agents that work together to provide proactive personal well-being support and task management.

## 🎯 Project Overview

The **Personal Vibe CEO System** showcases:
- **Multi-agent orchestration** with three specialized agents (Vibe, Planner, Knowledge)
- **Google ADK integration** for memory management and observability
- **Polyglot architecture** (Python backend + TypeScript frontend)
- **Real-time voice and text interfaces** via WebSocket streaming

### The Three Agents

1. **Vibe Agent (A1)** - Proactive Balance Check
   - Monitors emotional and health well-being
   - Uses long-term memory to recall context
   - Initiates proactive check-ins based on data patterns

2. **Planner Agent (A2)** - Task Scheduler
   - Manages calendar and to-do items
   - Executes tool calls to schedule appointments
   - Generates structured action lists

3. **Knowledge Agent (A3)** - Learning Digest Curator
   - Searches and curates personalized learning content
   - Creates structured learning digests
   - Formats information for easy consumption

## 🏗️ Architecture

### Technology Stack

**Frontend:**
- Next.js 15 (TypeScript)
- Tailwind CSS
- WebSocket client for voice streaming

**Backend:**
- Python 3.11+
- FastAPI
- Google ADK (Vertex AI)
- SQLite database

**Infrastructure:**
- npm workspaces monorepo
- Bidirectional WebSocket for real-time voice
- REST API for text-based chat

### Project Structure

```
vibe_ceo/
├── apps/
│   ├── web/              # Next.js frontend (TypeScript)
│   │   ├── app/          # Next.js app router
│   │   └── components/   # React components
│   └── api/              # Python backend (FastAPI)
│       ├── src/
│       │   ├── agents/   # Agent implementations
│       │   ├── tools/    # Mock tool integrations
│       │   ├── memory/   # Google ADK memory
│       │   └── db/       # Database models
│       └── api.py        # FastAPI entry point
├── packages/
│   └── shared/           # Shared TypeScript types
├── doc/                  # Project documentation
└── package.json          # Monorepo configuration
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** >= 18.0.0
- **Python** >= 3.11
- **npm** >= 9.0.0
- **Google Cloud Account** with Vertex AI enabled

### Environment Setup

1. **Clone and install dependencies:**

```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd apps/web && npm install && cd ../..

# Install Python dependencies
cd apps/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ../..
```

2. **Configure environment variables:**

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Google Cloud credentials
# Required variables:
# - GOOGLE_CLOUD_PROJECT
# - GOOGLE_APPLICATION_CREDENTIALS
# - VERTEX_AI_LOCATION
```

3. **Set up Google Cloud credentials:**

- Create a service account in your GCP project
- Download the JSON key file
- Set the path in `.env` as `GOOGLE_APPLICATION_CREDENTIALS`

### Running the Application

**Option 1: Run both services concurrently**

```bash
npm run dev
```

**Option 2: Run services separately**

```bash
# Terminal 1 - Frontend
npm run dev:web

# Terminal 2 - Backend
npm run dev:api
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📋 Development

### Building Components

```bash
# Build shared types
npm run build --workspace=packages/shared

# Build frontend
npm run build:web
```

### Testing

```bash
# Run all tests
npm test

# Run backend tests only
npm run test:api

# Run frontend tests only
cd apps/web && npm test
```

### Code Quality

```bash
# Format code
npm run format

# Type check
npm run type-check

# Lint
npm run lint
```

## 🎓 Features & Capabilities

### Feature 1: Proactive Balance Check (FR1)
The Vibe Agent monitors simulated health data and initiates conversations when it detects patterns requiring attention.

### Feature 2: Mandatory Check-up Scheduler (FR2/FR3)
The Planner Agent integrates with a mocked calendar service to schedule appointments and manage tasks.

### Feature 3: Personalized Learning Digest (FR4)
The Knowledge Agent curates learning content based on user interests using a simulated search API.

### Voice & Chat Interfaces (FR2)
- Real-time voice input via WebSocket streaming
- Text-based chat interface
- Agent context switching (FR5)
- Response latency <3 seconds (NFR4)

## 📊 Google ADK Integration

The project demonstrates Google ADK capabilities:

- **Memory Management** (NFR2): Long-term context storage for the Vibe Agent
- **Observability** (NFR3): Comprehensive logging of agent decisions and tool calls
- **Tool Calling**: Standardized integration with external services

## 📚 Documentation

- [Project Brief](doc/project_breaf.md) - High-level vision and scope
- [Product Requirements (PRD)](doc/prd.md) - Detailed requirements and epics
- [Architecture Document](doc/archtect.md) - Technical architecture and design

## 🔐 Security & Privacy

- All data is simulated/local (no real health data)
- Authentication is mocked for capstone demonstration
- Google Cloud credentials should be kept secure and never committed

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'google.genai'"**
- Ensure you've activated the Python virtual environment
- Install dependencies: `pip install -r apps/api/requirements.txt`

**CORS errors when connecting frontend to backend**
- Verify backend is running on port 8000
- Check CORS configuration in `apps/api/api.py`

**WebSocket connection fails**
- Ensure both frontend and backend are running
- Check console for error messages
- Verify WebSocket URL in frontend configuration

## 📝 License

This is a capstone project for demonstration purposes.

## 👥 Contributing

This is a capstone project and not currently accepting contributions.

---

**Built with ❤️ using Google ADK, Next.js, and FastAPI**
