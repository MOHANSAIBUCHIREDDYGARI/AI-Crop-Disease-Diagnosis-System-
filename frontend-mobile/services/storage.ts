import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

const isWeb = Platform.OS === 'web';

/**
 * Save a piece of information safely on the user's phone.
 * If on the web, we use LocalStorage.
 * If on a phone, we use SecureStore (like a digital safe).
 */
export const saveItem = async (key: string, value: string) => {
    if (isWeb) {
        try {
            localStorage.setItem(key, value);
        } catch (e) {
            console.error('Local storage unavailable:', e);
        }
    } else {
        await SecureStore.setItemAsync(key, value);
    }
};

/**
 * Retrieve saved information (like looking in the digital safe).
 */
export const getItem = async (key: string) => {
    if (isWeb) {
        if (typeof localStorage !== 'undefined') {
            return localStorage.getItem(key);
        }
        return null;
    } else {
        return await SecureStore.getItemAsync(key);
    }
};

/**
 * Remove information (clean it out of the safe).
 */
export const deleteItem = async (key: string) => {
    if (isWeb) {
        if (typeof localStorage !== 'undefined') {
            localStorage.removeItem(key);
        }
    } else {
        await SecureStore.deleteItemAsync(key);
    }
};
