import React, { createContext, useState, useEffect, useContext } from 'react';
import { saveItem, getItem, deleteItem } from '../services/storage';
import api from '../services/api';

interface User {
    id: number;
    email: string;
    name: string;
    preferred_language: string;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    isLoading: boolean;
    isGuest: boolean;
    signIn: (token: string, userData: User) => Promise<void>;
    signOut: () => Promise<void>;
    continueAsGuest: () => void;
    updateUser: (userData: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Authentication Provider:
 * This acts like a bouncer at the door.
 * It manages who is logged in, who is a guest, and remembers their session.
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isGuest, setIsGuest] = useState(false);

    // When the app starts, check if we remember the user from last time
    useEffect(() => {
        loadStorageData();
    }, []);

    const loadStorageData = async () => {
        try {
            const storedToken = await getItem('userToken');
            const storedUser = await getItem('userData');
            if (storedToken && storedUser) {
                // Welcome back! We know you.
                setToken(storedToken);
                setUser(JSON.parse(storedUser));
                setIsGuest(false);
            } else {
                // Stranger? You can proceed as guest or log in.
                setIsGuest(true);
            }
        } catch (e) {
            console.error('Failed to load auth data', e);
            setIsGuest(true);
        } finally {
            setIsLoading(false);
        }
    };

    /**
     * Log In: Save credentials so the user stays logged in even after closing the app.
     */
    const signIn = async (token: string, userData: User) => {
        await saveItem('userToken', token);
        await saveItem('userData', JSON.stringify(userData));
        await deleteItem('isGuest');
        setToken(token);
        setUser(userData);
        setIsGuest(false);
    };

    /**
     * Log Out: Forget everything about the user session.
     */
    const signOut = async () => {
        console.log('AuthContext: signOut called');
        try {
            console.log('AuthContext: Deleting stored items...');
            await deleteItem('userToken');
            await deleteItem('userData');
            await deleteItem('isGuest');
            console.log('AuthContext: Stored items deleted.');
        } catch (e) {
            console.error('AuthContext: Error removing auth data:', e);
        }
        console.log('AuthContext: Clearing state variables...');
        setToken(null);
        setUser(null);
        setIsGuest(false);
        console.log('AuthContext: State cleared.');
    };

    /**
     * Guest Mode: The user wants to look around without an account.
     */
    const continueAsGuest = async () => {
        await saveItem('isGuest', 'true');
        await deleteItem('userToken');
        await deleteItem('userData');
        setIsGuest(true);
        setToken(null);
        setUser(null);
    };

    /**
     * Update Profile: Changing name or language preference.
     */
    const updateUser = async (userData: Partial<User>) => {
        if (user) {
            const updatedUser = { ...user, ...userData };
            await saveItem('userData', JSON.stringify(updatedUser));
            setUser(updatedUser);
        }
    };

    return (
        <AuthContext.Provider value={{ user, token, isLoading, isGuest, signIn, signOut, continueAsGuest, updateUser }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
