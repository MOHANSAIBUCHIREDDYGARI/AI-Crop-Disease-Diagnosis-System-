import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useRouter, Stack } from 'expo-router';
import { Shield, ChevronLeft, Lock, EyeOff, FileText } from 'lucide-react-native';
import { useLanguage } from '../context/LanguageContext';

export default function PrivacyScreen() {
    const router = useRouter();
    const { t } = useLanguage();

    return (
        <View style={styles.container}>
            <Stack.Screen options={{
                headerShown: true,
                title: t('privacyPolicy'),
                headerLeft: () => (
                    <TouchableOpacity onPress={() => router.back()} style={{ marginLeft: 10 }}>
                        <ChevronLeft size={24} color="#333" />
                    </TouchableOpacity>
                )
            }} />

            <ScrollView contentContainerStyle={styles.scrollContent}>
                <View style={styles.header}>
                    <View style={styles.iconCircle}>
                        <Shield size={40} color="#2196f3" />
                    </View>
                    <Text style={styles.title}>{t('privacyPolicyTitle')}</Text>
                    <Text style={styles.subtitle}>{t('privacySubtitle')}</Text>
                </View>

                <View style={styles.contentCard}>
                    <View style={styles.policyItem}>
                        <Lock size={20} color="#2196f3" />
                        <Text style={styles.policyTitle}>{t('privacyDataSecurityTitle')}</Text>
                        <Text style={styles.policyText}>
                            {t('privacyDataSecurityText')}
                        </Text>
                    </View>

                    <View style={styles.policyItem}>
                        <EyeOff size={20} color="#2196f3" />
                        <Text style={styles.policyTitle}>{t('privacyDataUsageTitle')}</Text>
                        <Text style={styles.policyText}>
                            {t('privacyDataUsageText')}
                        </Text>
                    </View>

                    <View style={styles.policyItem}>
                        <FileText size={20} color="#2196f3" />
                        <Text style={styles.policyTitle}>{t('privacyTransparencyTitle')}</Text>
                        <Text style={styles.policyText}>
                            {t('privacyTransparencyText')}
                        </Text>
                    </View>
                </View>

                <Text style={styles.footerInfo}>{t('privacyLastUpdated')}</Text>
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8f9fa',
    },
    scrollContent: {
        padding: 24,
    },
    header: {
        alignItems: 'center',
        marginBottom: 32,
    },
    iconCircle: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: '#e3f2fd',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 16,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 16,
        color: '#666',
    },
    contentCard: {
        backgroundColor: '#fff',
        borderRadius: 16,
        padding: 20,
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    policyItem: {
        marginBottom: 24,
    },
    policyTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginTop: 8,
        marginBottom: 8,
    },
    policyText: {
        fontSize: 14,
        color: '#555',
        lineHeight: 22,
    },
    footerInfo: {
        textAlign: 'center',
        marginTop: 32,
        color: '#999',
        fontSize: 12,
    }
});
