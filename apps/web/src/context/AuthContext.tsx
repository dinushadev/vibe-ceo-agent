'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';

interface User {
    user_id: string;
    name: string;
    email: string;
    google_id: string;
    picture?: string;
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (userData: User) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        // Check local storage on mount
        const storedUser = localStorage.getItem('vibe_user');
        if (storedUser) {
            try {
                setUser(JSON.parse(storedUser));
            } catch (e) {
                console.error('Failed to parse user from local storage', e);
                localStorage.removeItem('vibe_user');
            }
        }
        setIsLoading(false);
    }, []);

    useEffect(() => {
        // Redirect if not authenticated and not on login page
        if (!isLoading && !user && pathname !== '/auth/login') {
            router.push('/auth/login');
        }
    }, [user, isLoading, pathname, router]);

    const login = (userData: User) => {
        setUser(userData);
        localStorage.setItem('vibe_user', JSON.stringify(userData));
        router.push('/');
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('vibe_user');
        router.push('/auth/login');
    };

    return (
        <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
