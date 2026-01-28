# 🌾 AI Crop Diagnosis System

A comprehensive, farmer-friendly mobile and web application for crop disease detection, diagnosis, and treatment recommendations with multilingual support.

## ✨ Features

### 🔍 Disease Detection (Epic 1)
- Upload or capture crop images in real-time
- Automatic disease detection with confidence scores
- Support for multiple crops: Tomato, Rice, Wheat, Cotton
- Handles different lighting conditions
- Rejects blurred or low-quality images
- Fast detection results (< 3 seconds)

### 💊 Diagnosis & Treatment (Epic 2)
- Recommended pesticides for detected diseases
- Correct dosage and application frequency
- Prevention steps to avoid recurrence
- Organic treatment alternatives
- Government-approved pesticide suggestions
- Disease severity-based treatment advice
- Weather-aware prevention tips
- Warnings for harmful pesticide combinations

### 💰 Cost Calculation (Epic 3)
- Input land area for accurate cost estimation
- Automatic pesticide quantity calculation
- Total treatment cost estimation
- Prevention cost comparison
- Severity-based cost adjustments
- Downloadable cost summaries for loans/subsidies

### 📊 Disease Progression Tracking (Epic 4)
- Current severity level detection
- Early-stage infection alerts
- Track disease spread over time
- Visual indicators of progression
- Upload follow-up images for comparison
- Historical disease progression records

### 🌐 Multilingual Support (Epic 5)
- **Supported Languages**: English, Hindi, Telugu, Tamil, Kannada, Marathi
- Diagnosis results in local language
- Pesticide instructions translated
- Prevention steps in local language
- Voice output for all information
- Play/pause/replay voice controls
- Language preference saved automatically

### 💬 Chatbot Assistance (Epic 6)
- Ask disease-related questions
- Explanation of diagnosis results
- Pesticide usage guidance
- Prevention advice
- Multilingual chat support
- Voice-based interaction
- 24/7 availability

### 👤 User Profile & History (Epic 7)
- Personal farmer profile
- Secure login and authentication
- Past disease detection history
- Treatment history tracking
- Disease progression over time
- Saved cost reports
- Multi-device access
- Secure data storage

## 🏗️ Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite
- **ML Framework**: TensorFlow/Keras
- **Image Processing**: OpenCV
- **Authentication**: JWT (JSON Web Tokens)
- **Translation**: Google Translate (googletrans)
- **Text-to-Speech**: gTTS (Google Text-to-Speech)
- **Chatbot**: Google Gemini AI

### Frontend (Mobile)
- **Framework**: Expo + React Native (TypeScript)
- **Navigation**: React Navigation
- **State Management**: React Hooks
- **API Client**: Axios
- **Audio**: Expo AV

## 📁 Project Structure

```
AI-Crop-Diagnosis/
├── backend/
│   ├── api/routes/          # API endpoints
│   ├── config/              # Configuration
│   ├── ml/                  # ML models (your existing code)
│   ├── services/            # Business logic services
│   ├── utils/               # Utility functions
│   ├── app.py              # Main Flask application
│   └── requirements.txt     # Python dependencies
├── database/
│   ├── seed/               # Seed data
│   ├── db_connection.py    # Database connection
│   └── crop_diagnosis.db   # SQLite database (auto-created)
├── models/                  # Pre-trained H5 models
├── frontend-mobile/         # Expo React Native app
└── uploads/                # Uploaded images (auto-created)
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher (for mobile app)
- pip (Python package manager)
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**
   ```bash
   # Copy the example file
   copy .env.example .env    # Windows
   cp .env.example .env      # Linux/Mac
   ```

5. **Edit .env file** (optional - API keys)
   ```
   # Add your API keys if you have them (optional)
   GOOGLE_GEMINI_API_KEY=your_key_here
   WEATHER_API_KEY=your_key_here
   ```

6. **Initialize database with seed data**
   ```bash
   cd ../database/seed
   python seed_database.py
   cd ../../backend
   ```

7. **Run the server**
   ```bash
   python app.py
   ```

   Server will start at `http://localhost:5000`

### Testing the Backend

1. **Check health**
   ```bash
   curl http://localhost:5000/health
   ```

2. **View API documentation**
   ```bash
   curl http://localhost:5000/api
   ```

