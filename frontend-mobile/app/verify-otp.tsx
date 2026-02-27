import React, { useState, useRef } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    KeyboardAvoidingView, Platform, ScrollView, ActivityIndicator
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { ArrowLeft, ShieldCheck } from 'lucide-react-native';
import api from '../services/api';

export default function VerifyOTPScreen() {
    const { email } = useLocalSearchParams<{ email: string }>();
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [loading, setLoading] = useState(false);
    const [resending, setResending] = useState(false);
    const [error, setError] = useState('');
    const [successMsg, setSuccessMsg] = useState('');
    const inputRefs = useRef<(TextInput | null)[]>([]);
    const router = useRouter();

    const handleOtpChange = (value: string, index: number) => {
        if (!/^\d*$/.test(value)) return;
        const newOtp = [...otp];
        newOtp[index] = value;
        setOtp(newOtp);
        if (value && index < 5) {
            inputRefs.current[index + 1]?.focus();
        }
    };

    const handleKeyPress = (key: string, index: number) => {
        if (key === 'Backspace' && !otp[index] && index > 0) {
            inputRefs.current[index - 1]?.focus();
        }
    };

    const handleVerify = async () => {
        setError('');
        const otpString = otp.join('');
        if (otpString.length !== 6) {
            setError('Please enter the complete 6-digit OTP.');
            return;
        }
        setLoading(true);
        try {
            await api.post('user/verify-otp', { email, otp: otpString });
            router.push({ pathname: '/reset-password', params: { email, otp: otpString } });
        } catch (err: any) {
            setError(err.response?.data?.error || 'Invalid OTP. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleResend = async () => {
        setError('');
        setResending(true);
        try {
            await api.post('user/forgot-password', { email });
            setOtp(['', '', '', '', '', '']);
            inputRefs.current[0]?.focus();
            setSuccessMsg('A new OTP has been sent to your email.');
        } catch {
            setError('Could not resend OTP. Please try again.');
        } finally {
            setResending(false);
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
                        <ShieldCheck size={40} color="#4caf50" />
                    </View>
                    <Text style={styles.title}>Verify OTP</Text>
                    <Text style={styles.subtitle}>Enter the 6-digit code sent to</Text>
                    <Text style={styles.emailText}>{email}</Text>
                    <Text style={styles.spamNote}>Check your spam/junk folder too!</Text>
                </View>

                {/* OTP Boxes */}
                <View style={styles.otpContainer}>
                    {otp.map((digit, index) => (
                        <TextInput
                            key={index}
                            ref={(ref) => { inputRefs.current[index] = ref; }}
                            style={[styles.otpBox, digit ? styles.otpBoxFilled : null]}
                            value={digit}
                            onChangeText={(val) => handleOtpChange(val, index)}
                            onKeyPress={({ nativeEvent }) => handleKeyPress(nativeEvent.key, index)}
                            keyboardType="number-pad"
                            maxLength={1}
                            textAlign="center"
                        />
                    ))}
                </View>

                {error ? <Text style={styles.errorText}>{error}</Text> : null}
                {successMsg ? <Text style={styles.successText}>{successMsg}</Text> : null}

                <TouchableOpacity
                    style={[styles.verifyButton, loading && styles.buttonDisabled]}
                    onPress={handleVerify}
                    disabled={loading}
                >
                    {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.verifyButtonText}>Verify OTP</Text>}
                </TouchableOpacity>

                <View style={styles.resendContainer}>
                    <Text style={styles.resendText}>Didn't receive it? </Text>
                    <TouchableOpacity onPress={handleResend} disabled={resending}>
                        <Text style={styles.resendLink}>{resending ? 'Resending...' : 'Resend OTP'}</Text>
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
    header: { alignItems: 'center', marginBottom: 32 },
    iconContainer: {
        width: 90, height: 90, borderRadius: 45, backgroundColor: '#e8f5e9',
        justifyContent: 'center', alignItems: 'center', marginBottom: 24,
        shadowColor: '#4caf50', shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.2, shadowRadius: 16, elevation: 8,
    },
    title: { fontSize: 28, fontWeight: 'bold', color: '#1b5e20', marginBottom: 8 },
    subtitle: { fontSize: 15, color: '#666' },
    emailText: { fontSize: 15, color: '#2e7d32', fontWeight: '700', marginTop: 4 },
    spamNote: { fontSize: 12, color: '#aaa', marginTop: 8 },
    otpContainer: {
        flexDirection: 'row', justifyContent: 'center', gap: 10, marginBottom: 16,
    },
    otpBox: {
        width: 48, height: 60, borderRadius: 12, borderWidth: 2,
        borderColor: '#e9ecef', backgroundColor: '#f8f9fa',
        fontSize: 24, fontWeight: 'bold', color: '#1b5e20',
    },
    otpBoxFilled: { borderColor: '#4caf50', backgroundColor: '#f0faf0' },
    errorText: { color: '#e53935', fontSize: 14, textAlign: 'center', marginBottom: 12 },
    successText: { color: '#4caf50', fontSize: 14, textAlign: 'center', marginBottom: 12 },
    verifyButton: {
        backgroundColor: '#4caf50', borderRadius: 16, height: 60,
        justifyContent: 'center', alignItems: 'center',
        shadowColor: '#4caf50', shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.3, shadowRadius: 16, elevation: 8,
    },
    buttonDisabled: { opacity: 0.7 },
    verifyButtonText: { color: '#fff', fontSize: 18, fontWeight: 'bold', letterSpacing: 1 },
    resendContainer: { flexDirection: 'row', justifyContent: 'center', marginTop: 24 },
    resendText: { fontSize: 15, color: '#888' },
    resendLink: { fontSize: 15, color: '#4caf50', fontWeight: '700' },
});
