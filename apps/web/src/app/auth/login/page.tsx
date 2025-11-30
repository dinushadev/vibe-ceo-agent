'use client';

import Login from '@/components/Login';

export default function LoginPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Personal Vibe CEO</h1>
                    <p className="text-gray-600 dark:text-gray-400">Your AI companion for well-being and productivity</p>
                </div>
                <Login />
            </div>
        </div>
    );
}
