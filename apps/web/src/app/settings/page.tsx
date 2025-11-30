'use client';

import React from 'react';
import Link from 'next/link';
import { useTheme } from '@/context/ThemeContext';
import IntegrationsSettings from '../../components/settings/IntegrationsSettings';

export default function SettingsPage() {
    const { theme } = useTheme();

    return (
        <div className={theme === 'dark' ? 'dark' : ''}>
            <div className="min-h-screen bg-background text-foreground p-8 transition-colors duration-300">
                <div className="max-w-2xl mx-auto">
                    <div className="mb-8">
                        <Link
                            href="/"
                            className="text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2"
                        >
                            ← Back to Home
                        </Link>
                    </div>
                    <h1 className="text-3xl font-bold mb-8">Settings</h1>
                    <IntegrationsSettings />
                </div>
            </div>
        </div>
    );
}
