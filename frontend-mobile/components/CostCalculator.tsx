import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity } from 'react-native';
import { Calculator, TrendingUp, TrendingDown } from 'lucide-react-native';
import { useLanguage } from '../context/LanguageContext';
import { useAppTheme } from '../context/ThemeContext';
import { Colors } from '../constants/theme';
import { T } from './ui/T';

interface Pesticide {
    name: string;
    dosage_per_acre: string;
    cost_per_liter: number;
}

interface CostCalculatorProps {
    pesticides: Pesticide[];
    preventionCostPerAcre?: number;
}

/**
 * A simple tool to help farmers budget for treatment.
 * It compares the cost of curing the disease vs. preventing it.
 */
const CostCalculator: React.FC<CostCalculatorProps> = ({ pesticides, preventionCostPerAcre = 500 }) => {
    const { t } = useLanguage();
    const { isDarkMode, colorScheme } = useAppTheme();
    const themeParams = Colors[colorScheme];
    const [landArea, setLandArea] = useState('1');
    const [unit, setUnit] = useState<'acres' | 'hectares'>('acres');

    const parseArea = () => {
        const area = parseFloat(landArea) || 0;
        // Convert hectares to acres because our math is based on acres
        return unit === 'hectares' ? area * 2.47105 : area;
    };

    const calculateCosts = () => {
        const areaInAcres = parseArea();
        let totalTreatmentCost = 0;

        pesticides.forEach(pesticide => {
            // Extract numbers from strings like "2.5-3.0 liters/acre"
            const dosageStr = String((pesticide as any).dosage_per_acre || (pesticide as any).dosage || '0');
            const dosageMatch = dosageStr.match(/(\d+\.?\d*)-?(\d+\.?\d*)?/);
            if (dosageMatch) {
                const min = parseFloat(dosageMatch[1]);
                const max = dosageMatch[2] ? parseFloat(dosageMatch[2]) : min;
                const avgDosage = (min + max) / 2;
                const cost = (pesticide as any).cost_per_liter || (pesticide as any).cost_per_unit || 0;
                totalTreatmentCost += avgDosage * areaInAcres * cost;
            }
        });

        const totalPreventionCost = preventionCostPerAcre * areaInAcres;
        const savings = totalTreatmentCost - totalPreventionCost;

        return {
            treatment: totalTreatmentCost,
            prevention: totalPreventionCost,
            savings: savings > 0 ? savings : 0,
        };
    };

    const costs = calculateCosts();

    return (
        <View style={[styles.container, { backgroundColor: isDarkMode ? '#2c2c2c' : '#fff' }]}>
            <View style={styles.header}>
                <Calculator size={24} color="#4caf50" />
                <Text style={[styles.title, { color: isDarkMode ? '#fff' : '#333' }]}>{t('costEstimation')}</Text>
            </View>

            <View style={styles.inputSection}>
                <Text style={[styles.label, { color: isDarkMode ? '#aaa' : '#666' }]}>{t('landArea')}:</Text>
                <View style={styles.inputRow}>
                    <TextInput
                        style={[styles.input, { backgroundColor: isDarkMode ? '#1e1e1e' : '#f5f5f5', color: isDarkMode ? '#fff' : '#000', borderColor: isDarkMode ? '#444' : '#e0e0e0' }]}
                        value={landArea}
                        onChangeText={setLandArea}
                        keyboardType="decimal-pad"
                        placeholder={t('enterArea')}
                        placeholderTextColor={isDarkMode ? '#888' : '#aaa'}
                    />
                    <View style={[styles.unitSelector, { backgroundColor: isDarkMode ? '#1e1e1e' : '#f5f5f5' }]}>
                        <TouchableOpacity
                            style={[styles.unitButton, unit === 'acres' && styles.unitButtonActive]}
                            onPress={() => setUnit('acres')}
                        >
                            <T style={[styles.unitText, unit === 'acres' && styles.unitTextActive]}>acres</T>
                        </TouchableOpacity>
                        <TouchableOpacity
                            style={[styles.unitButton, unit === 'hectares' && styles.unitButtonActive]}
                            onPress={() => setUnit('hectares')}
                        >
                            <T style={[styles.unitText, unit === 'hectares' && styles.unitTextActive]}>hectares</T>
                        </TouchableOpacity>
                    </View>
                </View>
            </View>

            <View style={styles.resultsSection}>
                {/* Treatment Cost (Expensive!) */}
                <View style={[styles.costCard, { backgroundColor: isDarkMode ? '#4a1515' : '#ffebee' }]}>
                    <TrendingUp size={20} color={isDarkMode ? '#ff8a80' : '#d32f2f'} />
                    <View style={styles.costInfo}>
                        <Text style={[styles.costLabel, { color: isDarkMode ? '#ccc' : '#666' }]}>{t('treatmentCost')}</Text>
                        <Text style={[styles.costValue, { color: isDarkMode ? '#ff8a80' : '#d32f2f' }]}>₹{costs.treatment.toFixed(0)}</Text>
                    </View>
                </View>

                {/* Prevention Cost (Cheaper!) */}
                <View style={[styles.costCard, { backgroundColor: isDarkMode ? '#1a3320' : '#e8f5e9' }]}>
                    <TrendingDown size={20} color={isDarkMode ? '#81c784' : '#2e7d32'} />
                    <View style={styles.costInfo}>
                        <Text style={[styles.costLabel, { color: isDarkMode ? '#ccc' : '#666' }]}>{t('preventionCost')}</Text>
                        <Text style={[styles.costValue, { color: isDarkMode ? '#81c784' : '#2e7d32' }]}>₹{costs.prevention.toFixed(0)}</Text>
                    </View>
                </View>

                {/* Show how much they save by being proactive */}
                {costs.savings > 0 && (
                    <View style={[styles.savingsCard, { backgroundColor: isDarkMode ? '#3e2723' : '#fff3e0', borderColor: isDarkMode ? '#ff9800' : '#ffb74d' }]}>
                        <Text style={[styles.savingsText, { color: isDarkMode ? '#ffb74d' : '#e65100' }]}>
                            💰 {t('savingsMessage')} ₹{costs.savings.toFixed(0)}!
                        </Text>
                    </View>
                )}
            </View>

            <T style={styles.disclaimer}>
                costDisclaimer
            </T>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        backgroundColor: '#fff',
        borderRadius: 16,
        padding: 20,
        marginBottom: 12,
        elevation: 2,
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 20,
    },
    title: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#333',
        marginLeft: 12,
    },
    inputSection: {
        marginBottom: 20,
    },
    label: {
        fontSize: 14,
        color: '#666',
        marginBottom: 8,
        fontWeight: '600',
    },
    inputRow: {
        flexDirection: 'row',
        gap: 12,
    },
    input: {
        flex: 1,
        backgroundColor: '#f5f5f5',
        borderRadius: 12,
        padding: 12,
        fontSize: 16,
        borderWidth: 1,
        borderColor: '#e0e0e0',
    },
    unitSelector: {
        flexDirection: 'row',
        backgroundColor: '#f5f5f5',
        borderRadius: 12,
        padding: 4,
    },
    unitButton: {
        paddingHorizontal: 16,
        paddingVertical: 8,
        borderRadius: 8,
    },
    unitButtonActive: {
        backgroundColor: '#4caf50',
    },
    unitText: {
        fontSize: 14,
        color: '#666',
        fontWeight: '600',
    },
    unitTextActive: {
        color: '#fff',
    },
    resultsSection: {
        gap: 12,
    },
    costCard: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 16,
        borderRadius: 12,
    },
    costInfo: {
        marginLeft: 12,
        flex: 1,
    },
    costLabel: {
        fontSize: 13,
        color: '#666',
        marginBottom: 4,
    },
    costValue: {
        fontSize: 24,
        fontWeight: 'bold',
    },
    savingsCard: {
        backgroundColor: '#fff3e0',
        padding: 16,
        borderRadius: 12,
        borderWidth: 2,
        borderColor: '#ffb74d',
        borderStyle: 'dashed',
    },
    savingsText: {
        fontSize: 15,
        color: '#e65100',
        fontWeight: '600',
        textAlign: 'center',
    },
    disclaimer: {
        fontSize: 11,
        color: '#999',
        fontStyle: 'italic',
        marginTop: 12,
        textAlign: 'center',
    },
});

export default CostCalculator;
