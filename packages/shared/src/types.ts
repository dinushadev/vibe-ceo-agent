// ============================================================================
// Data Models
// ============================================================================

export interface User {
    user_id: string;
    name: string;
    learning_interests: string[];
    created_at: string;
    updated_at: string;
}

export interface HealthLog {
    log_id: string;
    user_id: string;
    timestamp: string;
    sleep_hours: number;
    screen_time: number;
    imbalance_score: number;
    notes?: string;
}

export interface MemoryContext {
    context_id: string;
    user_id: string;
    agent_id: string;
    data_source_id?: string;
    summary_text: string;
    embedding_vector?: number[];
    timestamp: string;
    metadata?: Record<string, any>;
}

export interface ToolActionLog {
    log_id: string;
    user_id: string;
    tool_name: string;
    timestamp: string;
    input_query: string;
    output_result: string;
    success: boolean;
    execution_time_ms: number;
}

// ============================================================================
// Agent Types
// ============================================================================

export enum AgentType {
    VIBE = 'vibe',
    PLANNER = 'planner',
    KNOWLEDGE = 'knowledge',
}

export interface AgentMessage {
    agent_type: AgentType;
    content: string;
    timestamp: string;
    metadata?: {
        memory_used?: boolean;
        tool_called?: string;
        proactive?: boolean;
    };
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface ChatRequest {
    user_id: string;
    message: string;
    context?: {
        agent_preference?: AgentType;
        session_id?: string;
    };
}

export interface ChatResponse {
    agent_type: AgentType;
    response: string;
    timestamp: string;
    metadata?: {
        memory_retrieved?: MemoryContext[];
        tools_used?: string[];
        latency_ms: number;
    };
}

export interface UserConfigRequest {
    name?: string;
    learning_interests?: string[];
}

export interface UserConfigResponse {
    user: User;
    health_logs: HealthLog[];
    memory_summary: {
        total_contexts: number;
        recent_interactions: number;
    };
}

// ============================================================================
// WebSocket Protocol Types
// ============================================================================

export enum WebSocketMessageType {
    AUDIO_CHUNK = 'audio_chunk',
    TRANSCRIPT = 'transcript',
    AGENT_RESPONSE = 'agent_response',
    ERROR = 'error',
    CONNECTION_ACK = 'connection_ack',
    PING = 'ping',
    PONG = 'pong',
}

export interface WebSocketMessage {
    type: WebSocketMessageType;
    payload: any;
    timestamp: string;
}

export interface AudioChunkMessage extends WebSocketMessage {
    type: WebSocketMessageType.AUDIO_CHUNK;
    payload: {
        audio_data: string; // base64 encoded
        format: 'pcm' | 'opus' | 'mp3';
        sample_rate: number;
    };
}

export interface TranscriptMessage extends WebSocketMessage {
    type: WebSocketMessageType.TRANSCRIPT;
    payload: {
        text: string;
        is_final: boolean;
    };
}

export interface AgentResponseMessage extends WebSocketMessage {
    type: WebSocketMessageType.AGENT_RESPONSE;
    payload: {
        agent_type: AgentType;
        text: string;
        audio_data?: string; // base64 encoded response audio
    };
}

// ============================================================================
// Tool Types
// ============================================================================

export interface CalendarEvent {
    event_id: string;
    title: string;
    description: string;
    start_time: string;
    end_time: string;
    location?: string;
}

export interface SearchResult {
    title: string;
    url: string;
    snippet: string;
    relevance_score: number;
}

export interface LearningDigest {
    topic: string;
    summary: string;
    key_points: string[];
    sources: SearchResult[];
    generated_at: string;
}

// ============================================================================
// Error Types
// ============================================================================

export interface APIError {
    error: string;
    message: string;
    code: string;
    timestamp: string;
}
