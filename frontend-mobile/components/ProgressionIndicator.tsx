import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { AlertCircle, AlertTriangle, AlertOctagon } from 'lucide-react-native';
import { useLanguage } from '../context/LanguageContext';


interface ProgressionIndicatorProps {
    severity: number; // 0-100
    stage?: string;
}

const ProgressionIndicator: React.FC<ProgressionIndicatorProps> = ({ severity, stage }) => {
    const { t } = useLanguage();
    const getSeverityLevel = () => {
        if (severity < 30) return { level: t('earlyStage'), color: '#4caf50', icon: AlertCircle, bg: '#e8f5e9' };
        if (severity < 60) return { level: t('moderateStage'), color: '#ff9800', icon: AlertTriangle, bg: '#fff3e0' };
        return { level: t('severeStage'), color: '#d32f2f', icon: AlertOctagon, bg: '#ffebee' };
    };

    const severityInfo = getSeverityLevel();
    const Icon = severityInfo.icon;

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Icon size={24} color={severityInfo.color} />
                <View style={styles.headerText}>
                    <Text style={styles.title}>{t('diseaseProgression')}</Text>
                    <Text style={[styles.level, { color: severityInfo.color }]}>
                        {severityInfo.level}
                    </Text>
                </View>
            </View>

            <View style={styles.progressBarContainer}>
                <View style={styles.progressBarBg}>
                    <View
                        style={[
                            styles.progressBarFill,
                            {
                                width: `${severity}%`,
                                backgroundColor: severityInfo.color,
                            },
                        ]}
                    />
                </View>
                <Text style={styles.percentageText}>{severity.toFixed(1)}%</Text>
            </View>

            <View style={[styles.infoCard, { backgroundColor: severityInfo.bg }]}>
                <Text style={[styles.infoText, { color: severityInfo.color }]}>
                    {severity < 30 && t('earlyDetectionTip')}
                    {severity >= 30 && severity < 60 && t('moderateInfectionTip')}
                    {severity >= 60 && t('severeInfectionTip')}
                </Text>
            </View>

            {stage && (
                <View style={styles.stageInfo}>
                    <Text style={styles.stageLabel}>{t('currentStage')}</Text>
                    <Text style={styles.stageValue}>{stage}</Text>
                </View>
            )}
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
        marginBottom: 16,
    },
    headerText: {
        marginLeft: 12,
        flex: 1,
    },
    title: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
    },
    level: {
        fontSize: 14,
        fontWeight: '600',
        marginTop: 2,
    },
    progressBarContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 16,
    },
    progressBarBg: {
        flex: 1,
        height: 12,
        backgroundColor: '#e0e0e0',
        borderRadius: 6,
        overflow: 'hidden',
    },
    progressBarFill: {
        height: '100%',
        borderRadius: 6,
    },
    percentageText: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
        marginLeft: 12,
        width: 50,
    },
    infoCard: {
        padding: 12,
        borderRadius: 8,
        marginBottom: 12,
    },
    infoText: {
        fontSize: 14,
        fontWeight: '600',
        lineHeight: 20,
    },
    stageInfo: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingTop: 12,
        borderTopWidth: 1,
        borderTopColor: '#f0f0f0',
    },
    stageLabel: {
        fontSize: 14,
        color: '#666',
    },
    stageValue: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#333',
    },
});

export default ProgressionIndicator;
