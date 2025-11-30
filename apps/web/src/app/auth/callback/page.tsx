"use client";

import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function AuthCallback() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [status, setStatus] = useState('Processing authentication...');

    useEffect(() => {
        const code = searchParams.get('code');
        if (code) {
            handleCallback(code);
        } else {
            setStatus('No authentication code found.');
        }
    }, [searchParams]);

    const handleCallback = async (code: string) => {
        try {
            const response = await fetch('http://localhost:8000/api/auth/google/callback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    code,
                    user_id: 'user_123' // Default for MVP
                }),
            });

            if (response.ok) {
                setStatus('Successfully connected! Redirecting...');
                setTimeout(() => {
                    router.push('/settings');
                }, 1500);
            } else {
                setStatus('Failed to connect. Please try again.');
            }
        } catch (error) {
            console.error('Auth callback error:', error);
            setStatus('An error occurred during authentication.');
        }
    };

    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center">
            <div className="text-center">
                <h2 className="text-2xl font-bold mb-4">Google Calendar Connection</h2>
                <p className="text-gray-400">{status}</p>
            </div>
        </div>
    );
}
