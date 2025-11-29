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
        <div className="relative">
            <form onSubmit={handleSubmit} className="glass-card rounded-[2rem] p-2 shadow-lg border border-white/20">
                <div className="flex gap-2 items-end">
                    <div className="flex-1">
                        <textarea
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Type a message..."
                            disabled={isLoading}
                            rows={1}
                            className="w-full px-6 py-3.5 bg-transparent border-none focus:ring-0 text-foreground placeholder-muted-foreground/70 resize-none max-h-[120px] min-h-[52px]"
                            style={{ minHeight: '52px' }}
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
                        className="p-3 bg-primary text-primary-foreground rounded-full hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md mb-1 mr-1 flex-shrink-0"
                    >
                        {isLoading ? (
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                            <svg className="w-5 h-5 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        )}
                    </button>
                </div>
            </form>

            {/* Quick actions */}
            <div className="flex gap-2 mt-4 justify-center flex-wrap opacity-0 hover:opacity-100 transition-opacity duration-300">
                <button
                    type="button"
                    onClick={() => setMessage("I'm feeling stressed and overwhelmed")}
                    disabled={isLoading}
                    className="px-4 py-1.5 text-xs font-medium bg-secondary/50 hover:bg-secondary text-secondary-foreground rounded-full transition-colors backdrop-blur-sm"
                >
                    💜 Check my vibe
                </button>
                <button
                    type="button"
                    onClick={() => setMessage("Schedule a doctor appointment next week")}
                    disabled={isLoading}
                    className="px-4 py-1.5 text-xs font-medium bg-secondary/50 hover:bg-secondary text-secondary-foreground rounded-full transition-colors backdrop-blur-sm"
                >
                    📅 Schedule appointment
                </button>
                <button
                    type="button"
                    onClick={() => setMessage("Create a learning digest about AI")}
                    disabled={isLoading}
                    className="px-4 py-1.5 text-xs font-medium bg-secondary/50 hover:bg-secondary text-secondary-foreground rounded-full transition-colors backdrop-blur-sm"
                >
                    📚 Learning digest
                </button>
            </div>
        </div>
    );
}
