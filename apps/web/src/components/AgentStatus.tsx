/**
 * Agent Status Component
 * Displays which agent is currently active
 */

import React from 'react';
import { AgentType } from '@vibe-ceo/shared';

interface AgentStatusProps {
    currentAgent: AgentType | null;
    isLoading: boolean;
}

const agentConfig = {
    [AgentType.VIBE]: {
        name: 'Vibe',
        color: 'from-purple-500 to-pink-500',
        icon: '💜',
        description: 'Emotional & Well-being Support',
    },
    [AgentType.PLANNER]: {
        name: 'Planner',
        color: 'from-blue-500 to-cyan-500',
        icon: '📅',
        description: 'Task & Calendar Management',
    },
    [AgentType.KNOWLEDGE]: {
        name: 'Knowledge',
        color: 'from-green-500 to-emerald-500',
        icon: '📚',
        description: 'Learning & Research',
    },
};

export default function AgentStatus({ currentAgent, isLoading }: AgentStatusProps) {
    const agent = currentAgent ? agentConfig[currentAgent] : null;

    return (
        <div className="glass-card rounded-xl px-4 py-3 mb-2 flex items-center justify-between transition-all duration-300">
            <div className="flex items-center gap-3">
                <div className="text-xl filter drop-shadow-sm">{agent?.icon || '🤖'}</div>
                <div>
                    <h3 className="font-medium text-sm text-foreground">
                        {agent ? `${agent.name} Agent` : 'Personal Vibe CEO'}
                    </h3>
                    <p className="text-xs text-muted-foreground">
                        {agent?.description || 'Ready to help'}
                    </p>
                </div>
            </div>

            <div className="flex items-center gap-2">
                {isLoading ? (
                    <div className="flex items-center gap-1.5 px-2">
                        <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse"></div>
                        <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse delay-75"></div>
                        <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse delay-150"></div>
                    </div>
                ) : (
                    <div className={`w-2 h-2 rounded-full ${agent ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : 'bg-gray-300'}`}></div>
                )}
            </div>
        </div>
    );
}
