"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';

export default function IntegrationsSettings() {
    const { user } = useAuth();
    const [isConnected, setIsConnected] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (user?.user_id) {
            checkStatus();
        }
    }, [user]);

    const checkStatus = async () => {
        if (!user?.user_id) return;

        try {
            const response = await fetch(`http://localhost:8000/api/integrations/status?user_id=${user.user_id}`);
            const data = await response.json();
            setIsConnected(data.google_calendar);
        } catch (error) {
            console.error('Failed to check integration status:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleConnect = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/auth/google/url');
            const data = await response.json();
            if (data.url) {
                window.location.href = data.url;
            }
        } catch (error) {
            console.error('Failed to get auth URL:', error);
        }
    };

    if (isLoading) {
        return <div className="p-4 text-muted-foreground">Loading settings...</div>;
    }

    return (
        <div className="p-6 glass-card rounded-xl">
            <h2 className="text-xl font-semibold text-foreground mb-4">Integrations</h2>

            <div className="flex items-center justify-between p-4 bg-secondary/50 rounded-lg border border-border">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-sm">
                        <img
                            src="https://www.google.com/favicon.ico"
                            alt="Google"
                            className="w-6 h-6"
                        />
                    </div>
                    <div>
                        <h3 className="font-medium text-foreground">Google Calendar</h3>
                        <p className="text-sm text-muted-foreground">Sync your schedule and events</p>
                    </div>
                </div>

                {isConnected ? (
                    <div className="flex items-center gap-2 text-green-500 bg-green-500/10 px-3 py-1.5 rounded-full text-sm font-medium">
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                        Connected
                    </div>
                ) : (
                    <button
                        onClick={handleConnect}
                        className="btn-primary px-4 py-2 text-sm font-medium rounded-lg"
                    >
                        Connect
                    </button>
                )}
            </div>
        </div>
    );
}
