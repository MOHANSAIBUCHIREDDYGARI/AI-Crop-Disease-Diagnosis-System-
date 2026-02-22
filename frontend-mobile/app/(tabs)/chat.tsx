import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform, ActivityIndicator, Image, Alert } from 'react-native';
import { Send, User, Bot, HelpCircle, Video, UploadCloud, Mic, Square } from 'lucide-react-native';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import * as ImagePicker from 'expo-image-picker';
import { Audio } from 'expo-av';
import api from '../../services/api';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
    image?: string;
    mediaType?: 'image' | 'video';
}

export default function ChatScreen() {
    const { t, language } = useLanguage();
    console.log('ChatScreen current language:', language);
    const flatListRef = useRef<FlatList>(null);
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            text: t('chatbotWelcome'),
            sender: 'bot',
            timestamp: new Date(),
        }
    ]);
    const [inputText, setInputText] = useState('');
    const [selectedMedia, setSelectedMedia] = useState<{ uri: string, type: 'image' | 'video' } | null>(null);
    const [loading, setLoading] = useState(false);

    // Upload state
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [serverFilePath, setServerFilePath] = useState<string | null>(null);

    const { user, isGuest } = useAuth();

    // Voice Recording state
    const [recording, setRecording] = useState<Audio.Recording | null>(null);
    const [isRecording, setIsRecording] = useState(false);


    // If a registered user logs in, load their past conversation
    useEffect(() => {
        if (!isGuest && user) {
            fetchChatHistory();
        }

        // Update the very first welcome message when language changes
        setMessages(prev => {
            const newMessages = [...prev];
            if (newMessages.length > 0 && newMessages[0].id === '1') {
                newMessages[0] = {
                    ...newMessages[0],
                    text: t('chatbotWelcome')
                };
            }
            return newMessages;
        });
    }, [user, isGuest, language]);

    const fetchChatHistory = async () => {
        try {
            const response = await api.get('chatbot/history');
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

    const uploadMedia = async (uri: string, type: 'image' | 'video') => {
        setIsUploading(true);
        setUploadProgress(0);
        setServerFilePath(null);

        try {
            const formData = new FormData();

            if (Platform.OS !== 'web') {
                const uriParts = uri.split('.');
                const fileExtension = uriParts[uriParts.length - 1];
                const mimeType = type === 'video' ? `video/${fileExtension}` : `image/${fileExtension}`;

                formData.append('image', {
                    uri: uri,
                    name: `upload.${fileExtension}`,
                    type: mimeType,
                } as any);
            } else {
                const startBlob = await fetch(uri).then(r => r.blob());
                formData.append('image', startBlob, 'upload.jpg');
            }

            const response = await api.post('chatbot/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                onUploadProgress: (progressEvent) => {
                    if (progressEvent.total) {
                        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                        setUploadProgress(percent);
                    }
                },
            });

            if (response.data && response.data.file_path) {
                setServerFilePath(response.data.file_path);
            }
        } catch (error) {
            console.error('Upload failed', error);
            Alert.alert('Upload Failed', 'Please try attaching the media again.');
            setSelectedMedia(null); // Clear selection on failure
        } finally {
            setIsUploading(false);
        }
    };

    const pickMedia = async () => {
        try {
            const result = await ImagePicker.launchImageLibraryAsync({
                mediaTypes: ImagePicker.MediaTypeOptions.All,
                allowsEditing: true,
                aspect: [4, 3],
                quality: 0.8,
            });

            if (!result.canceled) {
                const asset = result.assets[0];
                const type = asset.type === 'video' ? 'video' : 'image';
                setSelectedMedia({
                    uri: asset.uri,
                    type: type
                });
                // Start upload immediately
                uploadMedia(asset.uri, type);
            }
        } catch (error) {
            Alert.alert('Error', 'Failed to pick media');
        }
    };

    const startRecording = async () => {
        try {
            const permission = await Audio.requestPermissionsAsync();
            if (permission.status !== 'granted') {
                Alert.alert('Permission needed', 'Please grant microphone access to use voice input.');
                return;
            }
            await Audio.setAudioModeAsync({
                allowsRecordingIOS: true,
                playsInSilentModeIOS: true,
            });
            const { recording } = await Audio.Recording.createAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
            setRecording(recording);
            setIsRecording(true);
        } catch (err) {
            console.error('Failed to start recording', err);
            Alert.alert('Error', 'Could not start recording hook up.');
        }
    };

    const stopRecordingAndSend = async () => {
        if (!recording) return;
        setRecording(null);
        setIsRecording(false);
        try {
            await recording.stopAndUnloadAsync();
            const uri = recording.getURI();
            if (uri) {
                await sendVoiceMessage(uri);
            }
        } catch (error) {
            console.error('Failed to stop recording', error);
        }
    };

    const sendVoiceMessage = async (uri: string) => {
        setLoading(true);

        try {
            const formData = new FormData();

            const uriParts = uri.split('.');
            let fileExtension = uriParts[uriParts.length - 1];
            if (fileExtension === 'm4a' || fileExtension === 'mp4') {
                fileExtension = 'mp4';
            }

            formData.append('audio', {
                uri,
                name: `voice.${fileExtension}`,
                type: `audio/${fileExtension}`
            } as any);
            formData.append('language', language || 'en');

            const response = await api.post('chatbot/voice', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            // Put the text in the input box so the user can send it or edit it
            if (response.data.transcription) {
                setInputText(response.data.transcription);
            }

        } catch (error: any) {
            console.error('Voice send error', error);
            const errorMessage = error.response?.data?.error || t('failedVoice');
            Alert.alert(t('error'), errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const handleSend = async () => {
        // Prevent sending while uploading
        if (isUploading) return;
        if ((!inputText.trim() && !selectedMedia) || loading) return;

        // 1. Show user's message immediately
        const userMessage: Message = {
            id: Date.now().toString(),
            text: inputText.trim(),
            sender: 'user',
            timestamp: new Date(),
            image: selectedMedia?.uri || undefined,
            mediaType: selectedMedia?.type
        };

        setMessages((prev) => [...prev, userMessage]);
        const currentText = inputText.trim();
        const currentServerPath = serverFilePath; // Capture current uploaded path

        setInputText('');
        setSelectedMedia(null);
        setServerFilePath(null);
        setLoading(true);

        try {
            // Enhanced JSON payload
            const payload: any = {
                message: currentText,
                language: language || 'en'
            };

            // Pass uploaded file path if exists
            if (currentServerPath) {
                payload.image_path = currentServerPath;
            }

            const response = await api.post('chatbot/message', payload);

            // 3. Show AI's response
            const botMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: response.data.response,
                sender: 'bot',
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, botMessage]);
        } catch (error: any) {
            console.error('Chat error detailed:', {
                message: error.message,
                response: error.response?.data,
                status: error.response?.status
            });
            const errorMessage = error.response?.data?.error || `${t('chatbotError')} (${error.message})`;

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
                {item.image && (
                    item.mediaType === 'video' ? (
                        <View style={styles.videoPlaceholder}>
                            <Video size={32} color="#fff" />
                            <Text style={styles.videoText}>Video Attached</Text>
                        </View>
                    ) : (
                        <Image source={{ uri: item.image }} style={styles.messageImage} />
                    )
                )}
                {item.text ? (
                    <Text style={[
                        styles.messageText,
                        item.sender === 'user' ? styles.userText : styles.botText
                    ]}>
                        {item.text.replace(/\\n/g, '\n')}
                    </Text>
                ) : null}
                <Text style={styles.timestampText}>
                    {item.timestamp.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}
                </Text>
            </View>
        </View>
    );

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
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




            <View style={styles.inputContainer}>
                <View style={styles.inputArea}>
                    <View style={styles.inputWrapper}>
                        <TextInput
                            style={styles.input}
                            placeholder={t('chatbotPlaceholder')}
                            value={inputText}
                            onChangeText={setInputText}
                            multiline
                            maxLength={500}
                        />
                        <TouchableOpacity
                            style={styles.micButton}
                            onPress={isRecording ? stopRecordingAndSend : startRecording}
                        >
                            {isRecording ? <Square fill="#f44336" color="#f44336" size={20} /> : <Mic color="#666" size={20} />}
                        </TouchableOpacity>
                    </View>
                    <TouchableOpacity
                        style={[
                            styles.sendButton,
                            ((!inputText.trim() && !selectedMedia) || loading || isUploading) && styles.sendButtonDisabled
                        ]}
                        onPress={handleSend}
                        disabled={(!inputText.trim() && !selectedMedia) || loading || isUploading}
                    >
                        {loading || isRecording ? (
                            <ActivityIndicator color="#fff" size="small" />
                        ) : isUploading ? (
                            <UploadCloud color="#fff" size={20} />
                        ) : (
                            <Send color="#fff" size={20} />
                        )}
                    </TouchableOpacity>
                </View>
            </View>
        </KeyboardAvoidingView >
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
        paddingBottom: Platform.OS === 'ios' ? 0 : 20,
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
    messageImage: {
        width: 200,
        height: 150,
        borderRadius: 8,
        marginBottom: 8,
    },
    videoPlaceholder: {
        width: 200,
        height: 100,
        backgroundColor: 'rgba(0,0,0,0.2)',
        borderRadius: 8,
        marginBottom: 8,
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'row',
    },
    videoText: {
        color: '#fff',
        marginLeft: 8,
        fontSize: 14,
        fontWeight: '500',
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
    inputContainer: {
        borderTopWidth: 1,
        borderTopColor: '#eee',
        backgroundColor: '#fff',
    },
    inputArea: {
        flexDirection: 'row',
        padding: 12,
        alignItems: 'center',
    },
    inputWrapper: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#f8f8f8',
        borderRadius: 24,
        marginRight: 8,
        paddingRight: 12,
    },
    input: {
        flex: 1,
        paddingHorizontal: 16,
        paddingVertical: 10,
        fontSize: 15,
        maxHeight: 100,
    },
    micButton: {
        padding: 4,
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
    recordingButton: {
        backgroundColor: '#f44336', // Red color while recording
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
