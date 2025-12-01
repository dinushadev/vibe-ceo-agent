'use client';

import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { useVoice } from '../hooks/useVoice';

export function VoiceInterface() {
    const { user } = useAuth();
    const {
        isListening,
        isProcessing,
        transcript,
        volume,
        startRecording,
        stopRecording,
        error
    } = useVoice(user?.user_id);

    return (
        <div className="fixed bottom-8 right-8 z-50 flex flex-col items-end gap-4">
            {/* Transcript Bubble */}
            {(transcript || isProcessing) && (
                <div className="glass-card p-4 rounded-2xl shadow-lg max-w-xs mb-2 border border-white/20 animate-in fade-in slide-in-from-bottom-4 backdrop-blur-md">
                    <p className="text-sm text-foreground font-medium">
                        {transcript}
                        {isProcessing && <span className="animate-pulse">...</span>}
                    </p>
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-600 px-4 py-2 rounded-lg text-sm mb-2 backdrop-blur-sm">
                    {error}
                </div>
            )}

            {/* Mic Button Container */}
            <div className="flex flex-col items-center gap-2">
                <div className="relative flex items-center justify-center">
                    {/* Pulsing Ring */}
                    {isListening && (
                        <div
                            className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-red-500/20 transition-all duration-75 ease-out pointer-events-none"
                            style={{
                                width: `${64 + (volume * 100)}px`,
                                height: `${64 + (volume * 100)}px`,
                            }}
                        />
                    )}

                    <button
                        onClick={isListening ? stopRecording : startRecording}
                        className={`
                            relative z-10 flex items-center justify-center w-14 h-14 rounded-full shadow-lg transition-all duration-300 backdrop-blur-md border border-white/10
                            ${isListening
                                ? 'bg-red-500 text-white hover:bg-red-600'
                                : 'bg-primary text-primary-foreground hover:opacity-90 hover:scale-105'
                            }
                        `}
                        aria-label={isListening ? "Stop listening" : "Start listening"}
                    >
                        {isListening ? (
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-6 h-6">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 7.5A2.25 2.25 0 017.5 5.25h9a2.25 2.25 0 012.25 2.25v9a2.25 2.25 0 01-2.25 2.25h-9a2.25 2.25 0 01-2.25-2.25v-9z" />
                            </svg>
                        ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-6 h-6">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
                            </svg>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
