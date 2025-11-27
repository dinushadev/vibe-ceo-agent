'use client';

/**
 * Main Page - Personal Vibe CEO System
 * Integrates all components for the chat interface
 */

import { useState } from 'react';
import { useChat } from '@/hooks/useChat';
import AgentStatus from '@/components/AgentStatus';
import ChatInterface from '@/components/ChatInterface';
import MessageInput from '@/components/MessageInput';
import { VoiceInterface } from '@/components/VoiceInterface';

const USER_ID = 'demo-user-001'; // Demo user from seeded database

export default function Home() {
  const { messages, isLoading, currentAgent, sendMessage, clearMessages } = useChat(USER_ID);
  const [darkMode, setDarkMode] = useState(false);

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10 shadow-sm">
          <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="text-3xl">🤖</div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  Personal Vibe CEO
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Your AI-powered well-being companion
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                aria-label="Toggle dark mode"
              >
                {darkMode ? '🌞' : '🌙'}
              </button>

              {messages.length > 0 && (
                <button
                  onClick={clearMessages}
                  className="px-4 py-2 text-sm bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                >
                  Clear Chat
                </button>
              )}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-6xl mx-auto px-4 py-6 h-[calc(100vh-80px)] flex flex-col">
          {/* Agent Status */}
          <AgentStatus currentAgent={currentAgent} isLoading={isLoading} />

          {/* Chat Container */}
          <div className="flex-1 bg-white dark:bg-gray-800 rounded-xl shadow-xl flex flex-col overflow-hidden border border-gray-200 dark:border-gray-700 mb-4">
            <ChatInterface messages={messages} isLoading={isLoading} />
          </div>

          {/* Message Input */}
          <MessageInput onSendMessage={sendMessage} isLoading={isLoading} />
        </main>

        {/* Footer */}
        <footer className="text-center py-4 text-sm text-gray-500 dark:text-gray-400">
          <p>Personal Vibe CEO System • Capstone Project • Powered by Google ADK</p>
        </footer>

        {/* Voice Interface */}
        <VoiceInterface />
      </div>
    </div>
  );
}
