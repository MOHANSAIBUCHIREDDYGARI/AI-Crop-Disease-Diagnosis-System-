import React, { useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    KeyboardAvoidingView, Platform, ScrollView, ActivityIndicator
} from 'react-native';
import { useRouter } from 'expo-router';
import { Mail, ArrowLeft, Leaf } from 'lucide-react-native';
import api from '../services/api';

export default function ForgotPasswordScreen() {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [emailFocused, setEmailFocused] = useState(false);
    const [error, setError] = useState('');
    const router = useRouter();

    const handleSendOTP = async () => {
        setError('');
        if (!email.trim()) {
            setError('Please enter your email address.');
            return;
        }

        setLoading(true);
        try {
            await api.post('user/forgot-password', { email: email.trim().toLowerCase() });
            // Navigate directly — no Alert needed
            router.push({ pathname: '/verify-otp', params: { email: email.trim().toLowerCase() } });
        } catch (err: any) {
            setError(err.response?.data?.error || 'Something went wrong. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
            <ScrollView contentContainerStyle={styles.scrollContainer}>
                {/* Back Button */}
                <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
                    <ArrowLeft size={22} color="#2e7d32" />
                </TouchableOpacity>

                {/* Header */}
                <View style={styles.header}>
                    <View style={styles.iconContainer}>
                        <Leaf size={40} color="#4caf50" />
                    </View>
                    <Text style={styles.title}>Forgot Password?</Text>
                    <Text style={styles.subtitle}>
                        Enter your registered email address and we'll send you a 6-digit OTP to reset your password.
                    </Text>
                </View>

                {/* Form */}
                <View style={styles.form}>
                    <Text style={[styles.fieldLabel, emailFocused && styles.fieldLabelFocused]}>EMAIL ADDRESS</Text>
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

                    <TouchableOpacity
                        style={[styles.sendButton, loading && styles.sendButtonDisabled]}
                        onPress={handleSendOTP}
                        disabled={loading}
                    >
                        {loading ? (
                            <ActivityIndicator color="#fff" />
                        ) : (
                            <Text style={styles.sendButtonText}>Send OTP</Text>
                        )}
                    </TouchableOpacity>

                    <TouchableOpacity style={styles.backToLogin} onPress={() => router.back()}>
                        <Text style={styles.backToLoginText}>Back to Login</Text>
                    </TouchableOpacity>
                </View>
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#fff' },
    scrollContainer: { flexGrow: 1, padding: 24, justifyContent: 'center' },
    backButton: {
        width: 44, height: 44, borderRadius: 12, backgroundColor: '#f0faf0',
        justifyContent: 'center', alignItems: 'center', marginBottom: 16,
    },
    header: { alignItems: 'center', marginBottom: 40 },
    iconContainer: {
        width: 90, height: 90, borderRadius: 45, backgroundColor: '#e8f5e9',
        justifyContent: 'center', alignItems: 'center', marginBottom: 24,
        shadowColor: '#4caf50', shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.2, shadowRadius: 16, elevation: 8,
    },
    title: { fontSize: 28, fontWeight: 'bold', color: '#1b5e20', marginBottom: 12 },
    subtitle: { fontSize: 15, color: '#666', textAlign: 'center', lineHeight: 22, maxWidth: '85%' },
    form: { width: '100%' },
    fieldLabel: {
        fontSize: 12, fontWeight: '700', color: '#999', marginBottom: 8,
        marginLeft: 4, letterSpacing: 0.5, textTransform: 'uppercase',
    },
    fieldLabelFocused: { color: '#4caf50' },
    inputContainer: {
        flexDirection: 'row', alignItems: 'center', backgroundColor: '#f8f9fa',
        borderRadius: 14, paddingHorizontal: 16, height: 56,
        borderWidth: 2, borderColor: '#e9ecef',
    },
    inputContainerFocused: { borderColor: '#4caf50', backgroundColor: '#f0faf0' },
    inputIcon: { marginRight: 12 },
    input: { flex: 1, fontSize: 16, color: '#333', fontWeight: '500' },
    sendButton: {
        backgroundColor: '#4caf50', borderRadius: 16, height: 60,
        justifyContent: 'center', alignItems: 'center', marginTop: 24,
        shadowColor: '#4caf50', shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.3, shadowRadius: 16, elevation: 8,
    },
    sendButtonDisabled: { opacity: 0.7 },
    sendButtonText: { color: '#fff', fontSize: 18, fontWeight: 'bold', letterSpacing: 1 },
    backToLogin: { alignItems: 'center', marginTop: 24 },
    backToLoginText: { fontSize: 15, color: '#4caf50', fontWeight: '600' },
});
