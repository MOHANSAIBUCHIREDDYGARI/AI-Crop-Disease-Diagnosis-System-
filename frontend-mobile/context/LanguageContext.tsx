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

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const { user } = useAuth();
    const [language, setLanguageState] = useState<LanguageCode>('en');
    const [translations, setTranslations] = useState(Translations.en);
    const [isLoading, setIsLoading] = useState(false);

    // Initial load - start with English
    useEffect(() => {
        setTranslations(Translations.en);
    }, []);

    // Sync with user preference if logged in
    useEffect(() => {
        if (user?.preferred_language) {
            console.log('Syncing language from user pref:', user.preferred_language);
            setLanguage(user.preferred_language as LanguageCode);
        }
    }, [user?.preferred_language]);

    const fetchTranslations = async (lang: LanguageCode) => {
        if (lang === 'en') {
            setTranslations(Translations.en);
            return;
        }

        setIsLoading(true);
        try {
            console.log(`Fetching translations for ${lang}...`);
            // Check if we already have it in local state/cache (simple implementation)
            // Ideally we would cache this in a more persistent way, but for now just fetch

            const response = await api.post('/translations/batch', {
                texts: Translations.en,
                target_language: lang,
            });

            setTranslations(response.data);
        } catch (error) {
            console.error('Error fetching translations:', error);
            // Fallback to English on error
            setTranslations(Translations.en);
        } finally {
            setIsLoading(false);
        }
    };

    const setLanguage = (lang: LanguageCode) => {
        console.log('Setting language to:', lang);
        setLanguageState(lang);
        fetchTranslations(lang);
    };

    const t = (key: keyof typeof Translations['en']) => {
        return translations[key] || Translations['en'][key] || key;
    };

    const value = {
        language,
        setLanguage,
        t,
        translations,
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
