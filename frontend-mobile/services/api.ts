import axios from 'axios';
import { getItem } from './storage';
import { Platform } from 'react-native';

/**
 * This is our phone line to the Server (Backend).
 * When running on Web (browser), we use localhost since the backend runs on the same machine.
 * When running on a physical device or emulator, we use the LAN IP so the device can reach the backend.
 */
export const API_URL = Platform.OS === 'web'
    ? 'http://localhost:5000/api/'
    : 'http://10.163.32.227:5000/api/';

const api = axios.create({
    baseURL: API_URL,

});

/**
 * Before making a call, let's check if the user is logged in.
 * If they have a token (VIP pass), we attach it to the request so the server knows who they are.
 */
api.interceptors.request.use(
    async (config) => {
        const token = await getItem('userToken');
        console.log(`[API] Request to ${config.url} | Token exists: ${!!token}`);
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            console.log('[API] Attached Authorization header');
        } else {
            console.log('[API] No token attached');
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;