3. **Test disease detection** (with your sample image)
   ```bash
   # First register a user
   curl -X POST http://localhost:5000/api/user/register \
     -H "Content-Type: application/json" \
     -d "{\"email\":\"farmer@example.com\",\"password\":\"test123\",\"name\":\"Test Farmer\"}"
   
   # Then login to get token
   curl -X POST http://localhost:5000/api/user/login \
     -H "Content-Type: application/json" \
     -d "{\"email\":\"farmer@example.com\",\"password\":\"test123\"}"
   
   # Use the token to detect disease
   curl -X POST http://localhost:5000/api/diagnosis/detect \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -F "image=@../sample.JPG" \
     -F "crop=tomato"
   ```

## 📱 API Endpoints

### User Management
- `POST /api/user/register` - Register new user
- `POST /api/user/login` - Login user
- `GET /api/user/profile` - Get user profile (requires auth)
- `PUT /api/user/profile` - Update profile (requires auth)
- `PUT /api/user/language` - Update language preference (requires auth)

### Disease Diagnosis
- `POST /api/diagnosis/detect` - Detect disease from image (requires auth)
- `GET /api/diagnosis/history` - Get diagnosis history (requires auth)
- `GET /api/diagnosis/<id>` - Get diagnosis details (requires auth)
- `GET /api/diagnosis/voice/<filename>` - Get voice file

### Cost Calculation
- `POST /api/cost/calculate` - Calculate treatment costs (requires auth)
- `GET /api/cost/report/<diagnosis_id>` - Get cost report (requires auth)

### Chatbot
- `POST /api/chatbot/message` - Send message to chatbot (requires auth)
- `GET /api/chatbot/history` - Get chat history (requires auth)

## 🔑 Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

Get the token by logging in via `/api/user/login`.

## 🌍 Supported Crops & Diseases

### Tomato
- Healthy
- Bacterial spot
- Early blight
- Late blight
- Leaf Mold
- Septoria leaf spot
- Spider mites
- Target Spot
- Yellow Leaf Curl Virus
- Tomato mosaic virus

### Rice
- Healthy
- Brown Spot
- Hispa
- Leaf Blast

### Wheat
- Healthy
- Brown rust
- Yellow rust
- Loose Smut

### Cotton
- Healthy
- Bacterial Blight
- Curl Virus
- Leaf Hopper Jassids

## 🗣️ Supported Languages

- English (en)
- Hindi (hi) - हिंदी
- Telugu (te) - తెలుగు
- Tamil (ta) - தமிழ்
- Kannada (kn) - ಕನ್ನಡ
- Marathi (mr) - मराठी

## 📊 Database Schema

### Users
- User authentication and profile information
- Farm details and preferences
- Language preferences

### Diagnosis History
- All disease detections
- Images, confidence scores, severity
- GPS coordinates (optional)

### Pesticide Recommendations
- Linked to each diagnosis
- Dosage, frequency, cost
- Organic alternatives

### Cost Calculations
- Treatment and prevention costs
- Land area-based calculations

### Chatbot Conversations
- Chat history for each user
- Multilingual support

## 🔧 Configuration

Edit `backend/config/settings.py` to customize:
- File upload limits
- Image quality thresholds
- Cost calculation defaults
- Severity thresholds
- Supported languages

## 🐛 Troubleshooting

### Database Issues
```bash
# Delete and recreate database
rm database/crop_diagnosis.db
cd database/seed
python seed_database.py
```

### Module Import Errors
```bash
# Make sure you're in the virtual environment
# and all dependencies are installed
pip install -r backend/requirements.txt
```

### Port Already in Use
```bash
# Change PORT in backend/.env file
PORT=5001
```

## 📝 Notes

- The system uses your existing ML models in the `models/` directory
- No crop classification needed - users select crop type manually
- All translations use free Google Translate library (no API key needed)
- Voice generation uses free gTTS library
- Chatbot works with fallback responses if no Gemini API key provided
- Weather integration is optional (works without API key)

## 🎯 Next Steps

1. ✅ Backend is complete and ready to use
2. 📱 Frontend mobile app needs to be built (React Native/Expo)
3. 🌐 Web frontend is optional
4. 🧪 Testing and deployment

## 👨‍🌾 For Farmers

This system is designed to be:
- **Simple**: Just take a photo of your crop
- **Fast**: Get results in seconds
- **Accurate**: AI-powered disease detection
- **Helpful**: Clear treatment recommendations
- **Affordable**: Cost calculations for planning
- **Local**: Available in your language
- **Voice-enabled**: Listen instead of reading

## 📄 License

This project is for educational and agricultural support purposes.

## 🤝 Support

For issues or questions, please check the API documentation at `/api` endpoint.
