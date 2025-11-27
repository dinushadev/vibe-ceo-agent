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
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
            {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center px-4">
                    <div className="text-6xl mb-4">🤖</div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                        Welcome to Personal Vibe CEO
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400 max-w-md mb-6">
                        I'm here to help with your emotional well-being, task planning, and learning.
                        Choose a quick action below or just start chatting!
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-3xl">
                        <div className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl border border-purple-200 dark:border-purple-700">
                            <div className="text-3xl mb-2">💜</div>
                            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Vibe Agent</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Check in on your emotional and physical well-being
                            </p>
                        </div>

                        <div className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 rounded-xl border border-blue-200 dark:border-blue-700">
                            <div className="text-3xl mb-2">📅</div>
                            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Planner Agent</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Schedule appointments and manage your tasks
                            </p>
                        </div>

                        <div className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl border border-green-200 dark:border-green-700">
                            <div className="text-3xl mb-2">📚</div>
                            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Knowledge Agent</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
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
                        <div className="flex justify-start mb-4">
                            <div className="flex gap-3 max-w-[80%]">
                                <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 bg-gray-600 text-white">
                                    🤖
                                </div>
                                <div className="bg-white dark:bg-gray-700 rounded-2xl px-4 py-3 shadow-md border border-gray-200 dark:border-gray-600">
                                    <div className="flex gap-2">
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
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
