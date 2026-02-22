import React, { useState, useRef, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ActivityIndicator, Alert, ScrollView, Platform, Dimensions, Modal } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import { useRouter } from 'expo-router';
import { Camera as CameraIcon, Image as ImageIcon, X, ShieldAlert, Sun, CloudRain, Wind, ArrowRight, MapPin, Globe } from 'lucide-react-native';

// --- Internal Imports ---
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import { useLanguage } from '../../context/LanguageContext';
import { T } from '../../components/ui/T';
import { addToLocalHistory } from '../../services/localHistory';

const { width } = Dimensions.get('window');

// --- Configuration ---
// These are the crops our AI knows how to diagnose.
// Ideally, this list mimics what the backend supports.
const CROP_OPTIONS = [
  { id: 'tomato', name: 'Tomato', image: require('../../assets/images/tomato.png') },
  { id: 'rice', name: 'Rice', image: require('../../assets/images/rice.png') },
  { id: 'potato', name: 'Potato', image: require('../../assets/images/potato.png') },
  { id: 'grape', name: 'Grape', image: require('../../assets/images/grape.png') },
  { id: 'maize', name: 'Maize', image: require('../../assets/images/maize.png') },
];

export default function DashboardScreen() {
  // --- Navigation & Permissions ---
  const router = useRouter(); // Helps us move between screens
  const [permission, requestPermission] = useCameraPermissions(); // Ask the phone nicely for camera access

  // --- App State (What's happening right now) ---
  const [selectedCrop, setSelectedCrop] = useState('tomato'); // crop selected by farmer
  const [image, setImage] = useState<string | null>(null); // The photo to analyze
  const [loading, setLoading] = useState(false); // Are we waiting for the AI?
  const [isScanning, setIsScanning] = useState(false); // Is the user in "Scan Mode"?
  const [isCameraActive, setIsCameraActive] = useState(false); // Is the actual camera open?

  // --- Location & Weather State ---
  const [location, setLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [locationPermission, setLocationPermission] = useState(false);
  const [weather, setWeather] = useState<{
    temp: number;
    code: number;
    location: string | null;
    description?: string;
  } | null>(null);

  // --- Helper Hooks ---
  const cameraRef = useRef<any>(null); // A reference to the camera component so we can tell it to "click"
  const { user, isGuest, updateUser } = useAuth(); // Who is using the app?
  const { language, setLanguage, t } = useLanguage(); // Current language
  const [showLanguageModal, setShowLanguageModal] = useState(false); // Is the language picker open?

  console.log('DashboardScreen rendered. Language:', language);

  // --- Language Options ---
  // List of languages we support for the UI
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

  // --- Weather Logic ---
  // We explicitly fetch weather because crop diseases depend heavily on it.
  const fetchWeather = async (lat: number, lon: number) => {
    try {
      // We use Open-Meteo as a free weather API
      const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`;
      const weatherRes = await fetch(weatherUrl);
      const weatherData = await weatherRes.json();

      // We also want to know the *name* of the place (e.g., "Hyderabad")
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
      // Fallback if weather fails (don't crash the app)
      setWeather({
        temp: 28,
        code: 0,
        description: t('clearSky'),
        location: t('weatherUnavailable'),
      });
    }
  };

  // Convert GPS coordinates (lat, lon) into a city name
  const reverseGeocode = async (lat: number, lon: number) => {
    try {
      const result = await Location.reverseGeocodeAsync({ latitude: lat, longitude: lon });
      if (result.length > 0) {
        return `${result[0].city || result[0].region}, ${result[0].isoCountryCode}`;
      }
    } catch (e) {
      console.log("Reverse geocode failed", e);
    }
    return t('yourLocation');
  };

  // Turn numeric weather codes into human-readable text (and translate them!)
  const getWeatherDescription = (code: number) => {
    // WMO Weather interpretation codes (https://open-meteo.com/en/docs)
    const codeToKey: { [key: number]: string } = {
      0: 'clearSky',
      1: 'mainlyClear', 2: 'partlyCloudy', 3: 'overcast',
      45: 'fog', 48: 'fog',
      51: 'drizzle', 53: 'drizzle', 55: 'drizzle',
      61: 'rain', 63: 'rain', 65: 'rain',
      71: 'snow', 73: 'snow', 75: 'snow',
      95: 'thunderstorm'
    };
    const key = codeToKey[code] || 'clearSky';
    return t(key as any);
  };


  // --- Helper: Initial Setup ---
  // When the app starts, we try to get the user's location automatically

  useEffect(() => {
    (async () => {
      try {
        if (Platform.OS === 'web') {
          // Web Browser Geolocation
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
                  description: t('clearSky'),
                  location: t('enableGps'),
                });
              }
            );
          }
        } else {
          // Native Device Geolocation (Android/iOS)
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
            // Permission denied logic
            setWeather({
              temp: 28,
              code: 0,
              description: t('clearSky'),
              location: t('enableGps'),
            });
          }
        }
      } catch (error) {
        console.log('Location setup error:', error);
      }
    })();
  }, []);

  // --- Helper: Language Update ---
  // If the language changes, re-fetch weather to get the translated description
  useEffect(() => {
    if (location) {
      fetchWeather(location.latitude, location.longitude);
    }
  }, [language, location]);



  // --- Camera & Image Handling ---

  // 1. Permission Check
  if (!permission) return <View />; // Still loading permission status
  if (!permission.granted && isScanning) {
    // If the user hasn't allowed the camera, we show a friendly request screen
    return (
      <View style={styles.permissionContainer}>
        <T style={styles.permissionText}>cameraPermissionReq</T>
        <TouchableOpacity style={styles.permissionButton} onPress={requestPermission}>
          <T style={styles.permissionButtonText}>allowCamera</T>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => setIsScanning(false)} style={{ marginTop: 20 }}>
          <T style={{ color: '#666' }}>cancel</T>
        </TouchableOpacity>
      </View>
    );
  }

  // 2. Take Picture Button Action
  const takePicture = async () => {
    if (cameraRef.current) {
      const photo = await cameraRef.current.takePictureAsync({ quality: 1.0 });
      setImage(photo.uri);
      setIsCameraActive(false); // Close camera view, show preview
    }
  };

  // 3. Upload from Gallery Action
  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: false, // We check quality ourselves later
      quality: 1.0,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      setIsCameraActive(false);
    }
  };

  // 4. Validate Image (Placeholder for now)
  const validateImageQuality = (uri: string): boolean => {
    // In a real app, we might check brightness/blur here before sending.
    // Right now, the backend does the heavy lifting.
    return true;
  };

  // 5. The Main Action: Diagnose!
  const handleDiagnose = async () => {
    if (!image) return;
    await performDiagnosis();
  };

  // 6. Diagnosis Logic (Sending to Backend)
  const performDiagnosis = async () => {
    if (!image) return;

    setLoading(true); // Show spinner

    try {
      let response;

      if (Platform.OS === 'web') {
        // --- Web Logic ---
        // On web, we have to convert the image URI to a Blob to send it.
        const blob = await fetch(image).then(r => r.blob());
        const formData = new FormData();
        formData.append('image', blob, 'photo.jpg');
        formData.append('crop', selectedCrop);
        formData.append('language', language);

        // Add context for better AI accuracy
        if (location) {
          formData.append('latitude', location.latitude.toString());
          formData.append('longitude', location.longitude.toString());
        }

        // Add language so the backend replies in the right language
        formData.append('language', language);

        const apiUrl = 'http://localhost:5000/api/diagnosis/detect';
        // Get token to send along with the request so the backend knows who we are
        const { getItem } = await import('../../services/storage');
        const token = await getItem('userToken');

        const fetchResponse = await fetch(apiUrl, {
          method: 'POST',
          body: formData,
          headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        });

        if (!fetchResponse.ok) {
          const errorData = await fetchResponse.json();
          // Create a custom error to handle it in the catch block
          const customError: any = new Error(errorData.error || 'Failed to detect disease');
          customError.response = {
            status: fetchResponse.status,
            data: errorData
          };
          throw customError;
        }

        response = { data: await fetchResponse.json() };
      } else {
        // --- Mobile Logic ---
        // On phones, it's easier. We just construct the FormData with the URI.
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

        // Add context
        if (location) {
          formData.append('latitude', location.latitude.toString());
          formData.append('longitude', location.longitude.toString());
        }

        response = await api.post('diagnosis/detect', formData, {
          headers: {
            // Let Axios set the Content-Type with boundary automatically
            // But we explicitly need 'Content-Type': 'multipart/form-data' for some RN versions? 
            // Actually, best practice is usually to let it be. 
            // IF this breaks, we will revert.
            'Content-Type': 'multipart/form-data',
          },
          transformRequest: (data, headers) => {
            // Hack to ensure Authorization header isn't lost if Axios creates a new header object
            return data;
          }
        });
      }

      // --- Success! ---
      // If we are a guest, save this locally so they don't lose it.
      if (isGuest) {
        await addToLocalHistory(response.data, selectedCrop);
      }

      // Go to results screen
      router.push({
        pathname: '/results',
        params: { data: JSON.stringify(response.data) }
      });

      // Show warning if the image was "meh" but we still got a result
      if (response.data.quality_warning) {
        setTimeout(() => {
          Alert.alert(
            'Image Quality Notice',
            response.data.quality_warning + '\n\n' + t('imageQualityWarningBody'),
            [{ text: 'OK' }]
          );
        }, 500);
      }

      // Reset state so they can scan again later
      setTimeout(() => {
        setIsScanning(false);
        setImage(null);
      }, 500);

    } catch (error: any) {
      console.log('=== Diagnosis Error Debug ===');
      console.log('Error object:', error);
      // ... debug logs ...

      // --- Error Handling ---
      const errData = error.response?.data;
      if (error.response?.status === 400 && (errData?.error === 'Low confidence prediction' || errData?.error === 'Image Rejected')) {
        // This is a "good" error - it means our quality control worked.
        console.log('✅ Detected quality error - showing alert');
        Alert.alert(
          t('imageQualityIssue'),
          errData.message || t('imageQualityWarningBody'),
          [
            { text: t('retakePhoto'), onPress: () => setImage(null), style: 'default' },
            { text: t('cancel'), style: 'cancel' }
          ]
        );
      } else {
        // This is a "bad" error - something actually broke.
        console.log('❌ Not a quality error - showing generic error');
        const message = errData?.message || errData?.error || 'Failed to detect disease.';
        Alert.alert(t('error'), message);
      }
    } finally {
      setLoading(false); // Stop loading spinner
    }
  };


  // --- Render Logic ---

  // 1. Scanning Mode UI (Camera or Preview)
  if (isScanning) {
    if (isCameraActive) {
      // THE CAMERA VIEW
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

    // THE PREVIEW / UPLOAD MODE
    return (
      <ScrollView style={styles.container}>
        <View style={styles.scanHeader}>
          <TouchableOpacity onPress={() => setIsScanning(false)}>
            <X size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.scanTitle}><T>scanCrop</T> <T>{`crop_${selectedCrop}` as any}</T></Text>
          <View style={{ width: 24 }} />
        </View>

        {/* Crop Selection Chips */}
        <View style={styles.cropSelectorContainer}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ paddingHorizontal: 20 }}>
            {CROP_OPTIONS.map((crop) => (
              <TouchableOpacity
                key={crop.id}
                style={[styles.cropChip, selectedCrop === crop.id && styles.cropChipActive]}
                onPress={() => setSelectedCrop(crop.id)}
              >
                <T style={[styles.cropChipText, selectedCrop === crop.id && styles.cropChipTextActive]}>{`crop_${crop.id}` as any}</T>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Image Preview or Action Buttons */}
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
                <T style={styles.actionLabel}>scanCrop</T>
              </TouchableOpacity>
              <TouchableOpacity style={styles.bigActionBtn} onPress={pickImage}>
                <View style={[styles.iconCircle, { backgroundColor: '#e3f2fd' }]}>
                  <ImageIcon size={32} color="#2196f3" />
                </View>
                <T style={styles.actionLabel}>uploadImage</T>
              </TouchableOpacity>
            </View>
          )}
        </View>

        {/* Helpful Tips for the Farmer */}
        <View style={styles.tipsCard}>
          <T style={styles.tipsTitle}>tipsTitle</T>
          <T style={styles.tipText}>tip1</T>
          <T style={styles.tipText}>tip2</T>
          <T style={styles.tipText}>tip3</T>
          <T style={styles.tipText}>tip4</T>
        </View>

        {/* The Big "Diagnose" Button */}
        <TouchableOpacity
          style={[styles.mainButton, (!image || loading) && styles.disabledButton]}
          onPress={handleDiagnose}
          disabled={!image || loading}
        >
          {loading ? <ActivityIndicator color="#fff" /> : (
            <>
              <ShieldAlert color="#fff" size={24} style={{ marginRight: 10 }} />
              <T style={styles.mainButtonText}>analyzeDisease</T>
            </>
          )}
        </TouchableOpacity>
      </ScrollView>
    );
  }


  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>
      {/* Header with Name & Language Picker */}
      <View style={styles.dashboardHeader}>
        <View style={styles.headerLeft}>
          <View>
            <T style={styles.greeting}>namaste</T>
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
          <View style={styles.headerIconContainer}>
            <Image source={require('../../assets/images/logo.jpeg')} style={styles.headerIconImage} resizeMode="cover" />
          </View>
        </View>
      </View>

      {/* Weather Card - Critical for agriculture */}
      <View style={styles.weatherCard}>
        <View style={styles.weatherInfo}>
          <Text style={styles.weatherTemp}>
            {location ? (weather ? `${weather.temp}°C` : t('weatherLoading')) : t('weatherNA')}
          </Text>
          <Text style={styles.weatherDesc}>
            {location ? (weather ? (weather.description || t(`weather_${weather.code}` as any)) : t('weatherFetching')) : t('weatherUnavailable')}
          </Text>
          <Text style={styles.weatherLocation}>
            {location ? (weather ? (weather.location || t('yourLocation')) : t('weather')) : t('enableGps')}
          </Text>
          <TouchableOpacity
            style={[styles.locationBadge, !location && styles.locationBadgeDisabled]}
            onPress={async () => {
              // Logic to ask for GPS permission manually if they clicked the button
              if (!location) {
                if (Platform.OS === 'web') {
                  // Web GPS Request
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
                  // Mobile GPS Request
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
                      Alert.alert(t('gpsEnabled'), 'Location access granted! Weather data will now be displayed.');
                    } catch (error) {
                      Alert.alert(t('error'), t('locationError'));
                    }
                  } else {
                    Alert.alert(t('permissionDenied'), t('locationPermissionRequired'));
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

      {/* Main "Call to Action" Button - Start Scanning */}
      <View style={styles.ctaSection}>
        <Text style={styles.sectionTitle}>{t('whatWouldYouLikeToDo')}</Text>
        <TouchableOpacity style={styles.heroButton} onPress={() => setIsScanning(true)}>
          <View style={styles.heroContent}>
            <View style={styles.heroIconBg}>
              <CameraIcon size={32} color="#fff" />
            </View>
            <View>
              <T style={styles.heroTitle}>scanCrop</T>
              <T style={styles.heroSubtitle}>instantDiagnosis</T>
            </View>
          </View>
          <ArrowRight size={24} color="#2E7D32" />
        </TouchableOpacity>
      </View>

      {/* Grid of supported crops (Visual Reference) */}
      <View style={styles.section}>
        <T style={styles.sectionTitle}>supportedCrops</T>
        <View style={styles.grid}>
          {CROP_OPTIONS.map((crop) => (
            <View key={crop.id} style={styles.gridItem}>
              <View style={styles.gridIconImage}>
                <Image source={crop.image} style={styles.cropImage} />
              </View>
              <T style={styles.gridLabel}>{`crop_${crop.id}` as any}</T>
            </View>
          ))}
        </View>
      </View>

      {/* Upsell for Guest Users to Register */}
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
              <T style={styles.modalTitle}>selectLanguage</T>
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
                      // 1. Update app context
                      setLanguage(lang.code as any);
                      setShowLanguageModal(false);
                      Alert.alert(t('languageChanged'), `${lang.name}`);

                      // 2. If user is logged in, save to backend
                      if (!isGuest && user) {
                        await api.put('user/language', { language: lang.code });
                        // 3. Update local user state
                        await updateUser({ preferred_language: lang.code });
                      }
                    } catch (error) {
                      console.log("Error updating language", error);
                      // Fail silently or show toast
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
  headerIconContainer: {
    width: 60,
    height: 60,
    borderRadius: 30, // Round shape
    backgroundColor: '#2E7D32', // App Theme Green Background
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerIconImage: {
    width: '100%',
    height: '100%',
    borderRadius: 30, // Match container radius
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
