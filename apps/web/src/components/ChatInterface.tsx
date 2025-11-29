/**
 * Chat Interface Component
 * Main chat display with messages
 */

import React, { useEffect, useRef } from 'react';
import { Message } from '@/hooks/useChat';
import ChatMessage from './ChatMessage';

interface ChatInterfaceProps {
    messages: Message[];
    isLoading: boolean;
}

export default function ChatInterface({ messages, isLoading }: ChatInterfaceProps) {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 scroll-smooth">
            {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center px-4 animate-fade-in-up">
                    <div className="text-6xl mb-6 filter drop-shadow-lg">🤖</div>
                    <h2 className="text-2xl font-semibold text-foreground mb-3 tracking-tight">
                        Welcome to Personal Vibe CEO
                    </h2>
                    <p className="text-muted-foreground max-w-md mb-8 leading-relaxed">
                        I'm here to help with your emotional well-being, task planning, and learning.
                        Choose a quick action below or just start chatting!
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-3xl">
                        <div className="glass-card p-6 rounded-2xl hover:bg-white/50 transition-all duration-300 cursor-pointer group">
                            <div className="text-3xl mb-3 group-hover:scale-110 transition-transform duration-300">💜</div>
                            <h3 className="font-semibold text-foreground mb-1">Vibe Agent</h3>
                            <p className="text-xs text-muted-foreground">
                                Check in on your emotional and physical well-being
                            </p>
                        </div>

                        <div className="glass-card p-6 rounded-2xl hover:bg-white/50 transition-all duration-300 cursor-pointer group">
                            <div className="text-3xl mb-3 group-hover:scale-110 transition-transform duration-300">📅</div>
                            <h3 className="font-semibold text-foreground mb-1">Planner Agent</h3>
                            <p className="text-xs text-muted-foreground">
                                Schedule appointments and manage your tasks
                            </p>
                        </div>

                        <div className="glass-card p-6 rounded-2xl hover:bg-white/50 transition-all duration-300 cursor-pointer group">
                            <div className="text-3xl mb-3 group-hover:scale-110 transition-transform duration-300">📚</div>
                            <h3 className="font-semibold text-foreground mb-1">Knowledge Agent</h3>
                            <p className="text-xs text-muted-foreground">
                                Curate personalized learning content
                            </p>
                        </div>
                    </div>
                </div>
            ) : (
                <>
                    {messages.map((message) => (
                        <ChatMessage key={message.id} message={message} />
                    ))}
                    {isLoading && (
                        <div className="flex justify-start mb-4 animate-fade-in-up">
                            <div className="flex gap-3 max-w-[80%]">
                                <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-secondary text-secondary-foreground shadow-sm">
                                    🤖
                                </div>
                                <div className="glass-card rounded-2xl rounded-tl-none px-4 py-3 shadow-sm">
                                    <div className="flex gap-1.5">
                                        <div className="w-1.5 h-1.5 bg-muted-foreground/50 rounded-full animate-bounce"></div>
                                        <div className="w-1.5 h-1.5 bg-muted-foreground/50 rounded-full animate-bounce delay-75"></div>
                                        <div className="w-1.5 h-1.5 bg-muted-foreground/50 rounded-full animate-bounce delay-150"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </>
            )}
        </div>
    );
}
