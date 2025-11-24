That's the final mandate\! I will compile the complete **Fullstack Architecture Document** by integrating the initial plan, the key technical decisions, and the essential course corrections (Polyglot Monolith, Voice/ADK requirements) into a single, cohesive document.

I am **Winston, the Architect** 🏗️, and here is the complete documentation for the **"Personal Vibe CEO"** system.

-----

# 🏗️ The Personal Vibe CEO System: Fullstack Architecture Document

### Version 1.0 (Capstone MVP)

| Change                 | Date         | Version | Description                                                                                           | Author    |
| :--------------------- | :----------- | :------ | :---------------------------------------------------------------------------------------------------- | :-------- |
| Initial draft complete | Nov 24, 2025 | 1.0     | Defines Polyglot Monolith, Google ADK integration, Voice/Bidi-streaming protocol, and MVP components. | Architect |

## 1\. High Level Architecture

The system uses a **Polyglot Monolith** architecture within an **npm Workspace Monorepo**. This approach minimizes infrastructure complexity for the capstone, allowing the project to focus entirely on advanced agent logic (NFR1, NFR2).

| Feature                  | Design Decision                    | Rationale                                                                                            |
| :----------------------- | :--------------------------------- | :--------------------------------------------------------------------------------------------------- |
| **Architectural Style**  | **Monolith** (Conceptual)          | Fastest path to integrated capstone demo; minimal deployment overhead.                               |
| **Language**             | **Polyglot (Python / TypeScript)** | Python is mandatory for Google ADK Agent Logic (NFR1); TypeScript is used for the modern Next.js UI. |
| **Memory/Orchestration** | **Google ADK**                     | **MANDATORY** for advanced memory (NFR2), observability (NFR3), and agent protocol.                  |
| **Data/Tools**           | **Simulated/Mocked**               | Eliminates integration time/complexity (NFR5).                                                       |

### High Level Architecture Diagram

This visualization shows the mandatory separation of agent logic (Python) from the web interface (TypeScript) within the deployment container.

```mermaid
graph TD
    A[User: Voice/Chat Interface] --> B(Web/Mobile Browser)
    B --> C[Frontend: Next.js App (TS)]
    C -->|Internal REST API| D[TS API Service: Router]
    
    subgraph Agent Runtime Container (Monorepo)
        D -->|HTTP Request / WebSocket Stream| E[Python Agent Service]
        E --> E1[A1: Vibe Agent]
        E --> E2[A2: Planner Agent]
        E --> E3[A3: Knowledge Agent]
        E1 & E2 & E3 --> G(Google ADK: Orchestration/Memory)
        E1 & E2 & E3 --> H[Tool Mocking Layer]
    end
    
    G --> I[Data: Local SQLite DB]
    
    style C fill:#FFE4B5,stroke:#333
    style D fill:#F0E68C,stroke:#333
    style E fill:#ADD8E6,stroke:#333
    style G fill:#90EE90,stroke:#333
    style H fill:#E6E6FA,stroke:#333
    style I fill:#D8BFD8,stroke:#333
```

-----

## 2\. Tech Stack and Language Protocol

### [cite\_start]Technology Stack Table [cite: 978, 981]

| Category         | Technology                            | Version       | Purpose                                              | Rationale                                                                    |
| :--------------- | :------------------------------------ | :------------ | :--------------------------------------------------- | :--------------------------------------------------------------------------- |
| **FE Framework** | Next.js (or Vite/React)               | Latest Stable | Frontend UI.                                         | [cite\_start]Excellent routing and performance for a modern demo[cite: 982]. |
| **FE Language**  | TypeScript                            | Latest Stable | Type safety across shared components and APIs.       | Mandatory for type safety.                                                   |
| **BE Framework** | Minimalist Python API (FastAPI/Flask) | Latest Stable | [cite\_start]Agent Monolith host for ADK[cite: 984]. | ADK compatibility (NFR1) and minimal configuration overhead.                 |
| **Agent Core**   | Google ADK                            | Latest Stable | Orchestration, Memory, Evaluation Layer.             | **MANDATORY** for capstone focus on advanced agentic features.               |
| **API Style**    | REST                                  | N/A           | API communication style.                             | Simple to implement mock endpoints and clear communication.                  |
| **Database**     | SQLite (or JSON files)                | N/A           | Simple, file-based data storage.                     | Eliminates DB setup/hosting time.                                            |
| **Styling**      | Tailwind CSS                          | Latest Stable | Rapid UI development and responsiveness.             | Speed of development for the UI.                                             |

### API and Voice Communication Protocol

1.  [cite\_start]**Standard Chat:** The TypeScript Frontend calls the Python Agent Service via an internal **REST API** endpoint (e.g., `/process-query`)[cite: 985].
2.  **Real-time Voice:** The Frontend (TypeScript) opens a **Bidirectional WebSocket Stream** directly to the Python Agent Service. This bypasses the REST layer and ensures low latency (NFR4) and interruption support by leveraging the Google ADK's native live processing capabilities.

-----

## 3\. Data Models and API Specification

### Data Models

