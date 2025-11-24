# Setup Guide - Personal Vibe CEO System

This guide will walk you through setting up the development environment for the Personal Vibe CEO System.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** >= 18.0.0 ([Download](https://nodejs.org/))
- **Python** >= 3.11 ([Download](https://www.python.org/downloads/))
- **npm** >= 9.0.0 (comes with Node.js)
- **Git** (for version control)

## Google Cloud Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID - you'll need this later

### 2. Enable Required APIs

Enable the following APIs in your GCP project:

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable other required APIs
gcloud services enable compute.googleapis.com
gcloud services enable storage-api.googleapis.com
```

Alternatively, enable them via the [Cloud Console](https://console.cloud.google.com/apis/library).

### 3. Create Service Account

1. Navigate to **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Name it `vibe-ceo-service-account`
4. Grant the following roles:
   - Vertex AI User
   - Storage Object Admin (optional, for future use)
5. Click **Create Key** and download as JSON
6. Save the JSON file securely (e.g., `~/gcp-credentials/vibe-ceo-key.json`)

> ⚠️ **IMPORTANT**: Never commit this file to version control!

## Project Setup

### 1. Clone and Navigate to Project

```bash
cd /Users/nandika/WS/ADK_capstone/vibe_ceo
```

### 2. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-actual-project-id
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/your-service-account-key.json

# Vertex AI Configuration
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-pro

# API Configuration (defaults are fine for local development)
API_PORT=8000
API_HOST=localhost
API_BASE_URL=http://localhost:8000

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Database
DATABASE_PATH=./data/vibe_ceo.db

# Development
NODE_ENV=development
LOG_LEVEL=debug
```

### 3. Install Node.js Dependencies

```bash
# Install all workspace dependencies (root + frontend + shared)
npm install
```

This will install dependencies for:
- Root workspace
- Frontend (`apps/web`)
- Shared types (`packages/shared`)

### 4. Set Up Python Environment

#### Create Virtual Environment

```bash
cd apps/api
python -m venv venv
```

#### Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

#### Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- FastAPI and Uvicorn (web framework)
- Google Cloud AI Platform and Generative AI SDKs
- WebSocket support
- SQLite async support
- Testing tools (pytest)

### 5. Initialize Database

```bash
# Make sure you're in apps/api with venv activated
cd /Users/nandika/WS/ADK_capstone/vibe_ceo/apps/api
python src/db/seed.py
```

This will:
- Create the SQLite database at `data/vibe_ceo.db`
- Create all required tables
- Seed with demo data (user, health logs, memory contexts)

You should see output like:
```
✅ Created user: Alex Johnson
📊 Creating health logs...
🧠 Creating memory contexts...
🔧 Creating tool action logs...
✅ Database seeding complete!
```

## Verify Installation

### 1. Check Python Dependencies

```bash
cd apps/api
source venv/bin/activate  # if not already activated
python -c "import fastapi, google.generativeai; print('✅ Python setup OK')"
```

### 2. Check Node.js Dependencies

```bash
cd /Users/nandika/WS/ADK_capstone/vibe_ceo
npm run type-check --workspace=packages/shared
```

### 3. Verify Database

```bash
cd /Users/nandika/WS/ADK_capstone/vibe_ceo
ls -la data/vibe_ceo.db
```

You should see the database file created.

## Running the Application

### Option 1: Run Everything Together

From the project root:

```bash
npm run dev
```

This starts both frontend and backend concurrently.

### Option 2: Run Services Separately

**Terminal 1 - Backend API:**
```bash
cd apps/api
source venv/bin/activate
python api.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev:web
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)

## Troubleshooting

### Google Cloud Authentication Issues

**Error:** `DefaultCredentialsError` or authentication failures

**Solutions:**
1. Verify `GOOGLE_APPLICATION_CREDENTIALS` path in `.env` is absolute
2. Check the service account has proper roles
3. Try authenticating with gcloud:
   ```bash
   gcloud auth application-default login
   ```

### Module Not Found Errors (Python)

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solutions:**
1. Ensure virtual environment is activated
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Port Already in Use

**Error:** `Address already in use` on port 8000 or 3000

**Solutions:**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port in .env
API_PORT=8001
```

### Database Locked Errors

**Solutions:**
1. Close all connections to the database
2. Delete and recreate:
   ```bash
   rm data/vibe_ceo.db
   python apps/api/src/db/seed.py
   ```

### CORS Errors

**Error:** Blocked by CORS policy

**Solutions:**
1. Verify backend is running on port 8000
2. Check CORS configuration in `apps/api/api.py`
3. Ensure frontend uses correct API URL in `.env`

## Development Workflow

### Building Shared Types

After modifying types in `packages/shared/src/types.ts`:

```bash
npm run build --workspace=packages/shared
```

### Running Tests

```bash
# Python tests
npm run test:api

# Frontend tests (when implemented)
cd apps/web && npm test
```

### Code Formatting

```bash
# Format all TypeScript/JavaScript
npm run format

# Python formatting (optional - add black/ruff)
cd apps/api
pip install black
black src/
```

## Next Steps

Once setup is complete:

1. ✅ Verify the backend API is accessible at http://localhost:8000
2. ✅ Verify the frontend loads at http://localhost:3000
3. ✅ Test the `/api/chat` endpoint using the Swagger UI
4. ✅ Review the project documentation in `doc/` folder

## Getting Help

If you encounter issues:

1. Check the main [README.md](../README.md)
2. Review error logs in terminal
3. Verify all prerequisites are installed
4. Check Google Cloud console for API quota/billing issues

---

**Ready to develop!** 🚀 Proceed to implement the three agents (Vibe, Planner, Knowledge).
