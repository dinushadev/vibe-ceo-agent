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
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 animate-fade-in-up`}>
            <div className={`flex gap-3 max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground'
                    } text-sm font-medium shadow-sm`}>
                    {isUser ? '👤' : agentIcon}
                </div>

                {/* Message bubble */}
                <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
                    <div className={`rounded-2xl px-5 py-3 shadow-sm ${isUser
                        ? 'bg-primary text-primary-foreground rounded-tr-sm'
                        : 'glass-card text-foreground rounded-tl-sm'
                        }`}>
                        <p className="text-sm leading-relaxed whitespace-pre-wrap font-normal">{message.content}</p>

                        {/* Metadata for agent messages */}
                        {!isUser && message.metadata && (
                            <div className="mt-3 pt-2 border-t border-border/50">
                                {message.metadata.tools_used && message.metadata.tools_used.length > 0 && (
                                    <div className="flex items-center gap-2 text-[10px] text-muted-foreground uppercase tracking-wider">
                                        <span className="font-semibold">Tools:</span>
                                        <span>{message.metadata.tools_used.join(', ')}</span>
                                    </div>
                                )}
                                {message.metadata.latency_ms && (
                                    <div className="text-[10px] text-muted-foreground mt-1 font-mono opacity-70">
                                        {message.metadata.latency_ms}ms
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Timestamp */}
                    <div className="text-[10px] text-muted-foreground mt-1 px-1 opacity-70">
                        {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                </div>
            </div>
        </div>
    );
}
