import axios from 'axios';
import { getItem } from './storage';
import { Platform } from 'react-native';

/**
 * BACKEND CONNECTION CONFIGURATION
 *
 * For LAN mode (npx expo start) - your phone must be on the same Wi-Fi as your PC.
 * The IP address must match your PC's current Wi-Fi IP (run 'ipconfig' to check).
 *
 * Current LAN IP: 10.163.32.227
 */
export const BACKEND_HOST = '10.163.32.227';
export const BACKEND_PORT = 5000;
export const API_URL = Platform.OS === 'web'
    ? `http://localhost:${BACKEND_PORT}/api/`
    : `http://${BACKEND_HOST}:${BACKEND_PORT}/api/`; // LAN IP is more reliable since loca.lt is down

const api = axios.create({
    baseURL: API_URL,
    timeout: 30000, // 30 second timeout
});

/**
 * Before making a call, let's check if the user is logged in.
 * If they have a token (VIP pass), we attach it to the request so the server knows who they are.
 */
api.interceptors.request.use(
    async (config) => {
        // Bypass localtunnel reminder page
        config.headers['Bypass-Tunnel-Reminder'] = 'true';

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
