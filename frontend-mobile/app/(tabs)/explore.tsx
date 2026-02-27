import { Image } from 'expo-image';
import { Platform, StyleSheet, TouchableOpacity, ScrollView, View, Dimensions, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { ThemedText } from '@/components/themed-text';
import { IconSymbol, IconSymbolName } from '@/components/ui/icon-symbol';
import { Fonts } from '@/constants/theme';
import { Collapsible } from '@/components/ui/collapsible';
import { LinearGradient } from 'expo-linear-gradient';
import { useLanguage } from '@/context/LanguageContext';
import { useAppTheme } from '@/context/ThemeContext';
import { Colors } from '@/constants/theme';

const { width } = Dimensions.get('window');

interface DiseaseData {
  name: string;
  desc: string;
  icon: IconSymbolName;
  gradient: [string, string, ...string[]];
  darkGradient: [string, string];
  textColor: string;
}

export default function ExploreScreen() {
  const router = useRouter();
  const { t } = useLanguage();
  const { isDarkMode, colorScheme } = useAppTheme();
  const themeParams = Colors[colorScheme];

  const CROPS = [
    { id: 'tomato', name: t('crop_tomato'), image: require('../../assets/images/tomato.png'), color: '#FF7676' },
    { id: 'potato', name: t('crop_potato'), image: require('../../assets/images/potato.png'), color: '#D4B886' },
    { id: 'rice', name: t('crop_rice'), image: require('../../assets/images/rice.png'), color: '#F7E7C3' },
    { id: 'grape', name: t('crop_grape'), image: require('../../assets/images/grape.png'), color: '#9B72CF' },
    { id: 'maize', name: t('crop_maize'), image: require('../../assets/images/maize.png'), color: '#FFE05C' },
  ];

  const DISEASES: DiseaseData[] = [
    {
      name: t('diseaseEarlyBlight'),
      desc: t('diseaseEarlyBlightDesc'),
      icon: 'circle.circle.fill',
      gradient: ['rgba(255, 245, 157, 0.9)', 'rgba(255, 249, 196, 0.9)'],
      darkGradient: ['#FFF59D', '#FFF9C4'],
      textColor: '#F57F17',
    },
    {
      name: t('diseaseLateBlight'),
      desc: t('diseaseLateBlightDesc'),
      icon: 'drop.triangle.fill',
      gradient: ['rgba(239, 154, 154, 0.9)', 'rgba(255, 205, 210, 0.9)'],
      darkGradient: ['#EF9A9A', '#FFCDD2'],
      textColor: '#C62828',
    },
    {
      name: t('diseaseLeafMold'),
      desc: t('diseaseLeafMoldDesc'),
      icon: 'humidity.fill',
      gradient: ['rgba(128, 203, 196, 0.9)', 'rgba(178, 223, 219, 0.9)'],
      darkGradient: ['#80CBC4', '#B2DFDB'],
      textColor: '#00695C',
    },
    {
      name: t('diseaseRust'),
      desc: t('diseaseRustDesc'),
      icon: 'allergens',
      gradient: ['rgba(244, 143, 177, 0.9)', 'rgba(248, 187, 208, 0.9)'],
      darkGradient: ['#F48FB1', '#F8BBD0'],
      textColor: '#AD1457',
    },
  ];

  return (
    <View style={[styles.container, { backgroundColor: isDarkMode ? themeParams.background : '#F2F6F2' }]}>
      {/* Absolute Header Gradient that bleeds down */}
      <LinearGradient
        colors={isDarkMode ? ['#0d2b0f', '#124016', themeParams.background] : ['#103e14', '#1B5E20', '#F2F6F2']}
        locations={[0, 0.3, 0.6]}
        style={styles.absoluteBackground}
      />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {/* --- Floating Hero Section --- */}
        <SafeAreaView>
          <View style={styles.heroWrapper}>
            <View style={styles.heroContent}>
              <IconSymbol name="leaf.fill" size={32} color="#A5D6A7" style={styles.heroIcon} />
              <ThemedText style={styles.heroTitle}>{t('exploreTitle')}</ThemedText>
              <ThemedText style={styles.heroSubtitle}>{t('exploreSubtitle')}</ThemedText>
            </View>

            {/* Decorative Abstract Shapes */}
            <View style={styles.shape1} />
            <View style={styles.shape2} />
          </View>
        </SafeAreaView>

        <View style={[styles.mainCanvas, { backgroundColor: isDarkMode ? themeParams.background : '#F2F6F2' }]}>

          {/* --- 1. Supported Crops (Floating Pills) --- */}
          <View style={styles.sectionHeader}>
            <ThemedText style={[styles.sectionTitle, { color: isDarkMode ? '#A5D6A7' : '#1B5E20' }]}>{t('cropsTitle')}</ThemedText>
          </View>

          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.cropsContainer}
            decelerationRate="fast"
            snapToInterval={100}
          >
            {CROPS.map((crop) => (
              <TouchableOpacity
                key={crop.id}
                style={styles.cropCard}
                activeOpacity={0.8}
              >
                <View style={[styles.cropImageContainer, { backgroundColor: 'transparent' }]}>
                  <Image source={crop.image} style={styles.cropImage} contentFit="contain" />
                </View>
                <ThemedText style={[styles.cropName, { color: isDarkMode ? '#fff' : '#2E3D2E' }]}>{crop.name}</ThemedText>
              </TouchableOpacity>
            ))}
          </ScrollView>

          <View style={styles.divider} />

          {/* --- 2. Threat Identification (Premium Grid) --- */}
          <View style={styles.sectionHeader}>
            <ThemedText style={[styles.sectionTitle, { color: isDarkMode ? '#A5D6A7' : '#1B5E20' }]}>{t('threatsTitle')}</ThemedText>
            <ThemedText style={[styles.sectionSubtext, { color: isDarkMode ? '#aaa' : '#666' }]}>{t('threatsSubtitle')}</ThemedText>
          </View>

          <View style={styles.diseaseGrid}>
            {DISEASES.map((disease, index) => (
              <TouchableOpacity
                key={index}
                style={styles.diseaseCard}
                activeOpacity={0.9}
              >
                <LinearGradient
                  colors={isDarkMode ? disease.darkGradient : disease.gradient}
                  style={[styles.diseaseGradient, { borderColor: isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(255, 255, 255, 0.8)' }]}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                >
                  <View style={styles.diseaseHeader}>
                    <View style={[styles.diseaseIconContainer, { backgroundColor: isDarkMode ? 'rgba(255,255,255,0.2)' : '#FFFFFF' }]}>
                      <IconSymbol name={disease.icon} size={20} color={disease.textColor} />
                    </View>
                  </View>
                  <View>
                    <ThemedText style={[styles.diseaseName, { color: disease.textColor }]}>{disease.name}</ThemedText>
                    <ThemedText style={[styles.diseaseDesc, { color: disease.textColor }]}>{disease.desc}</ThemedText>
                  </View>
                </LinearGradient>
              </TouchableOpacity>
            ))}
          </View>

          {/* --- 3. Daily Expert Tip (Masterpiece Card) --- */}
          <View style={styles.tipCardWrapper}>
            <LinearGradient
              colors={isDarkMode ? ['#3e2723', '#4e342e'] : ['#FFF8E1', '#FFECB3']}
              style={[styles.tipCard, isDarkMode && { borderColor: '#5d4037' }]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
            >
              <View style={styles.tipHeaderRow}>
                <View style={[styles.tipIconBadge, isDarkMode && { backgroundColor: '#ffca28' }]}>
                  <IconSymbol name="lightbulb.fill" size={24} color={isDarkMode ? '#3e2723' : '#F57F17'} />
                </View>
                <View style={styles.tipLabelTag}>
                  <ThemedText style={styles.tipLabelText}>{t('dailyTipTitle')}</ThemedText>
                </View>
              </View>

              <ThemedText style={[styles.tipMainText, isDarkMode && { color: '#ffecb3' }]}>
                {t('dailyTipContent')}
              </ThemedText>
            </LinearGradient>
          </View>

          {/* --- 4. Detailed Guides (Clean Accordions) --- */}
          <View style={styles.sectionHeader}>
            <ThemedText style={[styles.sectionTitle, { color: isDarkMode ? '#A5D6A7' : '#1B5E20' }]}>{t('guidesTitle')}</ThemedText>
          </View>

          <View style={styles.guidesContainer}>
            <Collapsible title={t('preventionStrategies')} titleColor={isDarkMode ? '#81C784' : '#1B5E20'}>
              <View style={styles.guideContent}>
                {[
                  { num: '1', title: t('guideRotationTitle'), desc: t('guideRotationDesc') },
                  { num: '2', title: t('guideSpacingTitle'), desc: t('guideSpacingDesc') },
                  { num: '3', title: t('guideMulchingTitle'), desc: t('guideMulchingDesc') }
                ].map((item, idx) => (
                  <View key={idx} style={[styles.guideItemRow, { backgroundColor: isDarkMode ? '#1e1e1e' : '#FFF', borderColor: isDarkMode ? '#333' : 'rgba(0,0,0,0.02)' }]}>
                    <View style={styles.guideNumberBadge}>
                      <ThemedText style={styles.guideNumberText}>{item.num}</ThemedText>
                    </View>
                    <View style={{ flex: 1 }}>
                      <ThemedText style={[styles.guideItemTitle, { color: isDarkMode ? '#fff' : '#2E3D2E' }]}>{item.title}</ThemedText>
                      <ThemedText style={[styles.guideItemText, { color: isDarkMode ? '#aaa' : '#666' }]}>{item.desc}</ThemedText>
                    </View>
                  </View>
                ))}
              </View>
            </Collapsible>

            <Collapsible title={t('usingTheApp')} titleColor={isDarkMode ? '#81C784' : '#1B5E20'}>
              <View style={styles.guideContent}>
                {[t('guideAppStep1'), t('guideAppStep2'), t('guideAppStep3'), t('guideAppStep4')].map((step, idx) => (
                  <View key={idx} style={[styles.guideItemRow, { backgroundColor: isDarkMode ? '#1e1e1e' : '#FFF', borderColor: isDarkMode ? '#333' : 'rgba(0,0,0,0.02)' }]}>
                    <View style={[styles.guideNumberBadge, { backgroundColor: '#4CAF50' }]}>
                      <ThemedText style={styles.guideNumberText}>{idx + 1}</ThemedText>
                    </View>
                    <View style={{ flex: 1, justifyContent: 'center' }}>
                      <ThemedText style={[styles.guideItemText, { marginTop: 0, color: isDarkMode ? '#aaa' : '#666' }]}>{step}</ThemedText>
                    </View>
                  </View>
                ))}
              </View>
            </Collapsible>
          </View>

          <View style={{ height: 100 }} />
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F6F2', // Soft, organic off-white
  },
  absoluteBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 600,
  },
  scrollContent: {
    flexGrow: 1,
  },
  heroWrapper: {
    paddingTop: Platform.OS === 'ios' ? 70 : 90,
    paddingHorizontal: 24,
    paddingBottom: 40,
    position: 'relative',
    overflow: 'hidden',
  },
  heroContent: {
    position: 'relative',
    zIndex: 2,
  },
  heroIcon: {
    marginBottom: 16,
    opacity: 0.9,
  },
  heroTitle: {
    fontSize: 44,
    fontWeight: '900',
    color: '#FFFFFF',
    letterSpacing: -1.5,
    lineHeight: 50,
  },
  heroSubtitle: {
    fontSize: 18,
    color: 'rgba(255, 255, 255, 0.85)',
    marginTop: 12,
    fontWeight: '500',
    lineHeight: 26,
    paddingRight: 40,
  },
  shape1: {
    position: 'absolute',
    width: 250,
    height: 250,
    borderRadius: 125,
    backgroundColor: '#4CAF50',
    opacity: 0.15,
    top: -50,
    right: -80,
    zIndex: 1,
  },
  shape2: {
    position: 'absolute',
    width: 150,
    height: 150,
    borderRadius: 75,
    backgroundColor: '#A5D6A7',
    opacity: 0.1,
    bottom: -20,
    right: 50,
    zIndex: 1,
  },
  mainCanvas: {
    backgroundColor: '#F2F6F2',
    borderTopLeftRadius: 40,
    borderTopRightRadius: 40,
    paddingTop: 32,
    flex: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -10 },
    shadowOpacity: 0.05,
    shadowRadius: 20,
    elevation: 10,
  },
  sectionHeader: {
    paddingHorizontal: 24,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#1B5E20',
    letterSpacing: -0.5,
  },
  sectionSubtext: {
    fontSize: 15,
    color: '#666',
    marginTop: 4,
    fontWeight: '500',
  },
  cropsContainer: {
    paddingHorizontal: 24,
    paddingBottom: 24,
    flexDirection: 'row',
    gap: 16,
  },
  cropCard: {
    width: 90,
    alignItems: 'center',
    padding: 12,
  },
  cropImageContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  cropImage: {
    width: 60,
    height: 60,
  },
  cropName: {
    fontSize: 14,
    textAlign: 'center',
    color: '#2E3D2E',
    fontWeight: '700',
  },
  divider: {
    height: 1,
    backgroundColor: 'rgba(0,0,0,0.05)',
    marginHorizontal: 24,
    marginBottom: 32,
  },
  diseaseGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 24,
    gap: 16,
    marginBottom: 40,
  },
  diseaseCard: {
    width: '47%',
    borderRadius: 28,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.08,
    shadowRadius: 20,
    elevation: 6,
  },
  diseaseGradient: {
    padding: 20,
    minHeight: 180,
    justifyContent: 'space-between',
    borderRadius: 28,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.8)',
  },
  diseaseHeader: {
    alignItems: 'flex-start',
  },
  diseaseIconContainer: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
  },
  diseaseName: {
    fontSize: 18,
    fontWeight: '800',
    marginBottom: 6,
    letterSpacing: -0.5,
  },
  diseaseDesc: {
    fontSize: 13,
    fontWeight: '600',
    opacity: 0.8,
    lineHeight: 18,
  },
  tipCardWrapper: {
    paddingHorizontal: 24,
    marginBottom: 44,
    shadowColor: '#FFB300',
    shadowOffset: { width: 0, height: 16 },
    shadowOpacity: 0.2,
    shadowRadius: 24,
    elevation: 12,
  },
  tipCard: {
    borderRadius: 32,
    padding: 28,
    borderWidth: 1,
    borderColor: '#FFF',
  },
  tipHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    gap: 12,
  },
  tipIconBadge: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
  },
  tipLabelTag: {
    backgroundColor: '#FFCC80',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  tipLabelText: {
    color: '#E65100',
    fontSize: 13,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  tipMainText: {
    fontSize: 16,
    color: '#5D4037',
    lineHeight: 26,
    fontWeight: '600',
  },
  guidesContainer: {
    paddingHorizontal: 24,
    gap: 16,
  },
  guideContent: {
    paddingTop: 16,
    paddingBottom: 8,
    gap: 20,
  },
  guideItemRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 16,
    backgroundColor: '#FFF',
    padding: 20,
    borderRadius: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.04,
    shadowRadius: 12,
    elevation: 2,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.02)',
  },
  guideNumberBadge: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#81C784',
    justifyContent: 'center',
    alignItems: 'center',
  },
  guideNumberText: {
    color: '#FFF',
    fontSize: 15,
    fontWeight: '800',
  },
  guideItemTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#2E3D2E',
    marginBottom: 6,
    letterSpacing: -0.3,
  },
  guideItemText: {
    fontSize: 15,
    color: '#666',
    lineHeight: 22,
    fontWeight: '500',
  },
});