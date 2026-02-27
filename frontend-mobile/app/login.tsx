import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Image, KeyboardAvoidingView, Platform, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { Mail, Lock, User, Leaf } from 'lucide-react-native';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import api from '../services/api';
import { T } from '../components/ui/T';

export default function LoginScreen() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [emailFocused, setEmailFocused] = useState(false);
    const [passwordFocused, setPasswordFocused] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const { signIn, continueAsGuest } = useAuth();
    const { t } = useLanguage();
    const router = useRouter();

    const handleLogin = async () => {
        setErrorMessage('');
        if (!email || !password) {
            setErrorMessage('Please enter both email and password.');
            return;
        }

        setLoading(true);
        try {
            const response = await api.post('user/login', { email, password });
            await signIn(response.data.token, response.data.user);
            router.replace('/(tabs)');
        } catch (error: any) {
            const serverMsg = error.response?.data?.error;
            setErrorMessage(serverMsg || 'Invalid email or password. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={styles.container}
        >
            <ScrollView contentContainerStyle={styles.scrollContainer}>
                <View style={styles.header}>
                    <View style={styles.logoContainer}>
                        <Image
                            source={require('../assets/images/logo.jpeg')}
                            style={styles.logoImage}
                            resizeMode="contain"
                        />
                    </View>
                    <T style={styles.title}>appTitle</T>
                    <T style={styles.subtitle}>appSubtitle</T>
                </View>

                <View style={styles.form}>
                    {/* Inline error banner */}
                    {errorMessage ? (
                        <View style={styles.errorBanner}>
                            <Text style={styles.errorBannerText}>⚠️  {errorMessage}</Text>
                        </View>
                    ) : null}

                    {/* Email Field */}
                    <View style={styles.fieldWrapper}>
                        <T style={[styles.fieldLabel, emailFocused && styles.fieldLabelFocused]}>emailPlaceholder</T>
                        <View style={[styles.inputContainer, emailFocused && styles.inputContainerFocused]}>
                            <Mail size={20} color={emailFocused ? '#4caf50' : '#aaa'} style={styles.inputIcon} />
                            <TextInput
                                style={styles.input}
                                placeholder={t('emailPlaceholder')}
                                value={email}
                                onChangeText={setEmail}
                                keyboardType="email-address"
                                autoCapitalize="none"
                                autoComplete="email"
                                onFocus={() => setEmailFocused(true)}
                                onBlur={() => setEmailFocused(false)}
                            />
                        </View>
                    </View>

                    {/* Password Field */}
                    <View style={styles.fieldWrapper}>
                        <T style={[styles.fieldLabel, passwordFocused && styles.fieldLabelFocused]}>passwordPlaceholder</T>
                        <View style={[styles.inputContainer, passwordFocused && styles.inputContainerFocused]}>
                            <Lock size={20} color={passwordFocused ? '#4caf50' : '#aaa'} style={styles.inputIcon} />
                            <TextInput
                                style={styles.input}
                                placeholder=""
                                value={password}
                                onChangeText={setPassword}
                                secureTextEntry
                                onFocus={() => setPasswordFocused(true)}
                                onBlur={() => setPasswordFocused(false)}
                            />
                        </View>
                    </View>

                    {/* Forgot Password */}
                    <TouchableOpacity
                        style={styles.forgotPasswordRow}
                        onPress={() => router.push('/forgot-password')}
                    >
                        <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                        style={styles.loginButton}
                        onPress={handleLogin}
                        disabled={loading}

                    >
                        {loading ? (
                            <ActivityIndicator color="#fff" />
                        ) : (
                            <T style={styles.loginButtonText}>loginButton</T>
                        )}
                    </TouchableOpacity>

                    {/* Guest Access Button */}
                    <TouchableOpacity
                        style={styles.guestButton}
                        onPress={() => {
                            continueAsGuest();
                            router.replace('/(tabs)');
                        }}
                    >
                        <T style={styles.guestButtonText}>continueGuest</T>
                    </TouchableOpacity>

                    <View style={styles.footer}>
                        <T style={styles.footerText}>noAccount</T>
                        <TouchableOpacity onPress={() => router.push('/register')}>
                            <T style={styles.footerLink}>registerNow</T>
                        </TouchableOpacity>
                    </View>
                </View>
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
    },
    errorBanner: {
        backgroundColor: '#ffebee',
        borderRadius: 12,
        paddingVertical: 12,
        paddingHorizontal: 16,
        marginBottom: 16,
        borderLeftWidth: 4,
        borderLeftColor: '#e53935',
    },
    errorBannerText: {
        color: '#c62828',
        fontSize: 14,
        fontWeight: '600',
        lineHeight: 20,
    },
    scrollContainer: {
        flexGrow: 1,
        padding: 24,
        justifyContent: 'center',
    },
    header: {
        alignItems: 'center',
        marginBottom: 48,
    },
    logoContainer: {
        width: 100,
        height: 100,
        borderRadius: 50,
        backgroundColor: '#e8f5e9',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 24,
        shadowColor: '#4caf50',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.2,
        shadowRadius: 20,
        elevation: 10,
        overflow: 'hidden',
    },
    logoImage: {
        width: 100,
        height: 100,
        borderRadius: 50,
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#1b5e20',
        marginBottom: 8,
        letterSpacing: 0.5,
    },
    subtitle: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
        maxWidth: '80%',
        lineHeight: 24,
    },
    form: {
        width: '100%',
    },
    fieldWrapper: {
        marginBottom: 20,
    },
    fieldLabel: {
        fontSize: 13,
        fontWeight: '600',
        color: '#999',
        marginBottom: 8,
        marginLeft: 4,
        letterSpacing: 0.5,
        textTransform: 'uppercase',
    },
    fieldLabelFocused: {
        color: '#4caf50',
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#f8f9fa',
        borderRadius: 14,
        paddingHorizontal: 16,
        height: 56,
        borderWidth: 2,
        borderColor: '#e9ecef',
    },
    inputContainerFocused: {
        borderColor: '#4caf50',
        backgroundColor: '#f0faf0',
    },
    inputIcon: {
        marginRight: 12,
    },
    input: {
        flex: 1,
        fontSize: 16,
        color: '#333',
        fontWeight: '500',
        outlineStyle: 'none' as any,
        backgroundColor: 'transparent',
    },
    loginButton: {
        backgroundColor: '#4caf50',
        borderRadius: 16,
        height: 60,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 16,
        shadowColor: '#4caf50',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.3,
        shadowRadius: 16,
        elevation: 8,
    },
    loginButtonText: {
        color: '#fff',
        fontSize: 18,
        fontWeight: 'bold',
        letterSpacing: 1,
    },
    guestButton: {
        backgroundColor: '#e8f5e9',
        borderRadius: 16,
        height: 60,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 16,
    },
    guestButtonText: {
        color: '#2e7d32',
        fontSize: 16,
        fontWeight: 'bold',
    },
    forgotPasswordRow: {
        alignSelf: 'flex-end',
        marginTop: 6,
        marginBottom: 4,
        paddingVertical: 4,
        paddingHorizontal: 2,
    },
    forgotPasswordText: {
        color: '#4caf50',
        fontSize: 14,
        fontWeight: '600',
    },
    footer: {
        flexDirection: 'row',
        justifyContent: 'center',
        marginTop: 32,
        alignItems: 'center',
    },
    footerText: {
        fontSize: 15,
        color: '#888',
        marginRight: 8,
    },
    footerLink: {
        fontSize: 15,
        color: '#2e7d32',
        fontWeight: 'bold',
    },
});
