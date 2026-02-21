
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useLanguage } from '../context/LanguageContext';

interface ConfidenceBarProps {
    confidence: number;
    label?: string;
}

/**
 * A colorful bar showing how sure the AI is about its guess.
 * Green = Very sure
 * Yellow = Pretty sure
 * Red = Not so sure (might be wrong)
 */
const ConfidenceBar: React.FC<ConfidenceBarProps> = ({ confidence, label }) => {
    const { t } = useLanguage();

    const getBarColor = () => {
        if (confidence > 80) return '#4caf50'; // Green
        if (confidence > 50) return '#ffeb3b'; // Yellow
        return '#f44336'; // Red
    };

    return (
        <View style={styles.container}>
            <View style={styles.labelContainer}>
                <Text style={styles.label}>{label || t('confidenceScore')}</Text>
                <Text style={styles.value}>{confidence.toFixed(1)}%</Text>
            </View>
            <View style={styles.barBackground}>
                <View
                    style={[
                        styles.barFill,
                        { width: `${confidence}%`, backgroundColor: getBarColor() }
                    ]}
                />
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        marginVertical: 10,
        width: '100%',
    },
    labelContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 5,
    },
    label: {
        fontSize: 14,
        color: '#666',
        fontWeight: '600',
    },
    value: {
        fontSize: 14,
        color: '#333',
        fontWeight: 'bold',
    },
    barBackground: {
        height: 10,
        backgroundColor: '#eee',
        borderRadius: 5,
        overflow: 'hidden',
    },
    barFill: {
        height: '100%',
        borderRadius: 5,
    },
});

export default ConfidenceBar;
