import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform, ActivityIndicator, Alert } from 'react-native';
import { Send, User, Bot, HelpCircle } from 'lucide-react-native';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import api from '../../services/api';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
}

export default function ChatScreen() {
    const { t, language } = useLanguage();
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            text: t('chatbotWelcome'),
            sender: 'bot',
            timestamp: new Date(),
        }
    ]);
    const [inputText, setInputText] = useState('');
    const [loading, setLoading] = useState(false);
    const { user, isGuest } = useAuth();
    const flatListRef = useRef<FlatList>(null);

    // If a registered user logs in, load their past conversation
    useEffect(() => {
        if (!isGuest && user) {
            fetchChatHistory();
        }
    }, [user, isGuest]);

    const fetchChatHistory = async () => {
        try {
            const response = await api.get('/chatbot/history');
            if (response.data.length > 0) {
                // Transform server data into our message format
                const historyMessages = response.data.flatMap((chat: any) => [
                    {
                        id: `user-${chat.id}`,
                        text: chat.user_message,
                        sender: 'user',
                        timestamp: new Date(chat.created_at)
                    },
                    {
                        id: `bot-${chat.id}`,
                        text: chat.bot_response,
                        sender: 'bot',
                        timestamp: new Date(chat.created_at)
                    }
                ]);
                setMessages((prev) => [...prev, ...historyMessages]);
            }
        } catch (error) {
            console.error('Failed to fetch chat history', error);
        }
    };

    const handleSend = async () => {
        if (!inputText.trim() || loading) return;

        // 1. Show user's message immediately
        const userMessage: Message = {
            id: Date.now().toString(),
            text: inputText.trim(),
            sender: 'user',
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInputText('');
        setLoading(true);

        try {
            // 2. Send to the AI
            const response = await api.post('/chatbot/message', {
                message: userMessage.text,
                language: language
            });

            // 3. Show AI's response
            const botMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: response.data.response,
                sender: 'bot',
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, botMessage]);
        } catch (error: any) {
            console.error('Chat error', error);
            const errorMessage = error.response?.data?.error || t('chatbotError');

            setMessages((prev) => [
                ...prev,
                {
                    id: (Date.now() + 1).toString(),
                    text: errorMessage,
                    sender: 'bot',
                    timestamp: new Date(),
                }
            ]);
        } finally {
            setLoading(false);
        }
    };

    const renderMessage = ({ item }: { item: Message }) => (
        <View style={[
            styles.messageWrapper,
            item.sender === 'user' ? styles.userWrapper : styles.botWrapper
        ]}>
            <View style={[
                styles.messageIcon,
                item.sender === 'user' ? styles.userIcon : styles.botIcon
            ]}>
                {item.sender === 'user' ? <User size={16} color="#4caf50" /> : <Bot size={16} color="#fff" />}
            </View>
            <View style={[
                styles.messageBubble,
                item.sender === 'user' ? styles.userBubble : styles.botBubble
            ]}>
                <Text style={[
                    styles.messageText,
                    item.sender === 'user' ? styles.userText : styles.botText
                ]}>
                    {item.text}
                </Text>
                <Text style={styles.timestampText}>
                    {item.timestamp.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}
                </Text>
            </View>
        </View>
    );

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior="padding"
            keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 60}
        >
            <View style={styles.header}>
                <Text style={styles.headerTitle}>{t('chatbotTitle')}</Text>
                <View style={styles.onlineStatus}>
                    <View style={styles.onlineDot} />
                    <Text style={styles.onlineText}>{t('chatbotOnline')}</Text>
                </View>
            </View>

            <FlatList
                ref={flatListRef}
                data={messages}
                renderItem={renderMessage}
                keyExtractor={(item) => item.id}
                contentContainerStyle={styles.messageList}
                onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
                onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
            />



            <View style={styles.inputArea}>
                <TextInput
                    style={styles.input}
                    placeholder={t('chatbotPlaceholder')}
                    value={inputText}
                    onChangeText={setInputText}
                    multiline
                    maxLength={500}
                />
                <TouchableOpacity
                    style={[styles.sendButton, (!inputText.trim() || loading) && styles.sendButtonDisabled]}
                    onPress={handleSend}
                    disabled={!inputText.trim() || loading}
                >
                    {loading ? (
                        <ActivityIndicator color="#fff" size="small" />
                    ) : (
                        <Send color="#fff" size={20} />
                    )}
                </TouchableOpacity>
            </View>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
    },
    header: {
        paddingTop: 60,
        paddingHorizontal: 20,
        paddingBottom: 15,
        backgroundColor: '#fff',
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    headerTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
    },
    onlineStatus: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    onlineDot: {
        width: 8,
        height: 8,
        borderRadius: 4,
        backgroundColor: '#4caf50',
        marginRight: 6,
    },
    onlineText: {
        fontSize: 12,
        color: '#666',
    },
    messageList: {
        padding: 16,
        paddingBottom: 20,
    },
    messageWrapper: {
        flexDirection: 'row',
        marginBottom: 20,
        maxWidth: '85%',
    },
    userWrapper: {
        alignSelf: 'flex-end',
        flexDirection: 'row-reverse',
    },
    botWrapper: {
        alignSelf: 'flex-start',
    },
    messageIcon: {
        width: 32,
        height: 32,
        borderRadius: 16,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 4,
    },
    userIcon: {
        backgroundColor: '#e8f5e9',
        marginLeft: 8,
    },
    botIcon: {
        backgroundColor: '#4caf50',
        marginRight: 8,
    },
    messageBubble: {
        padding: 12,
        borderRadius: 16,
        elevation: 1,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 2,
    },
    userBubble: {
        backgroundColor: '#4caf50',
        borderTopRightRadius: 4,
    },
    botBubble: {
        backgroundColor: '#f1f1f1',
        borderTopLeftRadius: 4,
    },
    messageText: {
        fontSize: 15,
        lineHeight: 22,
    },
    userText: {
        color: '#fff',
    },
    botText: {
        color: '#333',
    },
    timestampText: {
        fontSize: 10,
        marginTop: 4,
        alignSelf: 'flex-end',
        color: 'rgba(0,0,0,0.4)',
    },
    inputArea: {
        flexDirection: 'row',
        padding: 12,
        borderTopWidth: 1,
        borderTopColor: '#eee',
        alignItems: 'center',
        backgroundColor: '#fff',
    },
    input: {
        flex: 1,
        backgroundColor: '#f8f8f8',
        borderRadius: 24,
        paddingHorizontal: 16,
        paddingVertical: 8,
        marginRight: 8,
        fontSize: 15,
        maxHeight: 100,
    },
    sendButton: {
        width: 44,
        height: 44,
        borderRadius: 22,
        backgroundColor: '#4caf50',
        justifyContent: 'center',
        alignItems: 'center',
    },
    sendButtonDisabled: {
        backgroundColor: '#ccc',
    },
    guestReminder: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 4,
        backgroundColor: '#fffbe6',
    },
    guestReminderText: {
        fontSize: 12,
        color: '#666',
        marginLeft: 6,
    },
});