The system relies on a few core entities to drive the agent's memory and logic. These models will be defined as **TypeScript Interfaces** in the `packages/shared` directory and implemented as tables/files in the local DB.

| Model Name        | Purpose                                                         | Key Attributes                                                                               | Relationships                                   |
| :---------------- | :-------------------------------------------------------------- | :------------------------------------------------------------------------------------------- | :---------------------------------------------- |
| **User**          | System user and personalization profile.                        | `user_id`, `name`, `learning_interests` (used by A3).                                        | One-to-Many with `HealthLog`, `MemoryContext`.  |
| **HealthLog**     | Simulated data used by the Vibe Agent (A1).                     | `timestamp`, `sleep_hours`, `screen_time`, `imbalance_score`.                                | One-to-One with `MemoryContext` (as a trigger). |
| **MemoryContext** | **Long-Term Memory** storage for the Vibe Agent.                | `context_id`, `agent_id`, `data_source_id`, `summary_text`, `embedding_vector` (conceptual). | Linked via `user_id`.                           |
| **ToolActionLog** | Logs all executed tool calls (F2, F3) for observability (NFR3). | `tool_name`, `timestamp`, `input_query`, `output_result`.                                    | Linked via `user_id`.                           |

### Core API Endpoints (Internal)

These define the communication contract between the TypeScript UI and the Python Orchestrator.

| Endpoint           | Method  | Purpose                                                      | Agent Involved                                                         |
| :----------------- | :------ | :----------------------------------------------------------- | :--------------------------------------------------------------------- |
| `/api/chat`        | POST    | Main conversational endpoint (text and initiation of voice). | [cite\_start]**Orchestrator** (delegates to A1, A2, or A3)[cite: 998]. |
| `/api/live-stream` | WS      | **WebSocket** endpoint for real-time voice audio streaming.  | **Orchestrator** (routes to ADK Live).                                 |
| `/api/config/user` | GET/PUT | Retrieves/updates user profile, goals, and simulated data.   | Data Access Layer.                                                     |

-----

## 4\. Components

### [cite\_start]Agent Monolith Components (Python) [cite: 998, 999]

| Component Name           | Responsibility                                                                                 | Agentic Demonstration                                            |
| :----------------------- | :--------------------------------------------------------------------------------------------- | :--------------------------------------------------------------- |
| **Orchestrator**         | [cite\_start]**Intent Routing** and session context management (Short-Term Memory)[cite: 998]. | [cite\_start]Clean **Agent Context Switching** (FR5)[cite: 998]. |
| **Vibe Agent (A1)**      | **Proactive Balance Check (F1)** and **Long-Term Memory** retrieval.                           | **ADK Memory SDK** integration (NFR2).                           |
| **Planner Agent (A2)**   | **Mandatory Check-up Scheduler (F2)**.                                                         | **Tool Calling** (simulated calendar/to-do).                     |
| **Knowledge Agent (A3)** | **Personalized Learning Digest (F3)**.                                                         | **Structured Output** and **Tool Calling** (simulated search).   |
| **Tool Calling Layer**   | Wrapper for all **mocked** external services.                                                  | Standardized **Tool Use**.                                       |

-----

## 5\. Security and Development Workflow

### Security and Observability (NFR3)

  * **Agent Observability (NFR3):** The Python Agent Service will leverage **Google ADK's built-in logging** and evaluation features, capturing every ADK decision, tool call, and latency metric for the capstone demo and analysis.
  * **PII Handling:** Since data is simulated/local, PII risk is low. [cite\_start]All data access must go through the **Data Access Layer**[cite: 975].
  * **Authentication:** Mocked Authentication/Authorization is sufficient for capstone demonstration.

### Unified Project Structure (Monorepo)

The structure uses `npm workspaces` for configuration simplicity, managing the two distinct language services.

```text
project-root/
├── apps/
│   ├── api/                    # Python Agent Service (FastAPI/Flask)
│   │   ├── src/                # Agent Modules (A1, A2, A3)
│   │   └── api.py              # Main entry point/orchestrator
│   └── web/                    # Next.js Frontend (TS)
│       ├── components/         # UI components
│       └── pages/              # Routing/UI views
├── packages/
│   ├── shared/                 # Shared TypeScript Interfaces/Types (DB/API/Health Models)
│   └── config/                 # Unified ESlint/Prettier setup
├── infrastructure/             # Dockerfile for simple local deployment (conceptual)
├── docs/                       # Project Brief, PRD, Architecture Document (THIS FILE)
└── package.json                # Root Monorepo configuration
```

### Development Workflow

1.  **Local Setup:** Requires Node.js, Python, and the Google ADK Python SDK installation.
2.  **Build:** Node.js/npm scripts are used to manage the TypeScript FE and the Python BE dependencies.
3.  **Testing:** Focus on **Unit Tests** (Python/Jest) and **Integration Tests** (testing the internal REST/WebSocket contracts between the TS and Python services).

-----

The **Fullstack Architecture Document** is now complete, incorporating all planning and constraints. The next phase is development—translating this blueprint into code based on the approved stories.

**Would you like me to use the Product Owner (Sarah) to perform the final validation of this document against the PO Master Checklist before starting implementation?**