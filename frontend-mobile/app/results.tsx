import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity, Share, Alert } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Audio } from 'expo-av';
import { Volume2, Share2, CornerUpRight, Info, AlertTriangle, ShieldCheck, Download, Headphones, Check } from 'lucide-react-native';
import ConfidenceBar from '../components/ConfidenceBar';
import PesticideCard from '../components/PesticideCard';
import CostCalculator from '../components/CostCalculator';
import ProgressionIndicator from '../components/ProgressionIndicator';
import api from '../services/api';
import { useLanguage } from '../context/LanguageContext';



export default function ResultsScreen() {
    const { data } = useLocalSearchParams();
    const { t } = useLanguage();
    const [result, setResult] = useState<any>(null);
    const [sound, setSound] = useState<Audio.Sound | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const router = useRouter();

    useEffect(() => {
        if (data) {
            setResult(JSON.parse(data as string));
        }

        return () => {
            if (sound) {
                sound.unloadAsync();
            }
        };
    }, [data]);

    const playVoice = async () => {
        if (!result?.voice_file) return;

        try {
            if (sound) {
                if (isPlaying) {
                    await sound.pauseAsync();
                    setIsPlaying(false);
                } else {
                    await sound.playAsync();
                    setIsPlaying(true);
                }
                return;
            }

            setIsPlaying(true);
            const { sound: newSound } = await Audio.Sound.createAsync(
                { uri: `http://localhost:5000${result.voice_file}` },
                { shouldPlay: true }
            );
            setSound(newSound);

            newSound.setOnPlaybackStatusUpdate((status: any) => {
                if (status.didJustFinish) {
                    setIsPlaying(false);
                }
            });
        } catch (error) {
            console.error('Error playing sound', error);
            Alert.alert('Error', 'Failed to play voice explanation');
            setIsPlaying(false);
        }
    };

    const handleShare = async () => {
        try {
            await Share.share({
                message: `Crop Diagnosis Result: ${result.prediction.crop} - ${result.prediction.disease.replace(/_/g, ' ')}\nConfidence: ${result.prediction.confidence.toFixed(1)}%\nSeverity: ${result.prediction.severity_percent.toFixed(1)}%`,
            });
        } catch (error) {
            console.error('Error sharing', error);
        }
    };

    if (!result) return <View style={styles.container} />;

    const { prediction, disease_info, pesticide_recommendations, weather_advice } = result;

    return (
        <ScrollView style={styles.container}>
            <View style={[styles.statusBanner, { backgroundColor: prediction.confidence > 80 ? '#e8f5e9' : '#fff3e0' }]}>
                {prediction.confidence > 80 ? (
                    <ShieldCheck color="#2e7d32" size={24} />
                ) : (
                    <AlertTriangle color="#ef6c00" size={24} />
                )}
                <Text style={[styles.statusText, { color: prediction.confidence > 80 ? '#2e7d32' : '#ef6c00' }]}>
                    {prediction.disease === 'Healthy' ? t('healthyCrop') : t('potentialDisease')}
                </Text>
            </View>

            <View style={styles.section}>
                <View style={styles.titleRow}>
                    <Text style={styles.cropTitle}>{t(`crop_${prediction.crop.toLowerCase()}` as any)}</Text>
                    <View style={styles.stageBadge}>
                        <Text style={styles.stageText}>{t(`stage_${prediction.stage.split(' ')[0].toLowerCase()}` as any) || prediction.stage}</Text>
                    </View>
                </View>
                <Text style={styles.diseaseName}>{prediction.disease_local || prediction.disease.replace(/___/g, ': ').replace(/_/g, ' ')}</Text>

                <ConfidenceBar confidence={prediction.confidence} />

                <View style={styles.statsRow}>
                    <View style={styles.statBox}>
                        <Text style={styles.statLabel}>{t('severity')}</Text>
                        <Text style={styles.statValue}>{prediction.severity_percent.toFixed(1)}%</Text>
                    </View>
                    <View style={styles.statBox}>
                        <Text style={styles.statLabel}>{t('diagnosisId')}</Text>
                        <Text style={styles.statValue}>#{result.diagnosis_id || 'N/A'}</Text>
                    </View>
                </View>
            </View>

            {/* Disease Progression Indicator */}
            {prediction.disease !== 'Healthy' && (
                <View style={{ paddingHorizontal: 20 }}>
                    <ProgressionIndicator
                        severity={prediction.severity_percent}
                        stage={prediction.stage}
                    />
                </View>
            )}

            <View style={styles.actionButtons}>
                <TouchableOpacity style={styles.actionButton} onPress={playVoice}>
                    {isPlaying ? <Headphones size={20} color="#fff" /> : <Volume2 size={20} color="#fff" />}
                    <Text style={styles.actionButtonText}>{isPlaying ? t('pauseExplanation') : t('voiceExplanation')}</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.actionButton, styles.secondaryButton]} onPress={handleShare}>
                    <Share2 size={20} color="#4caf50" />
                    <Text style={[styles.actionButtonText, styles.secondaryButtonText]}>{t('shareReport')}</Text>
                </TouchableOpacity>
            </View>

            {weather_advice && (
                <View style={styles.weatherBox}>
                    <Info size={20} color="#1976d2" />
                    <View style={styles.weatherContent}>
                        <Text style={styles.weatherTitle}>{t('weatherAdvice')}</Text>
                        <Text style={styles.weatherText}>{weather_advice}</Text>
                    </View>
                </View>
            )}

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>{t('diseaseInfo')}</Text>
                <Text style={styles.infoText}>{disease_info.description}</Text>
                <Text style={styles.subSubtitle}>{t('symptoms')}</Text>
                <Text style={styles.infoText}>{disease_info.symptoms}</Text>
            </View>

            {prediction.disease !== 'Healthy' && (
                <>
                    <View style={styles.section}>
                        <View style={styles.sectionHeader}>
                            <Text style={styles.sectionTitle}>{t('treatmentPlan')}</Text>
                            <View style={[styles.urgencyBadge, { backgroundColor: pesticide_recommendations.urgency === 'high' ? '#ffebee' : '#e8f5e9' }]}>
                                <Text style={[styles.urgencyText, { color: pesticide_recommendations.urgency === 'high' ? '#d32f2f' : '#2e7d32' }]}>
                                    {pesticide_recommendations.urgency.toUpperCase()} {t('urgency')}
                                </Text>
                            </View>
                        </View>

                        <Text style={styles.approachText}>{pesticide_recommendations.treatment_approach}</Text>

                        <Text style={styles.subSubtitle}>{t('recommendedPesticides')}</Text>
                        {pesticide_recommendations.recommended_pesticides.map((pest: any, index: number) => (
                            <PesticideCard key={index} pesticide={pest} />
                        ))}
                    </View>

                    {/* Cost Calculator */}
                    <View style={{ paddingHorizontal: 20 }}>
                        <CostCalculator
                            pesticides={pesticide_recommendations.recommended_pesticides}
                            preventionCostPerAcre={500}
                        />
                    </View>
                </>
            )}

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>{t('preventionBestPractices')}</Text>
                <Text style={styles.infoText}>{disease_info.prevention_steps}</Text>

                {disease_info.organic_alternatives && (
                    <>
                        <Text style={styles.subSubtitle}>{t('organicAlternatives')}</Text>
                        <Text style={styles.infoText}>{disease_info.organic_alternatives}</Text>
                    </>
                )}
            </View>

            <TouchableOpacity style={styles.doneButton} onPress={() => router.replace('/(tabs)')}>
                <Check color="#fff" size={20} style={{ marginRight: 8 }} />
                <Text style={styles.doneButtonText}>{t('finishDiagnosis')}</Text>
            </TouchableOpacity>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    statusBanner: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 16,
        marginBottom: 12,
    },
    statusText: {
        fontSize: 16,
        fontWeight: 'bold',
        marginLeft: 12,
    },
    section: {
        backgroundColor: '#fff',
        padding: 20,
        marginBottom: 12,
    },
    titleRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    cropTitle: {
        fontSize: 14,
        color: '#666',
        fontWeight: 'bold',
        letterSpacing: 1,
    },
    stageBadge: {
        backgroundColor: '#f0f0f0',
        paddingHorizontal: 10,
        paddingVertical: 4,
        borderRadius: 12,
    },
    stageText: {
        fontSize: 12,
        color: '#444',
    },
    diseaseName: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 16,
    },
    statsRow: {
        flexDirection: 'row',
        marginTop: 16,
        gap: 16,
    },
    statBox: {
        flex: 1,
        backgroundColor: '#f9f9f9',
        padding: 12,
        borderRadius: 8,
        alignItems: 'center',
    },
    statLabel: {
        fontSize: 12,
        color: '#888',
        marginBottom: 4,
    },
    statValue: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
    },
    actionButtons: {
        flexDirection: 'row',
        paddingHorizontal: 20,
        gap: 12,
        marginBottom: 20,
    },
    actionButton: {
        flex: 2,
        backgroundColor: '#4caf50',
        flexDirection: 'row',
        height: 48,
        borderRadius: 24,
        justifyContent: 'center',
        alignItems: 'center',
        elevation: 2,
    },
    secondaryButton: {
        flex: 1,
        backgroundColor: '#fff',
        borderWidth: 1,
        borderColor: '#4caf50',
    },
    actionButtonText: {
        color: '#fff',
        fontWeight: 'bold',
        marginLeft: 8,
    },
    secondaryButtonText: {
        color: '#4caf50',
    },
    weatherBox: {
        backgroundColor: '#e3f2fd',
        marginHorizontal: 20,
        padding: 16,
        borderRadius: 12,
        flexDirection: 'row',
        marginBottom: 20,
    },
    weatherContent: {
        marginLeft: 12,
        flex: 1,
    },
    weatherTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#1976d2',
        marginBottom: 4,
    },
    weatherText: {
        fontSize: 14,
        color: '#444',
        lineHeight: 20,
    },
    sectionHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 16,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 12,
    },
    urgencyBadge: {
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 6,
    },
    urgencyText: {
        fontSize: 10,
        fontWeight: '900',
    },
    approachText: {
        fontSize: 14,
        color: '#555',
        lineHeight: 22,
        marginBottom: 16,
        fontStyle: 'italic',
    },
    subSubtitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#444',
        marginTop: 12,
        marginBottom: 8,
    },
    infoText: {
        fontSize: 15,
        color: '#555',
        lineHeight: 24,
    },
    doneButton: {
        backgroundColor: '#333',
        margin: 20,
        height: 56,
        borderRadius: 12,
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 40,
    },
    doneButtonText: {
        color: '#fff',
        fontSize: 18,
        fontWeight: 'bold',
    },
});
