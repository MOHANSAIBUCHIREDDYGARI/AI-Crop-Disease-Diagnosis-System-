import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator, Image, RefreshControl } from 'react-native';
import { useRouter, useNavigation } from 'expo-router';
import { Calendar, ChevronRight, Search, Filter, History as HistoryIcon, LogIn } from 'lucide-react-native';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import api from '../../services/api';

export default function HistoryScreen() {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [refreshing, setRefreshing] = useState(false);
    const { user, isGuest } = useAuth();
    const { t } = useLanguage();
    const router = useRouter();

    useEffect(() => {
        if (!isGuest && user) {
            fetchHistory();
        }
    }, [user, isGuest]);

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const response = await api.get('/diagnosis/history');
            setHistory(response.data);
        } catch (error) {
            console.error('Failed to fetch history', error);
        } finally {
            setLoading(false);
        }
    };

    const onRefresh = React.useCallback(() => {
        setRefreshing(true);
        fetchHistory().then(() => setRefreshing(false));
    }, []);

    const handleItemPress = async (id: number) => {
        setLoading(true);
        try {
            const response = await api.get(`/diagnosis/${id}`);
            router.push({
                pathname: '/results',
                params: { data: JSON.stringify(response.data) }
            });
        } catch (error) {
            console.error('Failed to fetch diagnosis details', error);
        } finally {
            setLoading(false);
        }
    };

    if (isGuest) {
        return (
            <View style={styles.guestContainer}>
                <View style={styles.guestContent}>
                    <View style={styles.guestIconCircle}>
                        <HistoryIcon size={48} color="#4caf50" />
                    </View>
                    <Text style={styles.guestTitle}>{t('saveYourHistory')}</Text>
                    <Text style={styles.guestSubtitle}>{t('guestHistorySubtitle')}</Text>
                    <TouchableOpacity style={styles.loginButton} onPress={() => router.replace('/login')}>
                        <LogIn color="#fff" size={20} style={{ marginRight: 8 }} />
                        <Text style={styles.loginButtonText}>{t('loginRegister')}</Text>
                    </TouchableOpacity>
                </View>
            </View>
        );
    }

    const renderItem = ({ item }: any) => (
        <TouchableOpacity style={styles.historyCard} onPress={() => handleItemPress(item.id)}>
            <View style={styles.cardContent}>
                <View style={styles.cropIcon}>
                    <Text style={styles.cropLetter}>{item.crop.charAt(0).toUpperCase()}</Text>
                </View>
                <View style={styles.itemInfo}>
                    <Text style={styles.itemTitle}>{item.disease.replace(/___/g, ': ').replace(/_/g, ' ')}</Text>
                    <View style={styles.itemMeta}>
                        <Calendar size={12} color="#888" />
                        <Text style={styles.itemDate}>{new Date(item.created_at).toLocaleDateString()}</Text>
                        <View style={styles.dot} />
                        <Text style={styles.itemCrop}>{item.crop.toUpperCase()}</Text>
                    </View>
                </View>
                <View style={styles.rightContent}>
                    <Text style={[styles.confidence, { color: item.confidence > 80 ? '#4caf50' : '#ff9800' }]}>
                        {item.confidence.toFixed(1)}%
                    </Text>
                    <ChevronRight size={20} color="#ccc" />
                </View>
            </View>
        </TouchableOpacity>
    );

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>Diagnosis History</Text>
                <TouchableOpacity style={styles.searchButton}>
                    <Search size={22} color="#333" />
                </TouchableOpacity>
            </View>

            {loading && !refreshing ? (
                <View style={styles.loader}>
                    <ActivityIndicator size="large" color="#4caf50" />
                </View>
            ) : history.length > 0 ? (
                <FlatList
                    data={history}
                    renderItem={renderItem}
                    keyExtractor={(item) => item.id.toString()}
                    contentContainerStyle={styles.list}
                    refreshControl={
                        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#4caf50']} />
                    }
                />
            ) : (
                <View style={styles.emptyContainer}>
                    <HistoryIcon size={64} color="#eee" />
                    <Text style={styles.emptyText}>No diagnoses yet</Text>
                    <Text style={styles.emptySubtext}>Your past crop diagnoses will appear here.</Text>
                    <TouchableOpacity style={styles.startButton} onPress={() => router.replace('/(tabs)')}>
                        <Text style={styles.startButtonText}>Start New Diagnosis</Text>
                    </TouchableOpacity>
                </View>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8f8f8',
    },
    header: {
        paddingTop: 60,
        paddingHorizontal: 20,
        paddingBottom: 20,
        backgroundColor: '#fff',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
    },
    searchButton: {
        padding: 8,
    },
    list: {
        padding: 16,
    },
    historyCard: {
        backgroundColor: '#fff',
        borderRadius: 12,
        marginBottom: 12,
        padding: 16,
        elevation: 1,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 2,
    },
    cardContent: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    cropIcon: {
        width: 48,
        height: 48,
        borderRadius: 24,
        backgroundColor: '#e8f5e9',
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 16,
    },
    cropLetter: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#2e7d32',
    },
    itemInfo: {
        flex: 1,
    },
    itemTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 4,
    },
    itemMeta: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    itemDate: {
        fontSize: 12,
        color: '#888',
        marginLeft: 4,
    },
    dot: {
        width: 3,
        height: 3,
        borderRadius: 1.5,
        backgroundColor: '#ccc',
        marginHorizontal: 8,
    },
    itemCrop: {
        fontSize: 10,
        fontWeight: 'bold',
        color: '#4caf50',
        letterSpacing: 0.5,
    },
    rightContent: {
        alignItems: 'flex-end',
        marginLeft: 8,
    },
    confidence: {
        fontSize: 14,
        fontWeight: 'bold',
        marginBottom: 4,
    },
    loader: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 40,
    },
    emptyText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginTop: 16,
    },
    emptySubtext: {
        fontSize: 14,
        color: '#888',
        textAlign: 'center',
        marginTop: 8,
        marginBottom: 24,
    },
    startButton: {
        backgroundColor: '#4caf50',
        paddingHorizontal: 24,
        paddingVertical: 12,
        borderRadius: 24,
    },
    startButtonText: {
        color: '#fff',
        fontWeight: 'bold',
    },
    guestContainer: {
        flex: 1,
        backgroundColor: '#fff',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 32,
    },
    guestContent: {
        alignItems: 'center',
    },
    guestIconCircle: {
        width: 100,
        height: 100,
        borderRadius: 50,
        backgroundColor: '#f1f8e9',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 24,
    },
    guestTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 12,
    },
    guestSubtitle: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
        lineHeight: 24,
        marginBottom: 32,
    },
    loginButton: {
        flexDirection: 'row',
        backgroundColor: '#4caf50',
        paddingHorizontal: 32,
        paddingVertical: 16,
        borderRadius: 30,
        alignItems: 'center',
        elevation: 4,
    },
    loginButtonText: {
        color: '#fff',
        fontSize: 18,
        fontWeight: 'bold',
    },
});
