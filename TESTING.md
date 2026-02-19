# AI Crop Diagnosis System Testing Documentation

## Testing Overview
Testing is a critical phase in the development of the AI Crop Diagnosis System to ensure accuracy, reliability, and usability for farmers and agricultural experts. The system functions as a bridge between complex AI analysis and practical field application. Testing verifies that the mobile application correctly captures images, communicates with the backend, processes disease diagnosis accurately, and provides actionable advice. It encompasses unit testing of individual components, integration testing of the API and database layers, and full system testing of the user workflows.

---

## Technologies and Languages Used

### Frontend Technologies (Mobile App)
- **React Native (Expo)** – Framework for building the cross-platform mobile application.
- **TypeScript** – Used for type-safe development and improved code quality.
- **React Navigation** – Handles routing and navigation between screens (Home, Camera, Results, Chat).
- **Axios** – Manages HTTP requests to the backend API.
- **Expo Camera** – Interface for capturing crop images directly within the app.
- **Expo File System** – Handles image storage and upload preparation.

### Backend Technologies (API & Logic)
- **Python** – The primary programming language for the backend logic and AI processing.
- **Flask** – Lightweight web framework for serving API endpoints.
- **TensorFlow / Keras** – Used for loading and running the deep learning models for disease classification.
- **OpenCV (cv2)** – Image processing library used for preprocessing uploaded images before analysis.
- **Google Generative AI (Gemini)** – Powers the chatbot and advanced advisory features.
- **GoogleTrans** – Provides translation services for multi-language support.

### Database & Storage
- **SQLite** – Lightweight, serverless database for storing disease info, pesticide data, and chat history.
- **JSON** – Used for configuration and seeding initial data.

---

## Testing Tools Used

### Unit & Integration Testing Tools
- **Jest** – JavaScript testing framework used for testing React Native components and logic.
- **Pytest** – Python testing framework used for testing backend functions, API routes, and database interactions.
- **Postman** – Used for manual and automated testing of API endpoints (`/diagnose`, `/chat`, `/cost`).

### System & Manual Testing Tools
- **Expo Go** – Used for real-time testing on physical Android and iOS devices.
- **Android Emulator / iOS Simulator** – Used for testing UI responsiveness and layout across different screen sizes.
- **DB Browser for SQLite** – Used to verify database integrity and check if data (e.g., chat logs, new diseases) is correctly stored.
- **Browser Developer Tools** – Used for debugging network requests when running the app in web mode.

---

## Unit Testing

### Frontend Unit Testing (Jest)
Focused on verifying that individual UI components and utility functions work as expected.
- **Components Checked**: Setup of `AuthContext` (though not fully implemented with backend yet), rendering of `ExploreScreen`, `Camera` permissions logic.
- **Utilities**: Date formatting, string manipulation helpers.

### Backend Unit Testing (Pytest)
Focused on ensuring the core logic of the API works in isolation.
- **Image Processing**: Verifying that images are correctly resized and normalized for the model.
- **Database Queries**: Testing `check_disease` and pesticide lookup functions to ensure accurate data retrieval.
- **Route Handlers**: ensuring routes like `/api/health` return 200 OK.

---

## Integration Testing

Integration testing validates communication between the mobile frontend, the Flask backend, and the SQLite database.

### API Integration (Postman & Manual)
- **Diagnosis Flow**:
  - Request: POST image to `/diagnose`
  - Verification: Backend receives image -> Preprocesses -> Model predicts -> Returns JSON with disease name, confidence, and treatment.
- **Chatbot Flow**:
  - Request: POST text to `/chat`
  - Verification: Backend routes query to Gemini/Rule-based logic -> Returns context-aware response.
- **Database Integration**:
  - Verified that requesting a diagnosis triggers a lookup in the `pesticides` table for relevant treatments.

### Frontend-Backend Integration
- Verified that the mobile app correctly handles network errors (e.g., "Server Offline").
- Tested loading states while waiting for the diagnosis response.
- Validated that the backend response (JSON) is correctly parsed and displayed in the frontend UI (e.g., Disease Name, Confidence Bar).

---

## System Testing

System testing validates the complete end-to-end functionality of the AI Crop Diagnosis application.

### Test Scenarios
1.  **Image Diagnosis Workflow**:
    - User opens Camera -> Captures Photo -> Confirms Upload -> View Results.
    - **Success Criteria**: Correct disease identified, treatment shown, high confidence score.
2.  **Gallery Upload Workflow**:
    - User selects image from Gallery -> Uploads -> View Results.
    - **Success Criteria**: Image correctly processed similarly to camera capture.
3.  **Chatbot Assistance**:
    - User asks "How to treat potato blight?" -> Chatbot responds with accurate info from the database/AI.
4.  **Language Translation**:
    - User changes language to Hindi -> App interface and diagnosis results update to Hindi.
    - **Success Criteria**: Accurate translation via `googletrans`.

---

## Performance and Usability Testing

### Performance Testing
- **Inference Speed**: Monitored time taken from "Upload" to "Result". Average response time goal: < 3 seconds.
- **App Startup**: Measured time for app to load and fetch initial data.
- **Memory Usage**: Monitored app stability during repeated camera usage to prevent crashes.

### Usability Testing
- **UI Responsiveness**: Tested scrolling smoothness in "Explore" tab and "Chat" interface.
- **Error Handling**: Checked user feedback when camera permissions are denied or internet is unavailable.
- **Visual Clarity**: Ensured text is readable and buttons are accessible on smaller screens.

---

## Conclusion
The testing process for the AI Crop Diagnosis System has covered critical paths from image capture to disease diagnosis. By utilizing a combination of automated unit tests (Jest, Pytest) and manual system testing (Expo Go, Postman), foundational issues were identified and resolved. The integration of SQLite and Flask has been verified for data consistency. Continued testing will focus on expanding the dataset for higher model accuracy and refining the offline capabilities of the mobile application.
