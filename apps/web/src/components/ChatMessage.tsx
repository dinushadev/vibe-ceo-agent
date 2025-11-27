/**
 * Chat Message Component
 * Displays individual messages in the chat
 */

import React from 'react';
import { Message } from '@/hooks/useChat';
import { AgentType } from '@vibe-ceo/shared';

interface ChatMessageProps {
    message: Message;
}

const agentColors = {
    [AgentType.VIBE]: 'bg-gradient-to-r from-purple-500 to-pink-500',
    [AgentType.PLANNER]: 'bg-gradient-to-r from-blue-500 to-cyan-500',
    [AgentType.KNOWLEDGE]: 'bg-gradient-to-r from-green-500 to-emerald-500',
};

const agentIcons = {
    [AgentType.VIBE]: '💜',
    [AgentType.PLANNER]: '📅',
    [AgentType.KNOWLEDGE]: '📚',
};

export default function ChatMessage({ message }: ChatMessageProps) {
    const isUser = message.role === 'user';
    const agentColor = message.agentType ? agentColors[message.agentType] : 'bg-gray-600';
    const agentIcon = message.agentType ? agentIcons[message.agentType] : '🤖';

    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fade-in`}>
            <div className={`flex gap-3 max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                {/* Avatar */}
                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-gradient-to-r from-indigo-500 to-purple-500' : agentColor
                    } text-white font-semibold shadow-lg`}>
                    {isUser ? '👤' : agentIcon}
                </div>

                {/* Message bubble */}
                <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
                    <div className={`rounded-2xl px-4 py-3 shadow-md ${isUser
                            ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white'
                            : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600'
                        }`}>
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

                        {/* Metadata for agent messages */}
                        {!isUser && message.metadata && (
                            <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
                                {message.metadata.tools_used && message.metadata.tools_used.length > 0 && (
                                    <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                                        <span className="font-medium">🔧 Tools:</span>
                                        <span>{message.metadata.tools_used.join(', ')}</span>
                                    </div>
                                )}
                                {message.metadata.latency_ms && (
                                    <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                                        ⚡ {message.metadata.latency_ms}ms
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Timestamp */}
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 px-2">
                        {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                </div>
            </div>
        </div>
    );
}
