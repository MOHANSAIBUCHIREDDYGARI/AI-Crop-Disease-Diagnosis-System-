import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { Translations, LanguageCode } from '../constants/Translations';
import { useAuth } from './AuthContext';
import api from '../services/api';

interface LanguageContextType {
    language: LanguageCode;
    setLanguage: (lang: LanguageCode) => void;
    t: (key: keyof typeof Translations['en']) => string;
    translations: typeof Translations['en'];
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

/**
 * Language Provider:
 * This makes sure the app speaks the user's language.
 * It handles loading translations from the backend and switching languages on the fly.
 */
export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const { user } = useAuth();
    const [language, setLanguageState] = useState<LanguageCode>('en');
    const [dynamicTranslations, setDynamicTranslations] = useState<Record<string, string>>({});

    // If the user logs in and has a preferred language, switch to it automatically
    useEffect(() => {
        if (user?.preferred_language) {
            console.log('Syncing language from user pref:', user.preferred_language);
            setLanguage(user.preferred_language as LanguageCode);
        }
    }, [user?.preferred_language]);

    // Fetch new translations whenever the language changes
    // (We don't ship all languages in the app bundle to keep it small)
    useEffect(() => {
        const fetchDynamicTranslations = async () => {
            try {
                // English is the default, no need to fetch
                if (language === 'en') {
                    setDynamicTranslations({});
                    return;
                }

                console.log('Fetching dynamic translations for:', language);
                const response = await api.get(`user/translations?lang=${language}`);
                if (response.data) {
                    // Update our dictionary with new words
                    setDynamicTranslations(response.data);
                }
            } catch (error) {
                console.error('Failed to fetch translations:', error);
            }
        };

        fetchDynamicTranslations();
    }, [language]);

    const setLanguage = (lang: LanguageCode) => {
        console.log('Setting language to:', lang);
        setLanguageState(lang);
    };

    /**
     * Translator Function (t):
     * Takes a key (e.g., 'welcome_message') and gives back the text in the correct language.
     * Priorities:
     * 1. Dynamic translation from backend
     * 2. Hardcoded translation in Translations.ts
     * 3. Fallback to English
     */
    const t = (key: keyof typeof Translations['en']) => {
        // Check dynamic updates first
        if (dynamicTranslations[key]) {
            return dynamicTranslations[key];
        }

        // Check static file
        const translation = (Translations[language] as any)?.[key];
        return translation || Translations['en'][key] || key;
    };

    const value = {
        language,
        setLanguage,
        t,
        translations: { ...Translations['en'], ...Translations[language] },
    };

    return (
        <LanguageContext.Provider value={value}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (context === undefined) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
};
