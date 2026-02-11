import { Image } from 'expo-image';
import { Platform, StyleSheet, TouchableOpacity, ScrollView, View } from 'react-native';
import { useRouter } from 'expo-router';
import { ExternalLink } from '@/components/external-link';
import ParallaxScrollView from '@/components/parallax-scroll-view';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';
import { Fonts } from '@/constants/theme';
import { Collapsible } from '@/components/ui/collapsible';
import { LinearGradient } from 'expo-linear-gradient';
import { useLanguage } from '@/context/LanguageContext';
import { Translations } from '@/constants/Translations';

// --- Assets ---
const CROPS = [
  { id: 'tomato', image: require('../../assets/images/tomato.png'), color: '#FF6B6B' },
  { id: 'potato', image: require('../../assets/images/potato.png'), color: '#C9A875' },
  { id: 'rice', image: require('../../assets/images/rice.png'), color: '#F4E4BA' },
  { id: 'wheat', image: require('../../assets/images/wheat.png'), color: '#E8C468' },
  { id: 'cotton', image: require('../../assets/images/cotton.png'), color: '#F0F0F0' },
  { id: 'grape', image: require('../../assets/images/grape.png'), color: '#8B5FBF' },
  { id: 'corn', image: require('../../assets/images/corn.png'), color: '#FFD93D' },
];

interface DiseaseData {
  nameKey: keyof typeof Translations['en'];
  descKey: keyof typeof Translations['en'];
  icon: string;
  gradient: [string, string, ...string[]];
  textColor: string;
}

const DISEASE_KEYS: DiseaseData[] = [
  {
    nameKey: 'earlyBlightName',
    descKey: 'earlyBlightDesc',
    icon: 'blur-circular',
    gradient: ['#FFF9C4', '#FFF59D'],
    textColor: '#F57F17',
  },
  {
    nameKey: 'lateBlightName',
    descKey: 'lateBlightDesc',
    icon: 'water-drop',
    gradient: ['#FFCDD2', '#EF9A9A'],
    textColor: '#C62828',
  },
  {
    nameKey: 'leafMoldName',
    descKey: 'leafMoldDesc',
    icon: 'opacity',
    gradient: ['#B2DFDB', '#80CBC4'],
    textColor: '#00695C',
  },
  {
    nameKey: 'rustName',
    descKey: 'rustDesc',
    icon: 'warning',
    gradient: ['#F8BBD0', '#F48FB1'],
    textColor: '#AD1457',
  },
];

