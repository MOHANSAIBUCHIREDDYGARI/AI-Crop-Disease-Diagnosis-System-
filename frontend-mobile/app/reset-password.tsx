import React, { useState, useRef } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    KeyboardAvoidingView, Platform, ScrollView, Alert, ActivityIndicator
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Lock, Eye, EyeOff, ArrowLeft } from 'lucide-react-native';
import api from '../services/api';

export default function ResetPasswordScreen() {
    const { email } = useLocalSearchParams<{ email: string }>();
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [inlineError, setInlineError] = useState('');
    const [inlineSuccess, setInlineSuccess] = useState('');
    const inputs = useRef<Array<TextInput | null>>([]);
    const router = useRouter();

    const handleOtpChange = (value: string, index: number) => {
        if (!/^\d*$/.test(value)) return;
        const newOtp = [...otp];
        newOtp[index] = value;
        setOtp(newOtp);
        if (value && index < 5) inputs.current[index + 1]?.focus();
    };

    const handleKeyPress = (e: any, index: number) => {
        if (e.nativeEvent.key === 'Backspace' && !otp[index] && index > 0) {
            inputs.current[index - 1]?.focus();
        }
    };

    const handleReset = async () => {
        setInlineError('');
        const otpStr = otp.join('');
        if (otpStr.length !== 6) {
            setInlineError('Please enter the full 6-digit OTP.');
            return;
        }
        if (!newPassword || newPassword.length < 6) {
            setInlineError('Password must be at least 6 characters.');
            return;
        }
        if (newPassword !== confirmPassword) {
            setInlineError('Passwords do not match.');
            return;
        }

        setLoading(true);
        try {
            await api.post('user/reset-password', {
                email,
                otp: otpStr,
                new_password: newPassword
            });
            setInlineSuccess('✅ Your password has been updated successfully! Redirecting to login...');
            setTimeout(() => {
                router.replace('/login');
            }, 2000);
        } catch (error: any) {
            const message = error.response?.data?.error || 'Reset failed. Please try again.';
            setInlineError(message);
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

                <Text style={styles.title}>Reset Password</Text>
                <Text style={styles.subtitle}>
                    Enter the OTP sent to{' '}
                    <Text style={styles.emailHighlight}>{email}</Text>
                    {' '}and choose a new password.
                </Text>

                {/* ⚠️ Inline Error Banner */}
                {inlineError ? (
                    <View style={styles.errorBanner}>
                        <Text style={styles.errorBannerText}>⚠️ {inlineError}</Text>
                    </View>
                ) : null}

                {/* ✅ Inline Success Banner */}
                {inlineSuccess ? (
                    <View style={styles.successBanner}>
                        <Text style={styles.successBannerText}>{inlineSuccess}</Text>
                    </View>
                ) : null}

                {/* OTP Input */}
                <Text style={styles.sectionLabel}>Enter OTP</Text>
                <View style={styles.otpRow}>
                    {otp.map((digit, i) => (
                        <TextInput
                            key={i}
                            ref={(ref) => { inputs.current[i] = ref; }}
                            style={[styles.otpBox, digit ? styles.otpBoxFilled : null]}
                            value={digit}
                            onChangeText={(v) => handleOtpChange(v, i)}
                            onKeyPress={(e) => handleKeyPress(e, i)}
                            keyboardType="numeric"
                            maxLength={1}
                            textAlign="center"
                            selectTextOnFocus
                        />
                    ))}
                </View>

                {/* New Password */}
                <Text style={styles.sectionLabel}>New Password</Text>
                <View style={styles.inputContainer}>
                    <Lock size={20} color="#aaa" style={styles.inputIcon} />
                    <TextInput
                        style={styles.input}
                        placeholder="Min. 6 characters"
                        placeholderTextColor="#bbb"
                        value={newPassword}
                        onChangeText={setNewPassword}
                        secureTextEntry={!showPassword}
                    />
                    <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                        {showPassword
                            ? <EyeOff size={20} color="#aaa" />
                            : <Eye size={20} color="#aaa" />}
                    </TouchableOpacity>
                </View>

                {/* Confirm Password */}
                <Text style={styles.sectionLabel}>Confirm Password</Text>
                <View style={styles.inputContainer}>
                    <Lock size={20} color="#aaa" style={styles.inputIcon} />
                    <TextInput
                        style={styles.input}
                        placeholder="Repeat password"
                        placeholderTextColor="#bbb"
                        value={confirmPassword}
                        onChangeText={setConfirmPassword}
                        secureTextEntry={!showPassword}
                    />
                </View>

                {/* Password match indicator */}
                {confirmPassword.length > 0 && (
                    <Text style={newPassword === confirmPassword ? styles.matchOk : styles.matchFail}>
                        {newPassword === confirmPassword ? '✅ Passwords match' : '❌ Passwords do not match'}
                    </Text>
                )}

                {/* Submit */}
                <TouchableOpacity
                    style={styles.resetButton}
                    onPress={handleReset}
                    disabled={loading}
                >
                    {loading ? (
                        <ActivityIndicator color="#fff" />
                    ) : (
                        <Text style={styles.resetButtonText}>Reset Password</Text>
                    )}
                </TouchableOpacity>

                <Text style={styles.expiryNote}>⏰ OTP is valid for 10 minutes</Text>
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
        marginBottom: 28,
    },
    title: { fontSize: 26, fontWeight: 'bold', color: '#1b5e20', marginBottom: 10 },
    subtitle: { fontSize: 15, color: '#666', lineHeight: 22, marginBottom: 28 },
    emailHighlight: { color: '#2e7d32', fontWeight: 'bold' },

    // Error banner
    errorBanner: {
        flexDirection: 'row',
        alignItems: 'flex-start',
        backgroundColor: '#ffebee',
        borderRadius: 12,
        padding: 14,
        marginBottom: 20,
        borderLeftWidth: 4,
        borderLeftColor: '#e53935',
        width: '100%',
    },
    errorBannerText: {
        color: '#c62828',
        fontSize: 13,
        fontWeight: '600',
        flex: 1,
        lineHeight: 19,
    },

    // Success banner
    successBanner: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#e8f5e9',
        borderRadius: 12,
        padding: 14,
        marginBottom: 20,
        borderLeftWidth: 4,
        borderLeftColor: '#43a047',
        width: '100%',
    },
    successBannerText: {
        color: '#2e7d32',
        fontSize: 13,
        fontWeight: '600',
        flex: 1,
        lineHeight: 19,
    },

    sectionLabel: {
        fontSize: 13, fontWeight: '600', color: '#999',
        marginBottom: 8, marginLeft: 2, letterSpacing: 0.5, textTransform: 'uppercase',
    },
    otpRow: { flexDirection: 'row', gap: 10, marginBottom: 28 },
    otpBox: {
        width: 46, height: 54,
        borderRadius: 12, borderWidth: 2, borderColor: '#ddd',
        backgroundColor: '#f8f9fa',
        fontSize: 22, fontWeight: 'bold', color: '#333',
        outlineStyle: 'none' as any,
    },
    otpBoxFilled: { borderColor: '#4caf50', backgroundColor: '#f0faf0' },
    inputContainer: {
        flexDirection: 'row', alignItems: 'center',
        backgroundColor: '#f8f9fa', borderRadius: 14,
        paddingHorizontal: 16, height: 56,
        borderWidth: 2, borderColor: '#e9ecef',
        marginBottom: 16,
    },
    inputIcon: { marginRight: 12 },
    input: { flex: 1, fontSize: 16, color: '#333', fontWeight: '500', backgroundColor: 'transparent', outlineStyle: 'none' as any },
    matchOk: { color: '#2e7d32', fontSize: 13, marginBottom: 16, marginLeft: 4 },
    matchFail: { color: '#c62828', fontSize: 13, marginBottom: 16, marginLeft: 4 },
    resetButton: {
        backgroundColor: '#4caf50', borderRadius: 16, height: 58,
        justifyContent: 'center', alignItems: 'center',
        shadowColor: '#4caf50', shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.3, shadowRadius: 16, elevation: 8,
        marginTop: 8, marginBottom: 16,
    },
    resetButtonText: { color: '#fff', fontSize: 18, fontWeight: 'bold', letterSpacing: 1 },
    expiryNote: { color: '#aaa', fontSize: 13, textAlign: 'center' },
});
