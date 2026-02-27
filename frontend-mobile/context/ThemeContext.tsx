import React, { createContext, useState, useEffect, useContext } from 'react';
import { useColorScheme as useSystemColorScheme, Appearance } from 'react-native';
import { saveItem, getItem } from '../services/storage';

interface ThemeContextType {
    isDarkMode: boolean;
    colorScheme: 'light' | 'dark';
    toggleTheme: () => Promise<void>;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const AppThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const systemColorScheme = useSystemColorScheme();
    const [isDarkMode, setIsDarkMode] = useState<boolean>(systemColorScheme === 'dark');

    useEffect(() => {
        loadThemePreference();
    }, []);

    const loadThemePreference = async () => {
        try {
            const storedTheme = await getItem('themePreference');
            if (storedTheme !== null) {
                setIsDarkMode(storedTheme === 'dark');
            } else {
                setIsDarkMode(systemColorScheme === 'dark');
            }
        } catch (e) {
            console.error('Failed to load theme preference', e);
        }
    };

    const toggleTheme = async () => {
        const newIsDark = !isDarkMode;
        setIsDarkMode(newIsDark);
        try {
            await saveItem('themePreference', newIsDark ? 'dark' : 'light');
            // If the environment supports Appearance.setColorScheme
            if (Appearance.setColorScheme) {
                Appearance.setColorScheme(newIsDark ? 'dark' : 'light');
            }
        } catch (e) {
            console.error('Failed to save theme preference', e);
        }
    };

    const colorScheme = isDarkMode ? 'dark' : 'light';

    return (
        <ThemeContext.Provider value={{ isDarkMode, colorScheme, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useAppTheme = () => {
    const context = useContext(ThemeContext);
    if (context === undefined) {
        throw new Error('useAppTheme must be used within an AppThemeProvider');
    }
    return context;
};
