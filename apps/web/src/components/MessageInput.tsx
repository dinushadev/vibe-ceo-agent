/**
 * Message Input Component
 * Handles user message input and submission
 */

import React, { useState, FormEvent, KeyboardEvent } from 'react';

interface MessageInputProps {
    onSendMessage: (message: string) => void;
    isLoading: boolean;
}

export default function MessageInput({ onSendMessage, isLoading }: MessageInputProps) {
    const [message, setMessage] = useState('');

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (message.trim() && !isLoading) {
            onSendMessage(message.trim());
            setMessage('');
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex gap-3 items-end">
                <div className="flex-1">
                    <textarea
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Type your message... (Shift+Enter for new line)"
                        disabled={isLoading}
                        rows={1}
                        className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl 
                     text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400
                     focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400
                     disabled:opacity-50 disabled:cursor-not-allowed resize-none
                     transition-all duration-200"
                        style={{ minHeight: '52px', maxHeight: '120px' }}
                        onInput={(e) => {
                            const target = e.target as HTMLTextAreaElement;
                            target.style.height = '52px';
                            target.style.height = target.scrollHeight + 'px';
                        }}
                    />
                </div>

                <button
                    type="submit"
                    disabled={!message.trim() || isLoading}
                    className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-medium rounded-xl
                   hover:from-indigo-600 hover:to-purple-600 
                   disabled:opacity-50 disabled:cursor-not-allowed
                   transition-all duration-200 shadow-lg hover:shadow-xl
                   flex items-center gap-2 flex-shrink-0"
                >
                    {isLoading ? (
                        <>
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            <span>Sending...</span>
                        </>
                    ) : (
                        <>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                            <span>Send</span>
                        </>
                    )}
                </button>
            </div>

            {/* Quick actions */}
            <div className="flex gap-2 mt-3 flex-wrap">
                <button
                    type="button"
                    onClick={() => setMessage("I'm feeling stressed and overwhelmed")}
                    disabled={isLoading}
                    className="px-3 py-1 text-sm bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-900/50 transition-colors"
                >
                    💜 Check my vibe
                </button>
                <button
                    type="button"
                    onClick={() => setMessage("Schedule a doctor appointment next week")}
                    disabled={isLoading}
                    className="px-3 py-1 text-sm bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
                >
                    📅 Schedule appointment
                </button>
                <button
                    type="button"
                    onClick={() => setMessage("Create a learning digest about AI")}
                    disabled={isLoading}
                    className="px-3 py-1 text-sm bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-lg hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors"
                >
                    📚 Learning digest
                </button>
            </div>
        </form>
    );
}
