
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { ShieldCheck, ShieldAlert, BadgeInfo } from 'lucide-react-native';
import { useLanguage } from '../context/LanguageContext';

interface Pesticide {
    name: string;
    dosage_per_acre: string;
    frequency: string;
    cost_per_liter: number;
    is_organic: boolean;
    warnings?: string;
}

/**
 * A handy card that displays the details of a recommended medicine.
 * Shows if it's Organic (Safe) or Chemical (Effective but use with caution).
 */
const PesticideCard: React.FC<{ pesticide: Pesticide }> = ({ pesticide }) => {
    const { t } = useLanguage();

    return (
        <View style={styles.card}>
            <View style={styles.header}>
                <Text style={styles.name}>{pesticide.name}</Text>
                {pesticide.is_organic ? (
                    <View style={styles.organicBadge}>
                        <ShieldCheck size={14} color="#fff" />
                        <Text style={styles.organicText}>{t('organic')}</Text>
                    </View>
                ) : (
                    <View style={[styles.organicBadge, { backgroundColor: '#ff9800' }]}>
                        <ShieldAlert size={14} color="#fff" />
                        <Text style={styles.organicText}>{t('chemical')}</Text>
                    </View>
                )}
            </View>

            <View style={styles.infoRow}>
                <Text style={styles.label}>{t('dosage')}:</Text>
                <Text style={styles.value}>{pesticide.dosage_per_acre}</Text>
            </View>

            <View style={styles.infoRow}>
                <Text style={styles.label}>{t('frequency')}:</Text>
                <Text style={styles.value}>{pesticide.frequency}</Text>
            </View>

            <View style={styles.infoRow}>
                <Text style={styles.label}>{t('estPrice')}:</Text>
                <Text style={styles.value}>₹{pesticide.cost_per_liter} / L</Text>
            </View>

            {pesticide.warnings && (
                <View style={styles.warningBox}>
                    <BadgeInfo size={16} color="#d32f2f" />
                    <Text style={styles.warningText}>{pesticide.warnings}</Text>
                </View>
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        elevation: 3,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        borderLeftWidth: 4,
        borderLeftColor: '#4caf50',
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
    name: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
    },
    organicBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#4caf50',
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 12,
    },
    organicText: {
        color: '#fff',
        fontSize: 12,
        fontWeight: 'bold',
        marginLeft: 4,
    },
    infoRow: {
        flexDirection: 'row',
        marginBottom: 6,
    },
    label: {
        fontSize: 14,
        color: '#666',
        width: 80,
    },
    value: {
        fontSize: 14,
        color: '#333',
        fontWeight: '600',
        flex: 1,
    },
    warningBox: {
        flexDirection: 'row',
        backgroundColor: '#ffebee',
        padding: 10,
        borderRadius: 8,
        marginTop: 10,
        alignItems: 'center',
    },
    warningText: {
        color: '#d32f2f',
        fontSize: 12,
        marginLeft: 8,
        flex: 1,
    },
});

export default PesticideCard;
