import React, { useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    KeyboardAvoidingView, Platform, ScrollView, ActivityIndicator
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { ArrowLeft, Lock, Eye, EyeOff } from 'lucide-react-native';
import api from '../services/api';

export default function ResetPasswordScreen() {
    const { email, otp } = useLocalSearchParams<{ email: string; otp: string }>();
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showNew, setShowNew] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);
    const [loading, setLoading] = useState(false);
    const [newFocused, setNewFocused] = useState(false);
    const [confirmFocused, setConfirmFocused] = useState(false);
    const [error, setError] = useState('');
    const router = useRouter();

    const handleReset = async () => {
        setError('');
        if (!newPassword || !confirmPassword) {
            setError('Please fill in both password fields.');
            return;
        }
        if (newPassword.length < 6) {
            setError('Password must be at least 6 characters long.');
            return;
        }
        if (newPassword !== confirmPassword) {
            setError('Passwords do not match. Please try again.');
            return;
        }

        setLoading(true);
        try {
            await api.post('user/reset-password', { email, otp, new_password: newPassword });
            // Navigate back to login on success
            router.replace('/login');
        } catch (err: any) {
            setError(err.response?.data?.error || 'Something went wrong. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
            <ScrollView contentContainerStyle={styles.scrollContainer}>
                <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
                    <ArrowLeft size={22} color="#2e7d32" />
                </TouchableOpacity>

                <View style={styles.header}>
                    <View style={styles.iconContainer}>
                        <Lock size={40} color="#4caf50" />
                    </View>
                    <Text style={styles.title}>New Password</Text>
                    <Text style={styles.subtitle}>Create a strong new password for your account.</Text>
                </View>

                <View style={styles.form}>
                    <Text style={[styles.fieldLabel, newFocused && styles.fieldLabelFocused]}>NEW PASSWORD</Text>
                    <View style={[styles.inputContainer, newFocused && styles.inputContainerFocused]}>
                        <Lock size={20} color={newFocused ? '#4caf50' : '#aaa'} style={styles.inputIcon} />
                        <TextInput
                            style={styles.input}
                            placeholder="At least 6 characters"
                            placeholderTextColor="#bbb"
                            value={newPassword}
                            onChangeText={setNewPassword}
                            secureTextEntry={!showNew}
                            onFocus={() => setNewFocused(true)}
                            onBlur={() => setNewFocused(false)}
                        />
                        <TouchableOpacity onPress={() => setShowNew(!showNew)}>
                            {showNew ? <EyeOff size={20} color="#aaa" /> : <Eye size={20} color="#aaa" />}
                        </TouchableOpacity>
                    </View>

                    <Text style={[styles.fieldLabel, confirmFocused && styles.fieldLabelFocused, { marginTop: 20 }]}>CONFIRM PASSWORD</Text>
                    <View style={[styles.inputContainer, confirmFocused && styles.inputContainerFocused]}>
                        <Lock size={20} color={confirmFocused ? '#4caf50' : '#aaa'} style={styles.inputIcon} />
                        <TextInput
                            style={styles.input}
                            placeholder="Re-enter password"
                            placeholderTextColor="#bbb"
                            value={confirmPassword}
                            onChangeText={setConfirmPassword}
                            secureTextEntry={!showConfirm}
                            onFocus={() => setConfirmFocused(true)}
                            onBlur={() => setConfirmFocused(false)}
                        />
                        <TouchableOpacity onPress={() => setShowConfirm(!showConfirm)}>
                            {showConfirm ? <EyeOff size={20} color="#aaa" /> : <Eye size={20} color="#aaa" />}
                        </TouchableOpacity>
                    </View>

                    {confirmPassword.length > 0 && (
                        <Text style={[styles.matchText, newPassword === confirmPassword ? styles.matchOk : styles.matchBad]}>
                            {newPassword === confirmPassword ? '✓ Passwords match' : '✗ Passwords do not match'}
                        </Text>
                    )}

                    {error ? <Text style={styles.errorText}>{error}</Text> : null}

                    <TouchableOpacity
                        style={[styles.resetButton, loading && styles.buttonDisabled]}
                        onPress={handleReset}
                        disabled={loading}
                    >
                        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.resetButtonText}>Reset Password</Text>}
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
    matchText: { fontSize: 13, fontWeight: '600', marginTop: 8, marginLeft: 4 },
    matchOk: { color: '#4caf50' },
    matchBad: { color: '#e53935' },
    errorText: { color: '#e53935', fontSize: 14, textAlign: 'center', marginTop: 12 },
    resetButton: {
        backgroundColor: '#4caf50', borderRadius: 16, height: 60,
        justifyContent: 'center', alignItems: 'center', marginTop: 24,
        shadowColor: '#4caf50', shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.3, shadowRadius: 16, elevation: 8,
    },
    buttonDisabled: { opacity: 0.7 },
    resetButtonText: { color: '#fff', fontSize: 18, fontWeight: 'bold', letterSpacing: 1 },
});
