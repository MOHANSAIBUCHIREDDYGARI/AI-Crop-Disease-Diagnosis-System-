# Developer Documentation (DevDocs)

## 1. Project Overview

The **AI Crop Diagnosis System** is a comprehensive solution designed to help farmers detect crop diseases using deep learning. It consists of a mobile application for end-users and a backend server that handles image processing, disease prediction, and data management.

**Key Features:**
*   **Disease Detection:** Uses TensorFlow/Keras models to identify diseases in crops (Grape, Maize, Potato, Rice, Tomato).
*   **Multilingual Support:** English, Hindi, Telugu, Tamil, Kannada, Marathi.
*   **Treatment Recommendations:** Provides chemical and organic treatment options.
*   **Chatbot:** AI-powered assistant (Gemini) for farming queries.
*   **Offline First:** Critical features work without internet.

---

## 2. Setup Guide

### Prerequisites
*   **Python 3.8+**
*   **Node.js 18+** & **npm**
*   **Expo Go** app on your mobile device (Android/iOS)

### Backend Setup
1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Environment Configuration:**
    Create a `.env` file in `backend/` with the following:
    ```env
    GOOGLE_GEMINI_API_KEY=your_gemini_key
    WEATHER_API_KEY=your_openweather_key
    SECRET_KEY=dev_secret_key
    PORT=5000
    DEBUG=True
    ```
5.  **Initialize Database:**
    ```bash
    cd ../database/seed
    python seed_database.py
    cd ../../backend
    ```
6.  **Run the Server:**
    ```bash
    python app.py
    # Server runs on http://localhost:5000
    ```

### Frontend Setup
1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend-mobile
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Start the generic Metro bundler:**
    ```bash
    npx expo start
    ```
4.  **Run on Device:**
    *   Scan the QR code with **Expo Go**.
    *   Ensure your phone and computer are on the **same Wi-Fi network**.

---

## 3. Architecture / Design

### System Architecture
The system follows a typical Client-Server architecture.

```mermaid
graph TD
    Client[Mobile App (React Native/Expo)]
    Server[Backend API (Flask)]
    DB[(SQLite Database)]
    AI[AI Models (TensorFlow)]
    Ext[External APIs]

    Client -- HTTP/JSON --> Server
    Server -- SQL --> DB
    Server -- Inference --> AI
    Server -- Requests --> Ext
    Ext --> |Gemini/Weather| Server
```

### Modules
*   **Frontend (`frontend-mobile`):**
    *   `app/`: Screens and routing (Expo Router).
    *   `components/`: Reusable UI components.
    *   `services/`: API integration (`api.ts`).
    *   `context/`: State management (Auth, Language).
*   **Backend (`backend`):**
    *   `app.py`: Entry point.
    *   `api/routes/`: Blueprints for `user`, `diagnosis`, `chatbot`, `cost`, `weather`.
    *   `database/`: Database connection and schema interactions.
    *   `ml/`: Model loading and prediction logic.
*   **Database (`database`):**
    *   SQLite file (`crop_diagnosis.db`).
    *   Seeding scripts (`seed/`).

---

## 4. API Documentation

Base URL: `http://localhost:5000/api`

### User Endpoints
*   **Register:** `POST /user/register`
*   **Login:** `POST /user/login`
    *   Returns: `{ "token": "jwt_token", "user_id": 1 }`
*   **Profile:** `GET /user/profile`, `PUT /user/profile`
*   **Language:** `PUT /user/language`

### Diagnosis Endpoints
*   **Detect Disease:** `POST /diagnosis/detect`
    *   Body: `image` (file), `crop` (string)
    *   Response: JSON with disease name, confidence, and treatment.
*   **History:** `GET /diagnosis/history`
*   **Details:** `GET /diagnosis/<id>`

### Cost Endpoints
*   **Calculate:** `POST /cost/calculate`
    *   Body: `{ "diagnosis_id": 1, "land_area": 5 }`

### Chatbot Endpoints
*   **Message:** `POST /chatbot/message`
    *   Body: `{ "message": "How to treat blight?" }`

---

## 5. Database Schema

The system uses **SQLite**.

### Key Tables
*   **Users (`users`)**
    *   `id` (PK), `email`, `password_hash`, `name`, `farm_size`, `preferred_language`.
*   **Diseases (`diseases`)**
    *   `id` (PK), `name`, `crop_type`, `description`, `symptoms`, `treatment_chemical`, `treatment_organic`.
*   **History (`diagnosis_history`)**
    *   `id` (PK), `user_id` (FK), `disease_id` (FK), `image_path`, `confidence_score`, `timestamp`.
*   **Pesticides (`pesticides`)**
    *   `id` (PK), `disease_id` (FK), `name`, `dosage`, `cost_per_unit`.
*   **Chat Logs (`chat_logs`)**
    *   `id` (PK), `user_id` (FK), `message`, `response`, `timestamp`.

---

## 6. Coding Standards

### Python (Backend)
*   **Style:** Follow **PEP 8** guidelines.
*   **Naming:** `snake_case` for functions/variables, `PascalCase` for classes.
*   **Linting:** Use `pylint` or `flake8` to check for issues.
*   **Structure:** Keep routes, services, and models separated.

### TypeScript/React Native (Frontend)
*   **Style:** Follow standard React formatting (Prettier recommended).
*   **Naming:** `PascalCase` for components (`MyComponent.tsx`), `camelCase` for functions/variables.
*   **Typing:** Use strict **TypeScript** types/interfaces. Avoid `any` whenever possible.
*   **Component Structure:**
    *   Props interface defined at the top.
    *   Functional components with hooks.

---

## 7. Deployment Steps

### Backend
1.  **Environment:** Ensure `DEBUG=False` in `.env` for production.
2.  **Server:** Use a production WSGI server like **Gunicorn** or **Waitress**.
    ```bash
    # Example using Waitress
    pip install waitress
    waitress-serve --port=5000 app:app
    ```
3.  **Host:** Deploy to a VM (AWS EC2, DigitalOcean) or a PaaS (Render, Heroku).

### Frontend
1.  **Build Configuration:** Update `app.json` with correct bundle patterns and version.
2.  **Build for Android:**
    ```bash
    eas build --platform android
    ```
3.  **Build for iOS:**
    ```bash
    eas build --platform ios
    ```
4.  **Publish:** Submit the `.apk` or `.ipa` to the respective app stores or distribute via Expo.

---

## 8. Troubleshooting

### Common Issues
*   **"Network Request Failed" on Mobile:**
    *   **Fix:** Ensure the phone is on the **same Wi-Fi** as the backend. Update the `API_URL` in `frontend-mobile/services/api.ts` to your computer's local IP (e.g., `http://192.168.1.10:5000`). localhost won't work on a physical device.

*   **Database Errors / Missing Tables:**
    *   **Fix:** Delete `database/crop_diagnosis.db` and re-run `python seed_database.py` inside the `database/seed` folder.

*   **"Module not found" in Frontend:**
    *   **Fix:** Run `npm install` to ensure all dependencies are present. Try `npx expo start -c` to clear the cache.

*   **Model Loading Errors:**
    *   **Fix:** Ensure `.h5` model files exist in `backend/models/`. Confirm TensorFlow versions match requirements.
