# 🧪 API Testing Guide

## Quick Test with Sample Image

### 1. Start the Server
```bash
cd backend
python app.py
```

### 2. Register a Test User
```bash
curl -X POST http://localhost:5000/api/user/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@farmer.com\",\"password\":\"farmer123\",\"name\":\"Test Farmer\",\"farm_size\":5,\"preferred_language\":\"en\"}"
```

**Expected Response:**
```json
{
  "message": "User registered successfully",
  "user_id": 1,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Save the token** for next requests!

### 3. Login (if already registered)
```bash
curl -X POST http://localhost:5000/api/user/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@farmer.com\",\"password\":\"farmer123\"}"
```

### 4. Test Disease Detection
```bash
curl -X POST http://localhost:5000/api/diagnosis/detect \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "image=@sample.JPG" \
  -F "crop=tomato"
```

**Expected Response:**
```json
{
  "diagnosis_id": 1,
  "prediction": {
    "crop": "tomato",
    "disease": "Tomato___Bacterial_spot",
    "confidence": 99.35,
    "severity_percent": 4.37,
    "stage": "Healthy Stage",
    "disease_local": "टमाटर - बैक्टीरियल स्पॉट" (if Hindi selected)
  },
  "disease_info": {
    "description": "Bacterial spot is caused by...",
    "symptoms": "Small dark brown spots...",
    "prevention_steps": "Use disease-free seeds..."
  },
  "pesticide_recommendations": {
    "severity_level": "Healthy",
    "recommended_pesticides": [
      {
        "name": "Copper Oxychloride",
        "dosage_per_acre": "2-3 kg in 200-300 liters of water",
        "frequency": "Spray every 7-10 days",
        "cost_per_liter": 450,
        "is_organic": false
      }
    ],
    "treatment_approach": "Preventive measures recommended...",
    "urgency": "low"
  },
  "voice_file": "/api/diagnosis/voice/voice_abc123.mp3"
}
```

### 5. Calculate Treatment Cost
```bash
curl -X POST http://localhost:5000/api/cost/calculate \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{\"diagnosis_id\":1,\"land_area\":5}"
```

**Expected Response:**
```json
{
  "cost_id": 1,
  "cost_data": {
    "treatment": {
      "pesticide_cost": 2250.0,
      "labor_cost": 1000.0,
      "total_treatment_cost": 3250.0,
      "applications_needed": 1
    },
    "prevention": {
      "total_prevention_cost": 3500.0
    },
    "comparison": {
      "treatment_cost": 3250.0,
      "prevention_cost": 3500.0,
      "total_cost": 6750.0
    }
  }
}
```

### 6. Get Diagnosis History
```bash
curl -X GET http://localhost:5000/api/diagnosis/history \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 7. Chat with Bot
```bash
curl -X POST http://localhost:5000/api/chatbot/message \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"What pesticides should I use for tomato blight?\"}"
```

### 8. Update Language Preference
```bash
curl -X PUT http://localhost:5000/api/user/language \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{\"language\":\"hi\"}"
```

## Testing with Postman

1. Import the API endpoints into Postman
2. Create an environment variable `token` after login
3. Use `{{token}}` in Authorization header as `Bearer {{token}}`

## Testing Different Scenarios

### Test Image Quality Rejection
Upload a blurry or very small image - should get error:
```json
{
  "error": "Image quality too low",
  "reason": "Image is too blurry. Please capture a clearer image.",
  "quality_score": 0.15
}
```

### Test Different Crops
```bash
# Rice
-F "crop=rice"

# Wheat
-F "crop=wheat"

# Cotton
-F "crop=cotton"
```

### Test Multilingual Response
Set language to Telugu and detect disease:
```bash
# First update language
curl -X PUT http://localhost:5000/api/user/language \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{\"language\":\"te\"}"

# Then detect disease - response will be in Telugu
curl -X POST http://localhost:5000/api/diagnosis/detect \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "image=@sample.JPG" \
  -F "crop=tomato"
```

## Common Issues

### 401 Unauthorized
- Token expired (tokens last 7 days)
- Token not provided
- Solution: Login again to get new token

### 400 Bad Request
- Missing required fields
- Invalid crop type
- Invalid image format
- Solution: Check request format

### 500 Internal Server Error
- Database connection issue
- ML model not found
- Solution: Check server logs

## Success Indicators

✅ Server starts without errors
✅ Database seeded successfully
✅ User registration works
✅ Login returns token
✅ Disease detection returns results
✅ Voice file is generated
✅ Cost calculation works
✅ Chatbot responds
✅ Multilingual translation works

## Performance Benchmarks

- User Registration: < 100ms
- Login: < 50ms
- Disease Detection: 1-3 seconds
- Cost Calculation: < 100ms
- Chatbot Response: 1-5 seconds (with AI), < 100ms (fallback)
- Voice Generation: 1-2 seconds (cached after first generation)
