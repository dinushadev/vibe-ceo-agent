/**
 * API Service for Personal Vibe CEO System
 * Handles all communication with the backend
 */

import { AgentType, ChatRequest, ChatResponse, UserConfigResponse } from '@vibe-ceo/shared';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIService {
    /**
     * Send a chat message to the backend
     */
    async sendMessage(
        userId: string,
        message: string,
        agentPreference?: AgentType
    ): Promise<ChatResponse> {
        const request: ChatRequest = {
            user_id: userId,
            message,
            context: agentPreference ? { agent_preference: agentPreference } : {}
        };

        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.json();
    }

    /**
     * Get user configuration
     */
    async getUserConfig(userId: string): Promise<UserConfigResponse> {
        const response = await fetch(
            `${API_BASE_URL}/api/config/user?user_id=${userId}`,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            }
        );

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.json();
    }

    /**
     * Check for proactive messages
     */
    async checkProactive(userId: string): Promise<{ triggered: boolean; message: any }> {
        const response = await fetch(
            `${API_BASE_URL}/api/proactive-check?user_id=${userId}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            }
        );

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.json();
    }

    /**
     * Health check
     */
    async healthCheck(): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/`);

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.json();
    }
}

// Export singleton instance
export const apiService = new APIService();
