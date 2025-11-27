/**
 * Custom hook for managing chat state
 */

import { useState, useCallback } from 'react';
import { apiService } from '@/services/api';
import { AgentType } from '@vibe-ceo/shared';

export interface Message {
    id: string;
    role: 'user' | 'agent';
    content: string;
    agentType?: AgentType;
    timestamp: string;
    metadata?: any;
}

export function useChat(userId: string) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [currentAgent, setCurrentAgent] = useState<AgentType | null>(null);

    const sendMessage = useCallback(async (content: string, agentPreference?: AgentType) => {
        if (!content.trim()) return;

        // Add user message to chat
        const userMessage: Message = {
            id: `user-${Date.now()}`,
            role: 'user',
            content,
            timestamp: new Date().toISOString(),
        };

        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
        setError(null);

        try {
            // Send to backend
            const response = await apiService.sendMessage(userId, content, agentPreference);

            // Add agent response
            const agentMessage: Message = {
                id: `agent-${Date.now()}`,
                role: 'agent',
                content: response.response,
                agentType: response.agent_type as AgentType,
                timestamp: response.timestamp,
                metadata: response.metadata,
            };

            setMessages(prev => [...prev, agentMessage]);
            setCurrentAgent(response.agent_type as AgentType);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
            setError(errorMessage);

            // Add error message to chat
            const errorMsg: Message = {
                id: `error-${Date.now()}`,
                role: 'agent',
                content: `Sorry, I encountered an error: ${errorMessage}`,
                timestamp: new Date().toISOString(),
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    }, [userId]);

    const clearMessages = useCallback(() => {
        setMessages([]);
        setCurrentAgent(null);
        setError(null);
    }, []);

    return {
        messages,
        isLoading,
        error,
        currentAgent,
        sendMessage,
        clearMessages,
    };
}
