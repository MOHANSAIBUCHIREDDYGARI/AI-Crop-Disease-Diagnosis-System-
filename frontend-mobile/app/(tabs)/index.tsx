import React, { useState, useRef, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ActivityIndicator, Alert, ScrollView, Platform, Dimensions, Modal } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import { useRouter } from 'expo-router';
import { Camera as CameraIcon, Image as ImageIcon, X, ShieldAlert, Sun, CloudRain, Wind, ArrowRight, MapPin, Globe } from 'lucide-react-native';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';

import { useLanguage } from '../../context/LanguageContext';

const { width } = Dimensions.get('window');

const CROP_OPTIONS = [
  { id: 'tomato', name: 'Tomato', image: require('../../assets/images/tomato.png') },
  { id: 'cotton', name: 'Cotton', image: require('../../assets/images/cotton.png') },
  { id: 'wheat', name: 'Wheat', image: require('../../assets/images/wheat.png') },
  { id: 'rice', name: 'Rice', image: require('../../assets/images/rice.png') },
  { id: 'potato', name: 'Potato', image: require('../../assets/images/potato.png') },
  { id: 'grape', name: 'Grape', image: require('../../assets/images/grape.png') },
];

export default function DashboardScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [selectedCrop, setSelectedCrop] = useState('tomato');
  const [image, setImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [location, setLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [locationPermission, setLocationPermission] = useState(false);
  const [weather, setWeather] = useState<{
    temp: number;
    code: number;
    location: string | null;
  } | null>(null);
  const [showLanguageModal, setShowLanguageModal] = useState(false);

  const cameraRef = useRef<any>(null);
  const router = useRouter();
  const { user, isGuest, updateUser } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  console.log('DashboardScreen rendered. Language:', language);

  // Use languages from context/constants? Or keep local definition?
  // Better to use the one from Profile or Constants if available, but for now reuse strict list
  const LANGUAGES = [
    { code: 'en', name: 'English', nativeName: 'English' },
    { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' },
    { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
    { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
    { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ' },
    { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
    { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം' },
    { code: 'tcy', name: 'Tulu', nativeName: 'ತುಳು' },
  ];

  // Fetch weather data based on location
  // Fetch weather data from OpenMeteo (Free, No Key)
  const fetchWeather = async (lat: number, lon: number) => {
    try {
      // 1. Get Weather
      const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`;
      const weatherRes = await fetch(weatherUrl);
      const weatherData = await weatherRes.json();

      // 2. Get Location Name (Reverse Geocoding)
      // Using BigDataCloud extraction or similar free service, or just expo-location reverseGeocode
      const locationName = await reverseGeocode(lat, lon);

      if (weatherData.current_weather) {
        setWeather({
          temp: Math.round(weatherData.current_weather.temperature),
          code: weatherData.current_weather.weathercode,
          location: locationName || null,
        });
      }
    } catch (error) {
      console.log('Error fetching weather:', error);
      // Fallback
      setWeather({
        temp: 28,
        code: 0, // Clear Sky default
        location: null,
      });
    }
  };

  const reverseGeocode = async (lat: number, lon: number) => {
    try {
      const result = await Location.reverseGeocodeAsync({ latitude: lat, longitude: lon });
      if (result.length > 0) {
        return `${result[0].city || result[0].region}, ${result[0].isoCountryCode}`;
      }
    } catch (e) {
      console.log("Reverse geocode failed", e);
    }
    return null;
  };

  // Request location permission and get location
  useEffect(() => {
    (async () => {
      try {
        if (Platform.OS === 'web') {
          // Web platform: use browser geolocation API
          if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
              (position) => {
                const coords = {
                  latitude: position.coords.latitude,
                  longitude: position.coords.longitude,
                };
                setLocation(coords);
                setLocationPermission(true);
                fetchWeather(coords.latitude, coords.longitude);
              },
              (error) => {
                console.log('Geolocation error:', error);
                setWeather({
                  temp: 28,
                  code: 0,
                  location: null,
                });
              }
            );
          }
        } else {
          // Native platform: use expo-location
          const { status } = await Location.requestForegroundPermissionsAsync();
          if (status === 'granted') {
            setLocationPermission(true);
            try {
              const loc = await Location.getCurrentPositionAsync({});
              const coords = {
                latitude: loc.coords.latitude,
                longitude: loc.coords.longitude,
              };
              setLocation(coords);
              await fetchWeather(coords.latitude, coords.longitude);
            } catch (error) {
              console.log('Error getting location:', error);
            }
          } else {
            setWeather({
              temp: 28,
              code: 0, // Clear Sky
              location: null,
            });
          }
        }
      } catch (error) {
        console.log('Location setup error:', error);
      }
    })();
  }, []);



  // --- CAMERA LOGIC ---
  if (!permission) return <View />;
  if (!permission.granted && isScanning) {
    return (
      <View style={styles.permissionContainer}>
        <Text style={styles.permissionText}>We need camera access to scan your crops.</Text>
        <TouchableOpacity style={styles.permissionButton} onPress={requestPermission}>
          <Text style={styles.permissionButtonText}>Allow Camera</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => setIsScanning(false)} style={{ marginTop: 20 }}>
          <Text style={{ color: '#666' }}>Cancel</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const takePicture = async () => {
    if (cameraRef.current) {
      const photo = await cameraRef.current.takePictureAsync({ quality: 1.0 });
      setImage(photo.uri);
      setIsCameraActive(false);
    }
  };

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: false,  // Disabled to ensure complete image is uploaded
      quality: 1.0,  // 100% quality - no compression
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      setIsCameraActive(false);
    }
  };

  const validateImageQuality = (uri: string): boolean => {
    // Basic client-side validation
    // In a real app, you might check file size, dimensions, etc.
    return true; // For now, accept all images
  };

  const handleDiagnose = async () => {
    if (!image) return;
    // Backend will handle quality and confidence validation
    await performDiagnosis();
  };

  const performDiagnosis = async () => {
    if (!image) return;

    setLoading(true);

    try {
      let response;

      if (Platform.OS === 'web') {
        // Web platform: use fetch with blob
        const blob = await fetch(image).then(r => r.blob());
        const formData = new FormData();
        formData.append('image', blob, 'photo.jpg');
        formData.append('crop', selectedCrop);
        formData.append('language', language);

        // Add location if available
        if (location) {
          formData.append('latitude', location.latitude.toString());
          formData.append('longitude', location.longitude.toString());
        }

        const apiUrl = 'http://localhost:5000/api/diagnosis/detect';
        const fetchResponse = await fetch(apiUrl, {
          method: 'POST',
          body: formData,
        });

        if (!fetchResponse.ok) {
          const errorData = await fetchResponse.json();
          throw new Error(errorData.error || 'Failed to detect disease');
        }

        response = { data: await fetchResponse.json() };
      } else {
        // Native platform: use axios with React Native FormData
        const formData = new FormData();
        const uriParts = image.split('.');
        const fileType = uriParts[uriParts.length - 1];

        formData.append('image', {
          uri: image,
          name: `photo.${fileType}`,
          type: `image/${fileType}`,
        } as any);
        formData.append('crop', selectedCrop);
        formData.append('language', language);

        // Add location if available
        if (location) {
          formData.append('latitude', location.latitude.toString());
          formData.append('longitude', location.longitude.toString());
        }

        response = await api.post('/diagnosis/detect', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      }

      router.push({
        pathname: '/results',
        params: { data: JSON.stringify(response.data) }
      });

      // Show quality warning if present (after navigation)
      if (response.data.quality_warning) {
        setTimeout(() => {
          Alert.alert(
            'Image Quality Notice',
            response.data.quality_warning + '\n\nFor better results, consider retaking the photo with better lighting and focus.',
            [{ text: 'OK' }]
          );
        }, 500);
      }

      // Reset after successful nav
      setTimeout(() => {
        setIsScanning(false);
        setImage(null);
      }, 500);

    } catch (error: any) {
      console.log('=== Diagnosis Error Debug ===');
      console.log('Error object:', error);
      console.log('Error response:', error.response);
      console.log('Error response data:', error.response?.data);
      console.log('Error response status:', error.response?.status);
      console.log('Error type:', error.response?.data?.error);
      console.log('============================');

      // Check if it's a low confidence error
      if (error.response?.status === 400 && error.response?.data?.error === 'Low confidence prediction') {
        console.log('✅ Detected low confidence error - showing alert');
        Alert.alert(
          'Image Quality Issue',
          error.response.data.message || 'The image quality is not clear enough for accurate diagnosis. Please retake the photo with better lighting and focus.',
          [
            { text: 'Retake Photo', onPress: () => setImage(null), style: 'default' },
            { text: 'Cancel', style: 'cancel' }
          ]
        );
      } else {
        console.log('❌ Not a low confidence error - showing generic error');
        const message = error.response?.data?.error || 'Failed to detect disease.';
        Alert.alert('Error', message);
      }
    } finally {
      setLoading(false);
    }
  };

  // --- SCANNING (DIAGNOSIS) VIEW ---
  if (isScanning) {
    if (isCameraActive) {
      return (
        <View style={styles.cameraContainer}>
          <CameraView style={styles.camera} ref={cameraRef}>
            <View style={styles.cameraOverlay}>
              <TouchableOpacity style={styles.closeCameraButton} onPress={() => setIsCameraActive(false)}>
                <X color="#fff" size={32} />
              </TouchableOpacity>
              <View style={styles.scanFrame} />
              <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
                <View style={styles.captureButtonInner} />
              </TouchableOpacity>
            </View>
          </CameraView>
        </View>
      );
    }

    return (
      <ScrollView style={styles.container}>
        <View style={styles.scanHeader}>
          <TouchableOpacity onPress={() => setIsScanning(false)}>
            <X size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.scanTitle}>{t('scanCrop')} {t(`crop_${selectedCrop}` as any)}</Text>
          <View style={{ width: 24 }} />
        </View>

        <View style={styles.cropSelectorContainer}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ paddingHorizontal: 20 }}>
            {CROP_OPTIONS.map((crop) => (
              <TouchableOpacity
                key={crop.id}
                style={[styles.cropChip, selectedCrop === crop.id && styles.cropChipActive]}
                onPress={() => setSelectedCrop(crop.id)}
              >
                <Text style={[styles.cropChipText, selectedCrop === crop.id && styles.cropChipTextActive]}>{t(`crop_${crop.id}` as any)}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        <View style={styles.uploadArea}>
          {image ? (
            <View style={styles.previewArea}>
              <Image source={{ uri: image }} style={styles.previewImg} />
              <TouchableOpacity style={styles.retakeBtn} onPress={() => setImage(null)}>
                <X color="#fff" size={20} />
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.actionButtons}>
              <TouchableOpacity style={styles.bigActionBtn} onPress={() => setIsCameraActive(true)}>
                <View style={[styles.iconCircle, { backgroundColor: '#e8f5e9' }]}>
                  <CameraIcon size={32} color="#4caf50" />
                </View>
                <Text style={styles.actionLabel}>{t('scanCrop')}</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.bigActionBtn} onPress={pickImage}>
                <View style={[styles.iconCircle, { backgroundColor: '#e3f2fd' }]}>
                  <ImageIcon size={32} color="#2196f3" />
                </View>
                <Text style={styles.actionLabel}>{t('uploadImage')}</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>

        <View style={styles.tipsCard}>
          <Text style={styles.tipsTitle}>{t('tipsTitle')}</Text>
          <Text style={styles.tipText}>{t('tip1')}</Text>
          <Text style={styles.tipText}>{t('tip2')}</Text>
          <Text style={styles.tipText}>{t('tip3')}</Text>
          <Text style={styles.tipText}>{t('tip4')}</Text>
        </View>

        <TouchableOpacity
          style={[styles.mainButton, (!image || loading) && styles.disabledButton]}
          onPress={handleDiagnose}
          disabled={!image || loading}
        >
          {loading ? <ActivityIndicator color="#fff" /> : (
            <>
              <ShieldAlert color="#fff" size={24} style={{ marginRight: 10 }} />
              <Text style={styles.mainButtonText}>{t('analyzeDisease')}</Text>
            </>
          )}
        </TouchableOpacity>
      </ScrollView>
    );
  }

  // --- DASHBOARD (HOME) VIEW ---
  return (
    <ScrollView key={language} style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>
      {/* Header Section */}
      <View style={styles.dashboardHeader}>
        <View style={styles.headerLeft}>
          <View>
            <Text style={styles.greeting}>{t('namaste')}</Text>
            <Text style={styles.farmerName}>{user ? user.name : t('farmer')}</Text>
          </View>
          <TouchableOpacity onPress={() => router.push('/profile')} style={styles.profileAvatarContainer}>
            <Image source={require('../../assets/images/farmer-avatar.png')} style={styles.profileAvatar} />
          </TouchableOpacity>
        </View>
        <View style={styles.headerRight}>
          <TouchableOpacity onPress={() => setShowLanguageModal(true)} style={styles.languageButton}>
            <Globe size={20} color="#2E7D32" />
          </TouchableOpacity>
          <Image source={require('../../assets/images/logo.png')} style={styles.headerIcon} />
        </View>
      </View>

      {/* Weather Widget */}
      <View style={styles.weatherCard}>
        <View style={styles.weatherInfo}>
          <Text style={styles.weatherTemp}>
            {location ? (weather ? `${weather.temp}°C` : 'Loading...') : t('notAvailable')}
          </Text>
          <Text style={styles.weatherDesc}>
            {location ? (weather ? t(`weather_${weather.code}` as any) : t('weather')) : t('weatherUnavailable')}
          </Text>
          <Text style={styles.weatherLocation}>
            {location ? (weather ? (weather.location || t('yourLocation')) : t('weather')) : t('enableGps')}
          </Text>
          <TouchableOpacity
            style={[styles.locationBadge, !location && styles.locationBadgeDisabled]}
            onPress={async () => {
              if (!location) {
                if (Platform.OS === 'web') {
                  // Web platform: use browser geolocation
                  if ('geolocation' in navigator) {
                    navigator.geolocation.getCurrentPosition(
                      (position) => {
                        const coords = {
                          latitude: position.coords.latitude,
                          longitude: position.coords.longitude,
                        };
                        setLocation(coords);
                        setLocationPermission(true);
                        fetchWeather(coords.latitude, coords.longitude);
                        Alert.alert('GPS Enabled', 'Location access granted! Weather data will now be displayed.');
                      },
                      (error) => {
                        Alert.alert('Permission Denied', 'Location permission is required for weather-based advice. Please enable it in your browser settings.');
                      }
                    );
                  } else {
                    Alert.alert('Not Supported', 'Geolocation is not supported by your browser.');
                  }
                } else {
                  // Native platform: request location permission
                  const { status } = await Location.requestForegroundPermissionsAsync();
                  if (status === 'granted') {
                    setLocationPermission(true);
                    try {
                      const loc = await Location.getCurrentPositionAsync({});
                      const coords = {
                        latitude: loc.coords.latitude,
                        longitude: loc.coords.longitude,
                      };
                      setLocation(coords);
                      await fetchWeather(coords.latitude, coords.longitude);
                      Alert.alert('GPS Enabled', 'Location access granted! Weather data will now be displayed.');
                    } catch (error) {
                      Alert.alert('Error', 'Could not get your location. Please try again.');
                    }
                  } else {
                    Alert.alert('Permission Denied', 'Location permission is required for weather-based advice. Please enable it in your device settings.');
                  }
                }
              }
            }}
            disabled={!!location}
          >
            <MapPin size={12} color={location ? "#4caf50" : "#f44336"} />
            <Text style={styles.locationText}>
              {location ? t('gpsEnabled') : t('enableGps')}
            </Text>
          </TouchableOpacity>
        </View>
        <Sun size={48} color="#FFD700" />
      </View>

      {/* Main Action */}
      <View style={styles.ctaSection}>
        <Text style={styles.sectionTitle}>{t('whatWouldYouLikeToDo')}</Text>
        <TouchableOpacity style={styles.heroButton} onPress={() => setIsScanning(true)}>
          <View style={styles.heroContent}>
            <View style={styles.heroIconBg}>
              <CameraIcon size={32} color="#fff" />
            </View>
            <View>
              <Text style={styles.heroTitle}>{t('scanCrop')}</Text>
              <Text style={styles.heroSubtitle}>{t('instantDiagnosis')}</Text>
            </View>
          </View>
          <ArrowRight size={24} color="#2E7D32" />
        </TouchableOpacity>
      </View>

      {/* Quick Tips / Crops */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{t('supportedCrops')}</Text>
        <View style={styles.grid}>
          {CROP_OPTIONS.map((crop) => (
            <View key={crop.id} style={styles.gridItem}>
              <View style={styles.gridIconImage}>
                <Image source={crop.image} style={styles.cropImage} />
              </View>
              <Text style={styles.gridLabel}>{t(`crop_${crop.id}` as any)}</Text>
            </View>
          ))}
        </View>
      </View>

      {/* Guest Upsell */}
      {isGuest && (
        <View style={styles.upsellCard}>
          <ShieldAlert size={24} color="#4caf50" style={{ marginBottom: 8 }} />
          <Text style={styles.upsellTitle}>{t('saveYourHistory')}</Text>
          <Text style={styles.upsellDesc}>{t('trackHealth')}</Text>
          <TouchableOpacity style={styles.upsellBtn} onPress={() => router.push('/profile')}>
            <Text style={styles.upsellBtnText}>{t('registerNow')}</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Language Selection Modal */}
      <Modal
        visible={showLanguageModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowLanguageModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{t('selectLanguage')}</Text>
              <TouchableOpacity onPress={() => setShowLanguageModal(false)}>
                <X size={24} color="#666" />
              </TouchableOpacity>
            </View>
            <ScrollView style={styles.languageList}>
              {LANGUAGES.map((lang) => (
                <TouchableOpacity
                  key={lang.code}
                  style={[
                    styles.languageItem,
                    language === lang.code && styles.languageItemSelected
                  ]}
                  onPress={async () => {
                    try {
                      // Optimistic Update
                      setLanguage(lang.code as any);
                      setShowLanguageModal(false);
                      Alert.alert(t('languageChanged'), `${lang.name}`);

                      if (!isGuest && user) {
                        await api.put('/user/language', { language: lang.code });
                        // Update user context with new language
                        await updateUser({ preferred_language: lang.code });
                      }
                    } catch (error) {
                      console.log("Error updating language", error);
                      // Alert.alert(t('error'), t('failedUpdate')); // Optional: suppress if optimistic update worked
                    }
                  }}
                >
                  <View>
                    <Text style={styles.languageName}>{lang.name}</Text>
                    <Text style={styles.languageNative}>{lang.nativeName}</Text>
                  </View>
                  {language === lang.code && (
                    <View style={styles.checkmark}>
                      <Text style={styles.checkmarkText}>✓</Text>
                    </View>
                  )}
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  permissionText: {
    marginBottom: 20,
    fontSize: 16
  },
  permissionButton: {
    backgroundColor: '#4caf50',
    padding: 12,
    borderRadius: 8
  },
  permissionButtonText: {
    color: 'white',
    fontWeight: 'bold'
  },
  // Dashboard Styles
  dashboardHeader: {
    paddingTop: 60,
    paddingHorizontal: 24,
    paddingBottom: 24,
    backgroundColor: '#fff',
    borderBottomLeftRadius: 32,
    borderBottomRightRadius: 32,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 10,
  },
  greeting: {
    fontSize: 18,
    color: '#666',
  },
  farmerName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2E7D32',
  },
  headerIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  profileAvatarContainer: {
    marginLeft: 8,
  },
  profileAvatar: {
    width: 45,
    height: 45,
    borderRadius: 22.5,
    borderWidth: 2,
    borderColor: '#2E7D32',
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  languageButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  weatherCard: {
    margin: 24,
    backgroundColor: '#2E7D32',
    borderRadius: 24,
    padding: 24,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#2E7D32',
    shadowOpacity: 0.4,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 }
  },
  weatherInfo: {
    flex: 1,
  },
  weatherTemp: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#fff',
  },
  weatherDesc: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.9)',
    marginTop: 4,
  },
  weatherLocation: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.7)',
    marginTop: 8,
  },
  locationBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginTop: 8,
  },
  locationBadgeDisabled: {
    backgroundColor: 'rgba(244, 67, 54, 0.3)',
  },
  locationText: {
    fontSize: 10,
    color: '#fff',
    marginLeft: 4,
    fontWeight: '600',
  },
  ctaSection: {
    paddingHorizontal: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  heroButton: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    elevation: 2,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  heroContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  heroIconBg: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#4caf50',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  heroTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  heroSubtitle: {
    fontSize: 13,
    color: '#666',
    marginTop: 2,
  },
  section: {
    padding: 24,
  },
  grid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
  },
  gridItem: {
    width: (width - 60) / 4,
    alignItems: 'center',
  },
  gridIcon: {
    width: 60,
    height: 60,
    borderRadius: 20,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
    elevation: 1,
  },
  gridIconImage: {
    width: 60,
    height: 60,
    borderRadius: 20,
    backgroundColor: '#fff',
    marginBottom: 8,
    elevation: 1,
    overflow: 'hidden',
  },
  cropImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  gridLabel: {
    fontSize: 12,
    color: '#666',
    fontWeight: '600',
  },
  upsellCard: {
    margin: 24,
    marginTop: 0,
    padding: 20,
    backgroundColor: '#e8f5e9',
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#c8e6c9',
  },
  upsellTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2e7d32',
  },
  upsellDesc: {
    textAlign: 'center',
    color: '#558b2f',
    marginVertical: 8,
    fontSize: 13,
  },
  upsellBtn: {
    backgroundColor: '#fff',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  upsellBtnText: {
    color: '#2e7d32',
    fontWeight: 'bold',
    fontSize: 12,
  },
  // Scan View Styles
  scanHeader: {
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#fff',
  },
  scanTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  cropSelectorContainer: {
    paddingVertical: 20,
  },
  cropChip: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    backgroundColor: '#fff',
    marginRight: 12,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  cropChipActive: {
    backgroundColor: '#4caf50',
    borderColor: '#4caf50',
  },
  cropChipText: {
    color: '#666',
    fontWeight: '600',
  },
  cropChipTextActive: {
    color: '#fff',
  },
  uploadArea: {
    margin: 24,
    height: 320,
    backgroundColor: '#fff',
    borderRadius: 24,
    elevation: 2,
    justifyContent: 'center',
    overflow: 'hidden',
  },
  previewArea: {
    width: '100%',
    height: '100%',
  },
  previewImg: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  retakeBtn: {
    position: 'absolute',
    top: 16,
    right: 16,
    backgroundColor: 'rgba(0,0,0,0.6)',
    padding: 8,
    borderRadius: 20,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 32,
  },
  bigActionBtn: {
    alignItems: 'center',
  },
  iconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  actionLabel: {
    fontWeight: '600',
    color: '#555',
  },
  tipsCard: {
    marginHorizontal: 24,
    marginBottom: 16,
    backgroundColor: '#e3f2fd',
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#2196f3',
  },
  tipsTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1976d2',
    marginBottom: 8,
  },
  tipText: {
    fontSize: 13,
    color: '#555',
    marginBottom: 4,
    lineHeight: 20,
  },
  mainButton: {
    marginHorizontal: 24,
    backgroundColor: '#4caf50',
    padding: 20,
    borderRadius: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 4,
    shadowColor: '#4caf50',
    shadowOpacity: 0.3,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
  },
  disabledButton: {
    backgroundColor: '#a5d6a7',
    elevation: 0,
  },
  mainButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  cameraContainer: {
    flex: 1,
    backgroundColor: '#000',
  },
  camera: {
    flex: 1,
  },
  cameraOverlay: {
    flex: 1,
    justifyContent: 'space-between',
    padding: 32,
    paddingBottom: 60,
  },
  scanFrame: {
    flex: 1,
    marginVertical: 60,
    borderWidth: 2,
    borderColor: 'white',
    borderStyle: 'dashed',
    borderRadius: 20
  },
  closeCameraButton: {
    alignSelf: 'flex-end',
    padding: 8,
  },
  captureButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    borderColor: '#fff',
    alignSelf: 'center',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButtonInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#fff',
  },
  // Language Modal Styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingBottom: 40,
    maxHeight: '70%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  languageList: {
    padding: 10,
  },
  languageItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    marginVertical: 4,
    backgroundColor: '#f8f9fa',
  },
  languageItemSelected: {
    backgroundColor: '#e8f5e9',
    borderWidth: 2,
    borderColor: '#2E7D32',
  },
  languageName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  languageNative: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  checkmark: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#2E7D32',
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkmarkText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
