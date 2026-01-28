# AI-Crop-Diagnosis - Complete Folder Structure

```
AI-Crop-Diagnosis/
│
├── .vscode/
│   └── launch.json
│
├── backend/
│   ├── api/
│   │   └── routes/
│   │       ├── chatbot.py
│   │       ├── cost.py
│   │       ├── detect.py
│   │       ├── diagnosis.py
│   │       └── user.py
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   ├── ml/
│   │   ├── __pycache__/
│   │   ├── confidence_handler.py
│   │   ├── crop_classifier.py
│   │   ├── disease_classifier.py
│   │   ├── final_predictor.py
│   │   ├── severity_estimator.py
│   │   ├── split_single_folder.py
│   │   ├── stage_classifier.py
│   │   ├── test_full_prediction.py
│   │   ├── test_predict.py
│   │   ├── test_severity.py
│   │   └── train_disease_model.py
│   │
│   ├── services/
│   │   ├── cost_service.py
│   │   ├── language_service.py
│   │   ├── pesticide_service.py
│   │   ├── voice_service.py
│   │   └── weather_service.py
│   │
│   ├── utils/
│   │   ├── image_quality_check.py
│   │   ├── preprocess.py
│   │   └── validators.py
│   │
│   ├── app.py
│   └── requirements.txt
│
├── database/
│   ├── schemas/
│   │   ├── cost_schema.json
│   │   ├── disease_schema.json
│   │   ├── history_schema.json
│   │   ├── pesticide_schema.json
│   │   └── user_schema.json
│   │
│   ├── seed/
│   │   ├── diseases.json
│   │   ├── pesticides.json
│   │   └── translations.json
│   │
│   └── db_connection.py
│
├── dataset/
│   └── (10,972 files - training/testing images)
│
├── frontend/
│   ├── mobile/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── ConfidenceBar.js
│   │   │   │   ├── DiseaseStageBadge.js
│   │   │   │   ├── ImagePicker.js
│   │   │   │   ├── PredictionCard.js
│   │   │   │   └── VoicePlayer.js
│   │   │   │
│   │   │   ├── navigation/
│   │   │   │   └── AppNavigator.js
│   │   │   │
│   │   │   ├── screens/
│   │   │   │   ├── ChatbotScreen.js
│   │   │   │   ├── CostScreen.js
│   │   │   │   ├── HistoryScreen.js
│   │   │   │   ├── HomeScreen.js
│   │   │   │   └── ResultScreen.js
│   │   │   │
│   │   │   ├── services/
│   │   │   │   ├── api.js
│   │   │   │   ├── translateService.js
│   │   │   │   └── voiceService.js
│   │   │   │
│   │   │   └── utils/
│   │   │       ├── constants.js
│   │   │       └── helpers.js
│   │   │
│   │   ├── assets/
│   │   ├── App.js
│   │   └── package.json
│   │
│   └── web/
│
├── frontend-mobile/
│   ├── .expo/
│   ├── .git/
│   ├── .vscode/
│   │
│   ├── app/
│   │   ├── (tabs)/
│   │   │   ├── _layout.tsx
│   │   │   ├── explore.tsx
│   │   │   └── index.tsx
│   │   │
│   │   ├── _layout.tsx
│   │   └── modal.tsx
│   │
│   ├── assets/
│   │
│   ├── components/
│   │   ├── ui/
│   │   │   ├── collapsible.tsx
│   │   │   ├── icon-symbol.ios.tsx
│   │   │   └── icon-symbol.tsx
│   │   │
│   │   ├── external-link.tsx
│   │   ├── haptic-tab.tsx
│   │   ├── hello-wave.tsx
│   │   ├── parallax-scroll-view.tsx
│   │   ├── themed-text.tsx
│   │   └── themed-view.tsx
│   │
│   ├── constants/
│   │   └── theme.ts
│   │
│   ├── hooks/
│   │   ├── use-color-scheme.ts
│   │   ├── use-color-scheme.web.ts
│   │   └── use-theme-color.ts
│   │
│   ├── node_modules/
│   │
│   ├── scripts/
│   │   └── reset-project.js
│   │
│   ├── .gitignore
│   ├── README.md
│   ├── app.json
│   ├── eslint.config.js
│   ├── expo-env.d.ts
│   ├── package-lock.json
│   ├── package.json
│   └── tsconfig.json
│
├── models/
│   ├── cotton_disease_model.h5
│   ├── rice_disease_model.h5
│   ├── tomato_disease_model.h5
│   └── wheat_disease_model.h5
│
├── venv/
│   └── (21,079 files - Python virtual environment)
│
├── sample.JPG
└── structure.txt
```

## Summary

### Main Directories:

1. **backend/** - Flask/Python backend with ML models and API routes
   - API routes for diagnosis, chatbot, cost estimation, and user management
   - ML modules for crop classification, disease detection, and severity estimation
   - Services for language translation, weather, voice, and pesticide recommendations
   - Utilities for image preprocessing and validation

2. **database/** - Database schemas and seed data
   - JSON schemas for costs, diseases, history, pesticides, and users
   - Seed data for diseases, pesticides, and translations

3. **dataset/** - Training and testing images (10,972 files)

4. **frontend/** - Frontend applications
   - **mobile/** - React Native mobile app (older version)
   - **web/** - Web application (empty/placeholder)

5. **frontend-mobile/** - Expo/React Native TypeScript mobile app (newer version)
   - Tab-based navigation
   - UI components with theming support
   - Custom hooks for color scheme and theme

6. **models/** - Pre-trained H5 models for disease detection
   - Cotton disease model
   - Rice disease model
   - Tomato disease model
   - Wheat disease model

7. **venv/** - Python virtual environment

### Technology Stack:
- **Backend**: Python (Flask), TensorFlow/Keras
- **Frontend Mobile (Old)**: React Native (JavaScript)
- **Frontend Mobile (New)**: Expo + React Native (TypeScript)
- **Database**: JSON-based schemas (likely MongoDB)
- **ML Models**: Keras H5 format
