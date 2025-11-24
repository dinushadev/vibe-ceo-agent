
# 🚀 The Personal Vibe CEO System: Product Requirements Document (PRD)

## 1. Goals and Background Context

### Goals
* Successfully implement and demonstrate three core agent types (Vibe, Planner, Knowledge) with functional tool-calling and memory access.
* Achieve a high level of user-perceived usefulness across emotional, task, and knowledge domains.
* Design the system architecture for extensibility and showcase advanced agentic features (memory, tool-calling, multi-agent coordination) for the capstone project.

### Background Context
The **Personal Vibe CEO** system is a capstone project focused on demonstrating advanced multi-agent architecture. It moves beyond reactive systems by using **proactive, context-aware digital oversight** to assist with personal well-being and logistics. The system must support both **voice and chat interfaces** (FR2) and will leverage the **Google ADK** (NFR1) for memory/observability features, using simulated APIs for constrained implementation.

---

## 2. Requirements

### 2.1 Functional Requirements (FR)
| ID      | Requirement                                                                                                                                                         | Agent / Feature             |
| :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------------------------- |
| **FR1** | The **Vibe Agent** MUST initiate a conversation (Proactive Check-In) when simulated data indicates an imbalance, recalling specific historical context from memory. | A1: Proactive Balance Check |
| **FR2** | The system MUST accept conversational input via both **text (chat)** and **voice interfaces**.                                                                      | UI/Interface                |
| **FR3** | The **Planner Agent** MUST successfully execute a simulated **Tool Call** to schedule a task in an external (mocked) calendar/to-do service.                        | A2: Check-up Scheduler      |
| **FR4** | The **Knowledge Agent** MUST use a simulated **Tool Call** (Search API) to retrieve, process, and summarize external data into a "Learning Digest."                 | A3: Learning Digest         |
| **FR5** | The system MUST be able to switch conversation context cleanly between the three agents (Vibe, Planner, Knowledge) via user command or implied context.             | Orchestrator                |
| **FR6** | The Vibe Agent's output MUST include empathetic language and demonstrate awareness of the user's emotional state based on simulated inputs.                         | A1: Proactive Balance Check |

### 2.2 Non-Functional Requirements (NFR)
| ID       | Requirement                                                                                                                           | Constraint Type      |
| :------- | :------------------------------------------------------------------------------------------------------------------------------------ | :------------------- |
| **NFR1** | The agent communication framework MUST be built using the **Google ADK**.                                                             | Technical / ADK      |
| **NFR2** | The architecture MUST explicitly use **Google ADK's memory features** for managing the Vibe Agent's long-term context.                | Technical / ADK      |
| **NFR3** | The system MUST leverage **Google ADK's observability and evaluation features** for logging and tracking agent performance/decisions. | Technical / ADK      |
| **NFR4** | The conversational response time (latency) for all agents MUST be below **3 seconds**.                                                | Performance          |
| **NFR5** | The **Frontend** must be implemented in **TypeScript**; the **Agent Monolith** must be implemented in **Python** (Polyglot).          | Technical / Language |

---

## 3. User Interface Design Goals

| Element               | Goal                                                                                                                                                                                                                                                  |
| :-------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Overall UX Vision** | **Proactive and Personalized**; the system must feel like a guiding presence, prioritizing **Clarity over Cleverness**.                                                                                                                               |
| **Key Interaction**   | **Proactive Initiation (F1)**: Agent starts the conversation when an event is detected. Structured outputs (O2, O3) must be clean and visually distinct.                                                                                              |
| **Core Screens**      | **1. Main Conversational Interface:** Accommodates chat log, text input, and a clearly visible **Voice Input Toggle**. **2. Agent Status Dashboard (Conceptual):** A conceptual view that visually indicates which agent is active (for demo impact). |
| **Platforms**         | **Web Responsive**.                                                                                                                                                                                                                                   |
| **Accessibility**     | Basic usability and text clarity; formal WCAG compliance out of scope.                                                                                                                                                                                |

---

## 4. Technical Assumptions

| Element                  | Preference                                                         | Rationale                                                                       |
| :----------------------- | :----------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| **Repository Structure** | **Monorepo** (npm Workspaces).                                     | Simplifies development, tooling, and sharing of shared TypeScript types.        |
| **Service Architecture** | **Polyglot Monolith** (TS UI $\rightarrow$ Python Agent).          | Preserves modern UI while meeting mandatory ADK Python constraint (NFR1).       |
| **Database/Tools**       | SQLite / Simulated (Mocked) APIs.                                  | Simplifies setup, minimizes hosting complexity, and controls time scope.        |
| **Voice Protocol**       | **Bidirectional WebSocket Streaming**.                             | Required for real-time, low-latency voice and interruption support (FR2, NFR4). |
| **Testing Focus**        | Unit + Integration Testing (focus on service contract validation). | Ensures agent logic and polyglot communication is robust.                       |

---

## 5. Epic List

The project is structured around a **Single Epic** to ensure all work remains focused on delivering the capstone MVP.

### Epic 1: Foundation & Agent Trio MVP

| Story ID | Story Title                              | Core Focus / Agent          | Dependencies       |
| :------- | :--------------------------------------- | :-------------------------- | :----------------- |
| **1.1**  | Project Scaffolding & ADK Integration    | Infrastructure / Backend    | None               |
| **1.2**  | **Polyglot Service Contract Validation** | Testing / Infrastructure    | **1.1**            |
| **1.3**  | Vibe Agent: Memory & Proactive Logic     | A1: Proactive Balance Check | 1.1, 1.2           |
| **1.4**  | Planner Agent: Tool-Calling Setup        | A2: Check-up Scheduler      | 1.1, 1.2           |
| **1.5**  | Knowledge Agent: Curation Tool Setup     | A3: Learning Digest         | 1.1, 1.2           |
| **1.6**  | Unified Conversational Interface         | UI/UX / Frontend            | 1.1, 1.3, 1.4, 1.5 |

***
**The Product Requirements Document is complete and ready for Architect and Development execution.**
***