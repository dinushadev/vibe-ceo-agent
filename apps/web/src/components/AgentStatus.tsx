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
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 mb-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="text-2xl">{agent?.icon || '🤖'}</div>
                    <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                            {agent ? `${agent.name} Agent` : 'Personal Vibe CEO'}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            {agent?.description || 'Ready to help'}
                        </p>
                    </div>
                </div>

                {isLoading && (
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-75"></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-150"></div>
                    </div>
                )}

                {agent && !isLoading && (
                    <div className={`px-3 py-1 rounded-full bg-gradient-to-r ${agent.color} text-white text-sm font-medium`}>
                        Active
                    </div>
                )}
            </div>

            {/* Agent indicators */}
            <div className="flex gap-2 mt-4">
                {Object.entries(agentConfig).map(([type, config]) => (
                    <div
                        key={type}
                        className={`flex-1 p-2 rounded-lg text-center transition-all ${currentAgent === type
                                ? `bg-gradient-to-r ${config.color} text-white shadow-md`
                                : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                            }`}
                    >
                        <div className="text-lg">{config.icon}</div>
                        <div className="text-xs font-medium mt-1">{config.name}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
