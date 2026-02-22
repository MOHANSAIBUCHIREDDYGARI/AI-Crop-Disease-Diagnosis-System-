import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useRouter, Stack } from 'expo-router';
import { HelpCircle, ChevronLeft, Mail, Info, Camera, Zap } from 'lucide-react-native';
import { useLanguage } from '../context/LanguageContext';

export default function HelpScreen() {
    const router = useRouter();
    const { t } = useLanguage();

    return (
        <View style={styles.container}>
            <Stack.Screen options={{ 
                headerShown: true, 
                title: t('helpCenter'),
                headerLeft: () => (
                    <TouchableOpacity onPress={() => router.back()} style={{ marginLeft: 10 }}>
                        <ChevronLeft size={24} color="#333" />
                    </TouchableOpacity>
                )
            }} />
            
            <ScrollView contentContainerStyle={styles.scrollContent}>
                <View style={styles.header}>
                    <View style={styles.iconCircle}>
                        <HelpCircle size={40} color="#4caf50" />
                    </View>
                    <Text style={styles.title}>Welcome to Help Center</Text>
                    <Text style={styles.subtitle}>How can we help you today?</Text>
                </View>

                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Quick Start Guide</Text>
                    
                    <View style={styles.guideItem}>
                        <Camera size={24} color="#4caf50" />
                        <View style={styles.guideText}>
                            <Text style={styles.guideLabel}>How to scan</Text>
                            <Text style={styles.guideDesc}>Point your camera at a crop leaf and tap 'Scan'. Ensure the leaf fills the frame.</Text>
                        </View>
                    </View>

                    <View style={styles.guideItem}>
                        <Zap size={24} color="#4caf50" />
                        <View style={styles.guideText}>
                            <Text style={styles.guideLabel}>Best Results</Text>
                            <Text style={styles.guideDesc}>Ensure good natural lighting and a clear focus for maximum accuracy.</Text>
                        </View>
                    </View>

                    <View style={styles.guideItem}>
                        <Info size={24} color="#4caf50" />
                        <View style={styles.guideText}>
                            <Text style={styles.guideLabel}>Supported Crops</Text>
                            <Text style={styles.guideDesc}>Our AI currently supports Tomato, Rice, Potato, Grape, and Maize.</Text>
                        </View>
                    </View>
                </View>

                <View style={styles.contactCard}>
                    <Mail size={24} color="#fff" />
                    <Text style={styles.contactTitle}>Still need help?</Text>
                    <Text style={styles.contactText}>Contact our support team at:</Text>
                    <Text style={styles.contactEmail}>support@smartcrophealth.com</Text>
                </View>
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
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
        backgroundColor: '#e8f5e9',
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
    section: {
        marginBottom: 32,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 16,
    },
    guideItem: {
        flexDirection: 'row',
        marginBottom: 20,
        alignItems: 'flex-start',
    },
    guideText: {
        marginLeft: 16,
        flex: 1,
    },
    guideLabel: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 4,
    },
    guideDesc: {
        fontSize: 14,
        color: '#666',
        lineHeight: 20,
    },
    contactCard: {
        backgroundColor: '#4caf50',
        borderRadius: 16,
        padding: 24,
        alignItems: 'center',
    },
    contactTitle: {
        color: '#fff',
        fontSize: 20,
        fontWeight: 'bold',
        marginTop: 12,
        marginBottom: 8,
    },
    contactText: {
        color: '#e8f5e9',
        fontSize: 14,
        marginBottom: 4,
    },
    contactEmail: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
});
