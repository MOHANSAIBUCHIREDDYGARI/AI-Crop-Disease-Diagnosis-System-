import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Switch, Alert, Platform } from 'react-native';
import { router } from 'expo-router';
import { User, LogOut, Globe, Bell, Shield, Info, HelpCircle, ChevronRight, Languages } from 'lucide-react-native';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import api from '../services/api';

const LANGUAGES = [
    { code: 'en', name: 'English', nativeName: 'English' },
    { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' },
    { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
    { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
    { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ' },
    { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
    { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം' },
    { code: 'tcy', name: 'Tulu', nativeName: 'ತುಳು' },
];

export default function ProfileScreen() {
    const { user, signOut, isGuest, updateUser } = useAuth();
    const { language, setLanguage, t } = useLanguage();
    console.log('ProfileScreen rendered. Current language:', language);
    const [notifications, setNotifications] = useState(true);
    const [showLanguagePicker, setShowLanguagePicker] = useState(false);

    const handleSignOut = async () => {
        const doLogout = async () => {
            try {
                await signOut();
            } catch (e) {
                console.error('SignOut error:', e);
            }
            if (Platform.OS === 'web') {
                (window as any).location.href = '/login';
            } else {
                router.replace('/login');
            }
        };

        if (Platform.OS === 'web') {
            // Alert.alert callbacks are unreliable on React Native Web — use native browser confirm
            const confirmed = (window as any).confirm('Are you sure you want to log out?');
            if (confirmed) {
                await doLogout();
            }
        } else {
            Alert.alert(
                t('signOutTitle'),
                t('signOutMessage'),
                [
                    { text: t('cancel'), style: 'cancel' },
                    { text: t('logOut'), style: 'destructive', onPress: doLogout }
                ]
            );
        }
    };

    /**
     * Change Language Strategy:
     * 1. Update the app state instantly (so the UI changes).
     * 2. If logged in, tell the server (sync).
     * 3. Show a nice success message.
     */
    const changeLanguage = async (code: string) => {
        try {
            console.log('User selected language:', code);
            // Update the app's language setting
            setLanguage(code as any);
            setShowLanguagePicker(false);

            if (!isGuest && user) {
                console.log('Syncing language with backend...');
                await api.put('user/language', { language: code });

                await updateUser({ preferred_language: code });
                console.log('Backend sync successful');
            }

            Alert.alert(t('success'), `${t('languageChanged')} ${LANGUAGES.find(l => l.code === code)?.name}`);
        } catch (error) {
            console.error('Failed to update language on backend', error);
            // Even if the server fails, we keep the local change so the user isn't stuck
            Alert.alert(t('error'), t('failedUpdate'));
        }
    };

    return (
        <ScrollView style={styles.container}>
            {/* Header: Avatar & Name */}
            <View style={styles.profileHeader}>
                <View style={styles.avatarCircle}>
                    <User size={40} color="#4caf50" />
                </View>
                <Text style={styles.userName}>{isGuest ? t('guestUser') : user?.name}</Text>
                <Text style={styles.userEmail}>{isGuest ? t('browseMode') : user?.email}</Text>

                {isGuest && (
                    <TouchableOpacity style={styles.registerCTA} onPress={() => router.replace('/login')}>
                        <Text style={styles.registerCTAText}>{t('registerFullAccess')}</Text>
                    </TouchableOpacity>
                )}
            </View>

            {/* Settings Section */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>{t('preferences')}</Text>

                {/* Language Picker Toggle */}
                <TouchableOpacity style={styles.menuItem} onPress={() => setShowLanguagePicker(!showLanguagePicker)}>
                    <View style={styles.menuIconCircle}>
                        <Languages size={20} color="#4caf50" />
                    </View>
                    <View style={styles.menuContent}>
                        <Text style={styles.menuLabel}>{t('appLanguage')}</Text>
                        <Text style={styles.menuSubLabel}>{LANGUAGES.find(l => l.code === language)?.nativeName}</Text>
                    </View>
                    <ChevronRight size={20} color="#ccc" />
                </TouchableOpacity>

                {/* Dropdown for Languages */}
                {showLanguagePicker && (
                    <View style={styles.languageGrid}>
                        {LANGUAGES.map((lang) => (
                            <TouchableOpacity
                                key={lang.code}
                                style={[styles.langOption, language === lang.code && styles.langOptionSelected]}
                                onPress={() => changeLanguage(lang.code)}
                            >
                                <Text style={[styles.langOptionText, language === lang.code && styles.langOptionTextSelected]}>
                                    {lang.nativeName}
                                </Text>
                            </TouchableOpacity>
                        ))}
                    </View>
                )}

                <View style={styles.menuItem}>
                    <View style={[styles.menuIconCircle, { backgroundColor: '#e3f2fd' }]}>
                        <Bell size={20} color="#1976d2" />
                    </View>
                    <View style={styles.menuContent}>
                        <Text style={styles.menuLabel}>{t('pushNotifications')}</Text>
                    </View>
                    <Switch
                        value={notifications}
                        onValueChange={setNotifications}
                        trackColor={{ false: "#ddd", true: "#a5d6a7" }}
                        thumbColor={notifications ? "#4caf50" : "#f4f3f4"}
                    />
                </View>
            </View>

            {/* Legal & Help */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>{t('supportLegal')}</Text>

                <TouchableOpacity
                    style={styles.menuItem}
                    onPress={() => router.push('/help')}
                >
                    <View style={[styles.menuIconCircle, { backgroundColor: '#f5f5f5' }]}>
                        <HelpCircle size={20} color="#666" />
                    </View>
                    <View style={styles.menuContent}>
                        <Text style={styles.menuLabel}>{t('helpCenter')}</Text>
                    </View>
                    <ChevronRight size={20} color="#ccc" />
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.menuItem}
                    onPress={() => router.push('/privacy')}
                >
                    <View style={[styles.menuIconCircle, { backgroundColor: '#f5f5f5' }]}>
                        <Shield size={20} color="#666" />
                    </View>
                    <View style={styles.menuContent}>
                        <Text style={styles.menuLabel}>{t('privacyPolicy')}</Text>
                    </View>
                    <ChevronRight size={20} color="#ccc" />
                </TouchableOpacity>

                <TouchableOpacity style={styles.menuItem}>
                    <View style={[styles.menuIconCircle, { backgroundColor: '#f5f5f5' }]}>
                        <Info size={20} color="#666" />
                    </View>
                    <View style={styles.menuContent}>
                        <Text style={styles.menuLabel}>{t('appVersion')}</Text>
                        <Text style={styles.menuSubLabel}>v1.0.0</Text>
                    </View>
                </TouchableOpacity>
            </View>

            {!isGuest && (
                <TouchableOpacity style={styles.logoutButton} onPress={handleSignOut}>
                    <LogOut size={20} color="#d32f2f" style={{ marginRight: 12 }} />
                    <Text style={styles.logoutText}>{t('logOut')}</Text>
                </TouchableOpacity>
            )}

            <View style={styles.footer}>
                <Text style={styles.footerText}>{t('madeWithLove')}</Text>
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8f8f8',
    },
    profileHeader: {
        backgroundColor: '#fff',
        padding: 32,
        alignItems: 'center',
        marginBottom: 12,
    },
    avatarCircle: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: '#e8f5e9',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 16,
    },
    userName: {
        fontSize: 22,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 4,
    },
    userEmail: {
        fontSize: 14,
        color: '#666',
        marginBottom: 16,
    },
    registerCTA: {
        backgroundColor: '#4caf50',
        paddingHorizontal: 20,
        paddingVertical: 10,
        borderRadius: 20,
    },
    registerCTAText: {
        color: '#fff',
        fontWeight: 'bold',
    },
    section: {
        backgroundColor: '#fff',
        paddingHorizontal: 20,
        paddingVertical: 16,
        marginBottom: 12,
    },
    sectionTitle: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#999',
        textTransform: 'uppercase',
        letterSpacing: 1,
        marginBottom: 16,
    },
    menuItem: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 12,
    },
    menuIconCircle: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#e8f5e9',
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 16,
    },
    menuContent: {
        flex: 1,
    },
    menuLabel: {
        fontSize: 16,
        color: '#333',
        fontWeight: '500',
    },
    menuSubLabel: {
        fontSize: 12,
        color: '#888',
        marginTop: 2,
    },
    languageGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
        marginTop: 8,
        marginBottom: 16,
        paddingLeft: 56,
    },
    langOption: {
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 16,
        borderWidth: 1,
        borderColor: '#eee',
        backgroundColor: '#f9f9f9',
    },
    langOptionSelected: {
        backgroundColor: '#e8f5e9',
        borderColor: '#4caf50',
    },
    langOptionText: {
        fontSize: 13,
        color: '#666',
    },
    langOptionTextSelected: {
        color: '#2e7d32',
        fontWeight: 'bold',
    },
    logoutButton: {
        backgroundColor: '#fff',
        padding: 20,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 24,
    },
    logoutText: {
        color: '#d32f2f',
        fontSize: 16,
        fontWeight: 'bold',
    },
    footer: {
        padding: 24,
        alignItems: 'center',
        marginBottom: 40,
    },
    footerText: {
        fontSize: 12,
        color: '#ccc',
    },
});
