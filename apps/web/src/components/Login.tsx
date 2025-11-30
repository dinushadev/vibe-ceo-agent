import React from 'react';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

interface LoginProps {
    onSuccess?: (user: any) => void;
}

const Login: React.FC<LoginProps> = ({ onSuccess }) => {
    const router = useRouter();
    const { login } = useAuth();

    const handleSuccess = async (credentialResponse: CredentialResponse) => {
        if (credentialResponse.credential) {
            try {
                const response = await fetch('http://localhost:8000/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ token: credentialResponse.credential }),
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log('Login successful:', data);

                    // Update auth context
                    login(data.user);

                    if (onSuccess) {
                        onSuccess(data.user);
                    }
                } else {
                    console.error('Login failed:', await response.text());
                }
            } catch (error) {
                console.error('Error during login:', error);
            }
        }
    };

    const handleError = () => {
        console.log('Login Failed');
    };

    return (
        <div className="flex flex-col items-center justify-center p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-white">Sign In</h2>
            <GoogleLogin
                onSuccess={handleSuccess}
                onError={handleError}
                useOneTap
                theme="filled_blue"
                shape="pill"
            />
        </div>
    );
};

export default Login;
