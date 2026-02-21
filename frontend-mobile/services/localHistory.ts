
import { Platform } from 'react-native';

// For guest users, we just save their history on their own device.
// We use a temporary variable for mobile (simple session) or SessionStorage for web.
const HISTORY_KEY = 'guest_diagnosis_history';

// A temporary place to keep history while the app is open (for non-web platforms)
let tempHistoryStore: string | null = null;


const getStorage = async () => {
    if (Platform.OS === 'web') {
        // web browser memory
        return sessionStorage.getItem(HISTORY_KEY);
    } else {
        // app memory
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
    fullData?: any;
}

/**
 * Fetch the list of past checkups from the local memory.
 */
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

/**
 * Save a new checkup result to the local memory.
 * We only keep the last 20 to save space.
 */
export const addToLocalHistory = async (diagnosisResult: any, crop: string) => {
    try {
        const history = await getLocalHistory();

        const newItem: LocalHistoryItem = {
            id: Date.now(),
            crop: crop,
            disease: diagnosisResult.prediction.disease,
            confidence: diagnosisResult.prediction.confidence,
            severity_percent: diagnosisResult.prediction.severity_percent,
            stage: diagnosisResult.prediction.stage,
            created_at: new Date().toISOString(),
            fullData: diagnosisResult
        };

        const updatedHistory = [newItem, ...history];

        // Limit the history list to 20 items
        if (updatedHistory.length > 20) {
            updatedHistory.length = 20;
        }

        await setStorage(JSON.stringify(updatedHistory));
        return newItem;
    } catch (e) {
        console.error('Error saving local history', e);
    }
};

/**
 * Wipe the memory clean (like when the user leaves).
 */
export const clearLocalHistory = async () => {
    if (Platform.OS === 'web') {
        sessionStorage.removeItem(HISTORY_KEY);
    } else {
        tempHistoryStore = null;
    }
};
