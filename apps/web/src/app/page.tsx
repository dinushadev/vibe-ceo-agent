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
      <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
        {/* Header */}
        <header className="glass sticky top-0 z-10 border-b border-border/40">
          <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="text-3xl filter drop-shadow-sm">🤖</div>
              <div>
                <h1 className="text-lg font-semibold tracking-tight">
                  Personal Vibe CEO
                </h1>
                <p className="text-xs text-muted-foreground font-medium">
                  Well-being Companion
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-full hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground"
                aria-label="Toggle dark mode"
              >
                {darkMode ? '🌞' : '🌙'}
              </button>

              {messages.length > 0 && (
                <button
                  onClick={clearMessages}
                  className="px-4 py-1.5 text-xs font-medium bg-secondary text-secondary-foreground rounded-full hover:bg-secondary/80 transition-colors"
                >
                  Clear Chat
                </button>
              )}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-3xl mx-auto px-4 py-8 h-[calc(100vh-80px)] flex flex-col gap-6">
          {/* Agent Status */}
          <AgentStatus currentAgent={currentAgent} isLoading={isLoading} />

          {/* Chat Container */}
          <div className="flex-1 flex flex-col overflow-hidden relative">
            <ChatInterface messages={messages} isLoading={isLoading} />
          </div>

          {/* Message Input */}
          <div className="pb-4">
            <MessageInput onSendMessage={sendMessage} isLoading={isLoading} />
          </div>
        </main>

        {/* Voice Interface */}
        <VoiceInterface />
      </div>
    </div>
  );
}