export default function ExploreScreen() {
  const router = useRouter();
  const { t } = useLanguage();

  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: '#A8E6A1', dark: '#0D3310' }}
      contentContainerStyle={{ backgroundColor: '#1B5E20' }}
      headerImage={
        <Image
          source={require('@/assets/images/logo.png')}
          style={styles.headerImage}
          contentFit="contain"
        />
      }>

      {/* --- Header Section with Gradient --- */}
      <View style={styles.headerSection}>
        <LinearGradient
          colors={['rgba(165, 214, 167, 0.2)', 'transparent']}
          style={styles.headerGradient}
        />
        <ThemedText type="title" style={styles.mainTitle}>{t('exploreTitle')}</ThemedText>
        <ThemedText style={styles.subtitle}>
          {t('exploreSubtitle')}
        </ThemedText>
      </View>

      {/* --- 1. Supported Crops (Enhanced Horizontal Scroll) --- */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <View style={styles.iconContainer}>
            <IconSymbol name="leaf.fill" size={22} color="#FFF" />
          </View>
          <View style={{ flex: 1 }}>
            <ThemedText type="subtitle" style={styles.sectionTitle}>{t('cropsDiagnoseTitle')}</ThemedText>
            <ThemedText style={styles.sectionSubtext}>{t('cropsDiagnoseSubtitle')}</ThemedText>
          </View>
        </View>

        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.cropsContainer}
          decelerationRate="fast"
          snapToInterval={116}
        >
          {CROPS.map((crop) => (
            <TouchableOpacity
              key={crop.id}
              style={styles.cropCard}
              activeOpacity={0.7}
            >
              <View style={[styles.cropImageContainer, { backgroundColor: crop.color + '20' }]}>
                <Image source={crop.image} style={styles.cropImage} contentFit="contain" />
              </View>
              <ThemedText type="defaultSemiBold" style={styles.cropName}>{t(`crop_${crop.id}` as any)}</ThemedText>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* --- 2. Common Diseases (Enhanced Grid) --- */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <View style={[styles.iconContainer, { backgroundColor: '#FFB74D' }]}>
            <IconSymbol name="exclamationmark.triangle.fill" size={22} color="#FFF" />
          </View>
          <View style={{ flex: 1 }}>
            <ThemedText type="subtitle" style={styles.sectionTitle}>{t('commonThreatsTitle')}</ThemedText>
            <ThemedText style={styles.sectionSubtext}>{t('commonThreatsSubtitle')}</ThemedText>
          </View>
        </View>

        <View style={styles.diseaseGrid}>
          {DISEASE_KEYS.map((disease, index) => (
            <TouchableOpacity
              key={index}
              style={styles.diseaseCard}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={disease.gradient}
                style={styles.diseaseGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
              >
                <View style={styles.diseaseHeader}>
                  <View style={[styles.diseaseIconContainer, { backgroundColor: disease.textColor + '20' }]}>
                    <MaterialIcons name={disease.icon as any} size={18} color={disease.textColor} />
                  </View>
                  <ThemedText type="defaultSemiBold" style={[styles.diseaseName, { color: disease.textColor }]}>
                    {t(disease.nameKey)}
                  </ThemedText>
                </View>
                <ThemedText style={styles.diseaseDesc}>{t(disease.descKey)}</ThemedText>
              </LinearGradient>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* --- 3. Daily Tip (Premium Card) --- */}
      <View style={styles.tipCardWrapper}>
        <LinearGradient
          colors={['#FFF9C4', '#FFECB3', '#FFE082']}
          style={styles.tipCard}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          <View style={styles.tipIconWrapper}>
            <View style={styles.tipIconOuter}>
              <View style={styles.tipIconInner}>
                <IconSymbol name="lightbulb.fill" size={28} color="#F57F17" />
              </View>
            </View>
          </View>

          <View style={{ flex: 1 }}>
            <View style={styles.tipHeader}>
              <ThemedText type="subtitle" style={styles.tipTitle}>{t('dailyTipTitle')}</ThemedText>
              <View style={styles.tipBadge}>
                <ThemedText style={styles.tipBadgeText}>{t('dailyTipBadge')}</ThemedText>
              </View>
            </View>
            <ThemedText style={styles.tipText}>
              {t('dailyTipContent')}
            </ThemedText>
          </View>
        </LinearGradient>
      </View>

      {/* --- 4. Detailed Guides (Enhanced Collapsible) --- */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <View style={[styles.iconContainer, { backgroundColor: '#66BB6A' }]}>
            <IconSymbol name="book.fill" size={22} color="#FFF" />
          </View>
          <View style={{ flex: 1 }}>
            <ThemedText type="subtitle" style={styles.sectionTitle}>{t('detailedGuidesTitle')}</ThemedText>
            <ThemedText style={styles.sectionSubtext}>{t('detailedGuidesSubtitle')}</ThemedText>
          </View>
        </View>

        <View style={styles.guidesContainer}>
          <Collapsible title={t('preventionStrategies')}>
            <View style={styles.guideContent}>
              <View style={styles.guideItem}>
                <View style={styles.guideBullet}>
                  <ThemedText style={styles.guideBulletText}>1</ThemedText>
                </View>
                <View style={{ flex: 1 }}>
                  <ThemedText type="defaultSemiBold" style={styles.guideItemTitle}>{t('cropRotation')}</ThemedText>
                  <ThemedText style={styles.guideItemText}>{t('cropRotationDesc')}</ThemedText>
                </View>
              </View>

              <View style={styles.guideItem}>
                <View style={styles.guideBullet}>
                  <ThemedText style={styles.guideBulletText}>2</ThemedText>
                </View>
                <View style={{ flex: 1 }}>
                  <ThemedText type="defaultSemiBold" style={styles.guideItemTitle}>{t('properSpacing')}</ThemedText>
                  <ThemedText style={styles.guideItemText}>{t('properSpacingDesc')}</ThemedText>
                </View>
              </View>

              <View style={styles.guideItem}>
                <View style={styles.guideBullet}>
                  <ThemedText style={styles.guideBulletText}>3</ThemedText>
                </View>
                <View style={{ flex: 1 }}>
                  <ThemedText type="defaultSemiBold" style={styles.guideItemTitle}>{t('mulching')}</ThemedText>
                  <ThemedText style={styles.guideItemText}>{t('mulchingDesc')}</ThemedText>
                </View>
              </View>
            </View>
          </Collapsible>

          <Collapsible title={t('usingTheApp')}>
            <View style={styles.guideContent}>
              <View style={styles.guideItem}>
                <View style={styles.guideBullet}>
                  <ThemedText style={styles.guideBulletText}>1</ThemedText>
                </View>
                <ThemedText style={styles.guideItemText}>{t('guideStep1')}</ThemedText>
              </View>

              <View style={styles.guideItem}>
                <View style={styles.guideBullet}>
                  <ThemedText style={styles.guideBulletText}>2</ThemedText>
                </View>
                <ThemedText style={styles.guideItemText}>{t('guideStep2')}</ThemedText>
              </View>

              <View style={styles.guideItem}>
                <View style={styles.guideBullet}>
                  <ThemedText style={styles.guideBulletText}>3</ThemedText>
                </View>
                <ThemedText style={styles.guideItemText}>{t('guideStep3')}</ThemedText>
              </View>

              <View style={styles.guideItem}>
                <View style={styles.guideBullet}>
                  <ThemedText style={styles.guideBulletText}>4</ThemedText>
                </View>
                <ThemedText style={styles.guideItemText}>{t('guideStep4')}</ThemedText>
              </View>
            </View>
          </Collapsible>
        </View>
      </View>

      <View style={{ height: 40 }} />
    </ParallaxScrollView>
  );
}
const styles = StyleSheet.create({
  headerImage: {
    height: '100%',
    width: '100%',
    bottom: 0,
    left: 0,
    position: 'absolute',
  },
  headerContentContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    paddingHorizontal: 20,
    gap: 15,
    marginTop: 20,
  },
  logoImage: {
    height: 100,
    width: 100,
    borderRadius: 50,
  },
  headerTextContainer: {
    flex: 1,
    justifyContent: 'center',
  },
  headerAppName: {
    color: '#FFF',
    fontSize: 22,
    fontWeight: '800',
    textShadowColor: 'rgba(0, 0, 0, 0.5)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  headerAppTagline: {
    color: '#E8F5E9',
    fontSize: 14,
    fontWeight: '600',
    marginTop: 4,
    textShadowColor: 'rgba(0, 0, 0, 0.5)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
  headerSection: {
    position: 'relative',
    marginBottom: 32,
    overflow: 'hidden',
  },
  headerGradient: {
    position: 'absolute',
    top: -20,
    left: -20,
    right: -20,
    height: 150,
    borderRadius: 100,
  },
  mainTitle: {
    fontFamily: Fonts.rounded,
    color: '#FFF',
    fontSize: 36,
    marginBottom: 8,
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#C8E6C9',
    lineHeight: 24,
  },
  section: {
    marginBottom: 36,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 20,
  },
  iconContainer: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#66BB6A',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#FFFFFF',
    letterSpacing: 0.5,
  },
  sectionSubtext: {
    fontSize: 13,
    color: '#A5D6A7',
    marginTop: 2,
  },
  cropsContainer: {
    paddingRight: 16,
    gap: 16,
  },
  cropCard: {
    width: 100,
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 6,
  },
  cropImageContainer: {
    width: 76,
    height: 76,
    borderRadius: 38,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  cropImage: {
    width: 56,
    height: 56,
  },
  cropName: {
    fontSize: 14,
    textAlign: 'center',
    color: '#2E7D32',
  },
  diseaseGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
  },
  diseaseCard: {
    width: '47%',
    borderRadius: 20,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 5,
  },
  diseaseGradient: {
    padding: 18,
    minHeight: 140,
    justifyContent: 'space-between',
  },
  diseaseHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 12,
  },
  diseaseIconContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  diseaseName: {
    fontSize: 15,
    fontWeight: '700',
    flex: 1,
  },
  diseaseDesc: {
    fontSize: 12,
    color: '#424242',
    lineHeight: 18,
  },
  tipCardWrapper: {
    marginBottom: 36,
    shadowColor: '#F57F17',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  tipCard: {
    borderRadius: 24,
    padding: 24,
    borderWidth: 2,
    borderColor: 'rgba(245, 127, 23, 0.2)',
    flexDirection: 'row',
    gap: 16,
  },
  tipIconWrapper: {
    paddingTop: 4,
  },
  tipIconOuter: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(255, 255, 255, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  tipIconInner: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  tipHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  tipTitle: {
    color: '#E65100',
    fontWeight: '800',
    fontSize: 18,
  },
  tipBadge: {
    backgroundColor: '#F57F17',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  tipBadgeText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '700',
  },
  tipText: {
    fontSize: 14,
    color: '#5D4037',
    lineHeight: 22,
  },
  guidesContainer: {
    gap: 12,
  },
  guideContent: {
    gap: 16,
    paddingTop: 8,
  },
  guideItem: {
    flexDirection: 'row',
    gap: 12,
    alignItems: 'flex-start',
  },
  guideBullet: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#66BB6A',
    justifyContent: 'center',
    alignItems: 'center',
  },
  guideBulletText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '700',
  },
  guideItemTitle: {
    color: '#E8F5E9',
    fontSize: 15,
    marginBottom: 4,
  },
  guideItemText: {
    color: '#C8E6C9',
    fontSize: 14,
    lineHeight: 20,
  },
});
