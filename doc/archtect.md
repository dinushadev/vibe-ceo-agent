# 🏗️ The Personal Vibe CEO System: Fullstack Architecture Document

### Version 2.0 (Native Audio & Agent-as-a-Tool)

| Change                   | Date             | Version | Description                                                          | Author          |
| :----------------------- | :--------------- | :------ | :------------------------------------------------------------------- | :-------------- |
| Initial draft            | Nov 24, 2025     | 1.0     | Polyglot Monolith, ADK integration.                                  | Architect       |
| **Native Audio Upgrade** | **Nov 27, 2025** | **2.0** | **Shift to Gemini 2.5 Flash Native Audio, Agent-as-a-Tool pattern.** | **Antigravity** |

## 1. High Level Architecture

The system has evolved from a traditional "Python Orchestrator" to an **AI-Native Orchestration** model. The core "brain" is no longer a Python script but the **Gemini 2.5 Flash** model itself, interacting directly with the user via **Native Audio** (Multimodal Live API).

| Feature           | Design Decision                     | Rationale                                                                                   |
| :---------------- | :---------------------------------- | :------------------------------------------------------------------------------------------ |
| **Core Brain**    | **Gemini 2.5 Flash (Native Audio)** | Lowest latency, highest emotional intelligence ("Vibe"), and natural interruption handling. |
| **Orchestration** | **Model-Driven (LLM Router)**       | The model hears audio and decides which tool to call. No rigid Python routing logic.        |
| **Sub-Agents**    | **Agent-as-a-Tool**                 | Planner and Knowledge agents are "Thinking Tools" invoked by the Orchestrator.              |
| **Frontend**      | **Next.js + WebSocket**             | Establishes a direct audio stream to the backend, which proxies to Gemini.                  |

### High Level Architecture Diagram

```mermaid
graph TD
    User[User: Voice/Chat] -->|WebSocket Audio Stream| FE[Frontend: Next.js]
    FE -->|Bidi Stream| BE[Backend: Python VoiceService]
    
    subgraph "AI-Native Core"
        BE <-->|Native Audio API| Model[Gemini 2.0 Flash (Orchestrator + Vibe Persona)]
    end
    
    subgraph "Intelligent Tools (Agent-as-a-Tool)"
        Model -.->|Function Call| Planner[Planner Agent (Tool)]
        Model -.->|Function Call| Knowledge[Knowledge Agent (Tool)]
        
        Planner -->|Reasoning| P_LLM[Planner LLM (Text)]
        Knowledge -->|Reasoning| K_LLM[Knowledge LLM (Text)]
    end
    
    Planner -->|Read/Write| DB[(Database / Calendar API)]
    Knowledge -->|Search| Web[Search API]
    
    style Model fill:#ff9999,stroke:#333,stroke-width:2px
    style Planner fill:#99ccff,stroke:#333
    style Knowledge fill:#99ccff,stroke:#333
```

-----

## 2. Technology Stack & Protocols

| Category            | Technology                 | Purpose                                                                  |
| :------------------ | :------------------------- | :----------------------------------------------------------------------- |
| **AI Model**        | **Gemini 2.0 Flash**       | The "Vibe CEO". Handles Audio I/O, personality, and orchestration.       |
| **API Protocol**    | **WebSocket (Bidi)**       | Real-time audio streaming between Client <-> Server <-> Model.           |
| **Agent Framework** | **Google ADK (GenAI SDK)** | Manages the model connection, tools, and function calling.               |
| **Backend**         | **FastAPI (Python)**       | Hosts the WebSocket endpoint and defines the "Tools" (Python functions). |
| **Frontend**        | **Next.js (React)**        | Captures microphone input, plays audio response.                         |

### The "Vibe" Transformation
*   **Old Way:** `User -> STT -> Text Router -> Vibe Agent -> TTS -> User`
*   **New Way:** `User -> Gemini 2.0 (Vibe Persona) -> User`
    *   The **Vibe Agent** is now the *default persona* of the Orchestrator. It is not a separate module.

-----

## 3. Agent-as-a-Tool Design

Instead of simple API wrappers, our tools are **Intelligent Agents**.

### 3.1. The Planner Tool (Agent)
*   **Trigger:** User asks to schedule, plan, or organize.
*   **Input:** User's vague request ("Fix my messy schedule") + Calendar Data + Health Logs.
*   **Internal Logic:** Spins up a text-based LLM to analyze the schedule against well-being goals.
*   **Output:** A strategic plan or a specific calendar action.
*   **Example:**
    > **Orchestrator:** "Hey Planner, the user is stressed. Look at their calendar."
    > **Planner Tool:** "I see 4 back-to-back meetings. I recommend moving the 3 PM sync to tomorrow. Shall I do that?"

### 3.2. The Knowledge Tool (Agent)
*   **Trigger:** User asks to learn, research, or explain.
*   **Input:** Research topic.
*   **Internal Logic:** Performs Google Search, reads pages, synthesizes a summary.
*   **Output:** A concise briefing.

-----

## 4. Data Models

| Model             | Purpose                                                           |
| :---------------- | :---------------------------------------------------------------- |
| **User**          | Profile and preferences.                                          |
| **HealthLog**     | Sleep, steps, stress data (used by Planner to optimize schedule). |
| **MemoryContext** | Long-term memory injected into the Orchestrator's system prompt.  |

-----

## 5. Implementation Strategy

1.  **Refactor `VoiceService`:**
    *   Switch to `google-genai` Native Audio API.
    *   Define `tools` list configuration.
    *   Set `system_instruction` to embody the "Vibe CEO" persona.

2.  **Implement Tools:**
    *   `src/tools/planner_tool.py`: The "Thinking" function for scheduling.
    *   `src/tools/knowledge_tool.py`: The "Thinking" function for research.

3.  **Frontend Update:**
    *   Ensure `useVoice` hook handles the raw PCM audio format expected by the new backend.