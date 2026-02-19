AI Crop Diagnosis System
========================

Table of Contents
-----------------

*   [Intro](#intro)
*   [About](#about)
*   [Installing and Updating](#installing-and-updating)
    *   [Backend Setup](#backend-setup)
    *   [Frontend Setup](#frontend-setup)
*   [Usage](#usage)
    *   [Running Backend](#running-backend)
    *   [Running Frontend](#running-frontend)
    *   [Example Diagnosis](#example-diagnosis)
*   [Running Tests](#running-tests)
*   [Supported Crops & Diseases](#supported-crops--diseases)
*   [Troubleshooting](#troubleshooting)
*   [Contributing](#contributing)
*   [License](#license)

Intro
-----

**AI Crop Diagnosis System** allows farmers to quickly detect diseases in crops like Grape, Maize, Potato, Rice, and Tomato using deep learning models via a mobile app and web API.

Example:

    $ curl -X POST "http://localhost:5000/api/diagnosis/detect" \
        -F "image=@sample.JPG" \
        -F "crop=tomato"

    {
      "disease": "Tomato_Early_Blight",
      "confidence": 98.5,
      "treatment": "Use Copper Fungicide..."
    }

Simple as that!

About
-----

This project is a comprehensive, farmer-friendly mobile and web application for crop disease detection, diagnosis, and treatment recommendations with multilingual support. It leverages TensorFlow/Keras for high-accuracy disease identification and provides actionable advice, including organic alternatives and prevention tips.

Key features include:

*   **Real-time Detection**: powered by deep learning models.
*   **Multilingual Support**: English, Hindi, Telugu, Tamil, Kannada, Marathi.
*   **Treatment Recommendations**: Pesticide & Organic options.
*   **Chatbot Assistant**: AI-powered (Gemini) farming queries.
*   **Offline Capability**: Essential features work without internet.

The system is built using:

*   **Frontend**: React Native (Expo) & TypeScript.
*   **Backend**: Python (Flask), SQLite, TensorFlow/Keras.
*   **AI Services**: Google Gemini, Google Translate.

Installing and Updating
-----------------------

To install or update the AI Crop Diagnosis System, you need to set up both the backend and frontend components.

### Backend Setup

Navigate to the `backend` directory and install dependencies:

    cd backend
    python -m venv venv
    # Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
    pip install -r requirements.txt

**Configuration**:

Create a `.env` file in `backend/` and add your API keys (optional for core features):

    GOOGLE_GEMINI_API_KEY=your_key
    WEATHER_API_KEY=your_key
    SECRET_KEY=dev_secret

**Initialize Database**:

    cd ../database/seed
    python seed_database.py
    cd ../../backend

### Frontend Setup

Open a new terminal and navigate to `frontend-mobile`:

    cd frontend-mobile
    npm install

Usage
-----

### Running Backend

To start the backend server:

    cd backend
    python app.py
    # Server starts at http://localhost:5000

### Running Frontend

To start the mobile application:

    cd frontend-mobile
    npx expo start

*   Scan the QR code with the **Expo Go** app on your Android/iOS device.
*   Or press `a` to run on Android Emulator, `w` for Web.

### Example Diagnosis

You can test the diagnosis API directly using `curl` or Postman.

    $ curl -X POST "http://localhost:5000/api/diagnosis/detect" \
        -F "image=@sample.JPG" \
        -F "crop=potato"

Running Tests
-------------

Tests are available to verify the system functionality.

You can run the provided PowerShell script to test disease detection:

    ./test_detection.ps1

This script logs in a test user, uploads a sample image, and retrieves the diagnosis result.

For unit tests:

    # Backend
    pytest

    # Frontend
    npm test

Supported Crops & Diseases
--------------------------

| Crop | Detectable Conditions |
| :--- | :--- |
| **Grape** | Black Rot, ESCA, Leaf Blight, Healthy |
| **Maize** | Blight, Common Rust, Gray Leaf Spot, Healthy |
| **Potato** | Early Blight, Late Blight, Healthy |
| **Rice** | Bacterial Leaf Blight, Brown Spot, Leaf Smut, Healthy |
| **Tomato** | Bacterial Spot, Early/Late Blight, Leaf Mold, Septoria, Spider Mites, Target Spot, Mosaic Virus, Yellow Leaf Curl Virus, Healthy |

Troubleshooting
---------------

If you get "Network Error" on the App, ensure your phone and computer are on the **same Wi-Fi**. Update the `API_URL` in `frontend-mobile/services/api.ts` to your computer's local IP (e.g., `http://192.168.1.5:5000`).

If the server won't start, check if port 5000 is free or change `PORT` in `.env`.

If you encounter database errors, delete `database/crop_diagnosis.db` and re-run `python seed_database.py`.

Contributing
------------

1.  Fork the repository
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

License
-------

[MIT License](LICENSE) (Assuming MIT, update if different)
