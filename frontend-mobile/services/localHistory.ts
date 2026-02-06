
import { Platform } from 'react-native';

// For web compatibility if we needed AsyncStorage we could use it, but let's stick to the pattern in storage.ts
// or simple localStorage for web.

const HISTORY_KEY = 'guest_diagnosis_history';

// Helper to interact with storage
// In-memory store for native session (cleared when app is killed)
let tempHistoryStore: string | null = null;

// Helper to interact with storage
const getStorage = async () => {
    if (Platform.OS === 'web') {
        // Use sessionStorage instead of localStorage for session-only persistence
        return sessionStorage.getItem(HISTORY_KEY);
    } else {
        // Return in-memory variable for native
        return tempHistoryStore;
    }
};

const setStorage = async (value: string) => {
    if (Platform.OS === 'web') {
        sessionStorage.setItem(HISTORY_KEY, value);
    } else {
        tempHistoryStore = value;
    }
};

export interface LocalHistoryItem {
    id: string | number;
    crop: string;
    disease: string;
    confidence: number;
    severity_percent: number;
    stage: string;
    created_at: string;
    fullData?: any; // Store full response to avoid re-fetching since backend doesn't have it
}

export const getLocalHistory = async (): Promise<LocalHistoryItem[]> => {
    try {
        const json = await getStorage();
        if (!json) return [];
        return JSON.parse(json);
    } catch (e) {
        console.error('Error reading local history', e);
        return [];
    }
};

export const addToLocalHistory = async (diagnosisResult: any, crop: string) => {
    try {
        const history = await getLocalHistory();

        const newItem: LocalHistoryItem = {
            id: Date.now(), // Generate a local ID
            crop: crop,
            disease: diagnosisResult.prediction.disease,
            confidence: diagnosisResult.prediction.confidence,
            severity_percent: diagnosisResult.prediction.severity_percent,
            stage: diagnosisResult.prediction.stage,
            created_at: new Date().toISOString(),
            fullData: diagnosisResult
        };

        const updatedHistory = [newItem, ...history];

        // Limit to last 20 items to save space
        if (updatedHistory.length > 20) {
            updatedHistory.length = 20;
        }

        await setStorage(JSON.stringify(updatedHistory));
        return newItem;
    } catch (e) {
        console.error('Error saving local history', e);
    }
};

export const clearLocalHistory = async () => {
    if (Platform.OS === 'web') {
        sessionStorage.removeItem(HISTORY_KEY);
    } else {
        tempHistoryStore = null;
    }
};
