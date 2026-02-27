import React, { useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    KeyboardAvoidingView, Platform, ScrollView, Alert, ActivityIndicator
} from 'react-native';
import { useRouter } from 'expo-router';
import { Mail, ArrowLeft } from 'lucide-react-native';
import api from '../services/api';

export default function ForgotPasswordScreen() {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [emailFocused, setEmailFocused] = useState(false);
    const router = useRouter();

    const handleSendOTP = async () => {
        const trimmed = email.trim().toLowerCase();
        if (!trimmed) {
            Alert.alert('Error', 'Please enter your registered email address.');
            return;
        }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
            Alert.alert('Error', 'Please enter a valid email address.');
            return;
        }

        setLoading(true);
        try {
            await api.post('user/forgot-password', { email: trimmed });
            Alert.alert(
                '📧 OTP Sent!',
                `A password reset code has been sent to ${trimmed}. Check your inbox.`,
                [],
                { cancelable: false }
            );

            // Automatically redirect after showing the alert
            setTimeout(() => {
                router.push({ pathname: '/reset-password', params: { email: trimmed } });
            }, 1000);
        } catch (error: any) {
            const message = error.response?.data?.error || 'Something went wrong. Please try again.';
            Alert.alert('Error', message);
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
                {/* Back Button */}
                <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
                    <ArrowLeft size={22} color="#2e7d32" />
                </TouchableOpacity>

                {/* Icon */}
                <View style={styles.iconWrapper}>
                    <Mail size={48} color="#4caf50" />
                </View>

                <Text style={styles.title}>Forgot Password?</Text>
                <Text style={styles.subtitle}>
                    Enter your registered email address and we'll send you a one-time password to reset your password.
                </Text>

                {/* Email Field */}
                <View style={styles.fieldWrapper}>
                    <Text style={[styles.fieldLabel, emailFocused && styles.fieldLabelFocused]}>
                        Email Address
                    </Text>
                    <View style={[styles.inputContainer, emailFocused && styles.inputContainerFocused]}>
                        <Mail size={20} color={emailFocused ? '#4caf50' : '#aaa'} style={styles.inputIcon} />
                        <TextInput
                            style={styles.input}
                            placeholder="your@email.com"
                            placeholderTextColor="#bbb"
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

                {/* Send OTP Button */}
                <TouchableOpacity
                    style={styles.sendButton}
                    onPress={handleSendOTP}
                    disabled={loading}
                >
                    {loading ? (
                        <ActivityIndicator color="#fff" />
                    ) : (
                        <Text style={styles.sendButtonText}>Send Reset OTP</Text>
                    )}
                </TouchableOpacity>



                <TouchableOpacity style={styles.loginLink} onPress={() => router.back()}>
                    <Text style={styles.loginLinkText}>Back to Login</Text>
                </TouchableOpacity>
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#fff' },
    scrollContainer: { flexGrow: 1, padding: 28, paddingTop: 60 },
    backButton: {
        width: 44, height: 44, borderRadius: 22,
        backgroundColor: '#e8f5e9',
        justifyContent: 'center', alignItems: 'center',
        marginBottom: 32,
    },
    iconWrapper: {
        width: 90, height: 90, borderRadius: 45,
        backgroundColor: '#e8f5e9',
        justifyContent: 'center', alignItems: 'center',
        alignSelf: 'center',
        marginBottom: 24,
        shadowColor: '#4caf50', shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.2, shadowRadius: 16, elevation: 8,
    },
    title: {
        fontSize: 26, fontWeight: 'bold', color: '#1b5e20',
        textAlign: 'center', marginBottom: 12,
    },
    subtitle: {
        fontSize: 15, color: '#666', textAlign: 'center',
        lineHeight: 22, marginBottom: 36,
    },
    fieldWrapper: { marginBottom: 20 },
    fieldLabel: {
        fontSize: 13, fontWeight: '600', color: '#999',
        marginBottom: 8, marginLeft: 4, letterSpacing: 0.5, textTransform: 'uppercase',
    },
    fieldLabelFocused: { color: '#4caf50' },
    inputContainer: {
        flexDirection: 'row', alignItems: 'center',
        backgroundColor: '#f8f9fa', borderRadius: 14,
        paddingHorizontal: 16, height: 56,
        borderWidth: 2, borderColor: '#e9ecef',
    },
    inputContainerFocused: { borderColor: '#4caf50', backgroundColor: '#f0faf0' },
    inputIcon: { marginRight: 12 },
    input: { flex: 1, fontSize: 16, color: '#333', fontWeight: '500', backgroundColor: 'transparent', outlineStyle: 'none' as any },
    sendButton: {
        backgroundColor: '#4caf50', borderRadius: 16, height: 58,
        justifyContent: 'center', alignItems: 'center',
        shadowColor: '#4caf50', shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.3, shadowRadius: 16, elevation: 8, marginBottom: 16,
    },
    sendButtonText: { color: '#fff', fontSize: 18, fontWeight: 'bold', letterSpacing: 1 },
    secondaryButton: {
        borderWidth: 2, borderColor: '#4caf50', borderRadius: 16, height: 52,
        justifyContent: 'center', alignItems: 'center', marginBottom: 24,
    },
    secondaryButtonText: { color: '#2e7d32', fontSize: 15, fontWeight: '600' },
    loginLink: { alignItems: 'center' },
    loginLinkText: { color: '#888', fontSize: 15 },
});
