import React, { useState, useRef, useEffect } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    KeyboardAvoidingView, Platform, ScrollView, Alert, ActivityIndicator
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Mail, Shield, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react-native';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function VerifyOTPScreen() {
    const { email, otpError } = useLocalSearchParams<{ email: string; otpError?: string }>();
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [loading, setLoading] = useState(false);
    const [resending, setResending] = useState(false);
    const [inlineError, setInlineError] = useState('');
    const [inlineSuccess, setInlineSuccess] = useState('');
    const inputs = useRef<Array<TextInput | null>>([]);
    const { signIn } = useAuth();
    const router = useRouter();

    // Show the OTP-send error as an inline banner when the screen first opens
    useEffect(() => {
        if (otpError) {
            setInlineError(otpError);
        }
    }, [otpError]);

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

    const handleVerify = async () => {
        const otpStr = otp.join('');
        if (otpStr.length !== 6) {
            setInlineError('Please enter the full 6-digit OTP.');
            return;
        }

        setInlineError('');
        setInlineSuccess('');
        setLoading(true);
        try {
            const response = await api.post('user/verify-email-otp', {
                email: email,
                otp: otpStr
            });

            // Verification succeeded — show banner and auto-redirect
            setInlineSuccess('✅ Your email has been verified successfully! Redirecting to login...');
            setTimeout(() => {
                router.replace('/login');
            }, 2000);
        } catch (error: any) {
            const message = error.response?.data?.error || 'Verification failed. Please try again.';
            setInlineError(message);
        } finally {
            setLoading(false);
        }
    };

    const handleResend = async () => {
        setInlineError('');
        setInlineSuccess('');
        setResending(true);
        try {
            await api.post('user/send-otp', { email });
            setInlineSuccess(`✅ A new OTP has been sent to ${email}`);
            setOtp(['', '', '', '', '', '']);
            inputs.current[0]?.focus();
        } catch (error: any) {
            const message = error.response?.data?.error || 'Failed to resend OTP.';
            setInlineError(message);
        } finally {
            setResending(false);
        }
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={styles.container}
        >
            <ScrollView contentContainerStyle={styles.scrollContainer}>
                {/* Header */}
                <View style={styles.iconWrapper}>
                    <Shield size={48} color="#4caf50" />
                </View>
                <Text style={styles.title}>Verify Your Email</Text>
                <Text style={styles.subtitle}>
                    We sent a 6-digit code to{'\n'}
                    <Text style={styles.emailHighlight}>{email}</Text>
                </Text>

                {/* ⚠️ Inline Error Banner */}
                {inlineError ? (
                    <View style={styles.errorBanner}>
                        <AlertTriangle size={18} color="#c62828" style={{ marginRight: 8 }} />
                        <Text style={styles.errorBannerText}>{inlineError}</Text>
                    </View>
                ) : null}

                {/* ✅ Inline Success Banner */}
                {inlineSuccess ? (
                    <View style={styles.successBanner}>
                        <CheckCircle size={18} color="#2e7d32" style={{ marginRight: 8 }} />
                        <Text style={styles.successBannerText}>{inlineSuccess}</Text>
                    </View>
                ) : null}

                {/* OTP Boxes */}
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

                {/* Verify Button */}
                <TouchableOpacity
                    style={styles.verifyButton}
                    onPress={handleVerify}
                    disabled={loading}
                >
                    {loading ? (
                        <ActivityIndicator color="#fff" />
                    ) : (
                        <Text style={styles.verifyButtonText}>Verify Email</Text>
                    )}
                </TouchableOpacity>

                {/* Resend */}
                <TouchableOpacity style={styles.resendRow} onPress={handleResend} disabled={resending}>
                    {resending ? (
                        <ActivityIndicator size="small" color="#4caf50" />
                    ) : (
                        <>
                            <RefreshCw size={16} color="#4caf50" style={{ marginRight: 6 }} />
                            <Text style={styles.resendText}>Resend OTP</Text>
                        </>
                    )}
                </TouchableOpacity>

                <Text style={styles.expiryNote}>⏰ OTP is valid for 10 minutes</Text>
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#fff' },
    scrollContainer: { flexGrow: 1, padding: 28, justifyContent: 'center', alignItems: 'center' },
    iconWrapper: {
        width: 90, height: 90, borderRadius: 45,
        backgroundColor: '#e8f5e9',
        justifyContent: 'center', alignItems: 'center',
        marginBottom: 24,
        shadowColor: '#4caf50', shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.2, shadowRadius: 16, elevation: 8,
    },
    title: { fontSize: 26, fontWeight: 'bold', color: '#1b5e20', marginBottom: 12, textAlign: 'center' },
    subtitle: { fontSize: 16, color: '#666', textAlign: 'center', lineHeight: 24, marginBottom: 20 },
    emailHighlight: { color: '#2e7d32', fontWeight: 'bold' },

    // Error banner
    errorBanner: {
        flexDirection: 'row',
        alignItems: 'flex-start',
        backgroundColor: '#ffebee',
        borderRadius: 12,
        padding: 14,
        marginBottom: 16,
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
        marginBottom: 16,
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

    otpRow: { flexDirection: 'row', gap: 12, marginBottom: 32 },
    otpBox: {
        width: 48, height: 56,
        borderRadius: 12,
        borderWidth: 2, borderColor: '#ddd',
        backgroundColor: '#f8f9fa',
        fontSize: 22, fontWeight: 'bold', color: '#333',
        outlineStyle: 'none' as any,
    },
    otpBoxFilled: { borderColor: '#4caf50', backgroundColor: '#f0faf0' },
    verifyButton: {
        width: '100%',
        backgroundColor: '#4caf50',
        borderRadius: 16, height: 58,
        justifyContent: 'center', alignItems: 'center',
        shadowColor: '#4caf50', shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.3, shadowRadius: 16, elevation: 8,
        marginBottom: 20,
    },
    verifyButtonText: { color: '#fff', fontSize: 18, fontWeight: 'bold', letterSpacing: 1 },
    resendRow: { flexDirection: 'row', alignItems: 'center', padding: 12 },
    resendText: { color: '#4caf50', fontWeight: '600', fontSize: 15 },
    expiryNote: { color: '#aaa', fontSize: 13, marginTop: 12 },
});
