@echo off
echo ========================================
echo AI CROP DIAGNOSIS - SETUP CHECK
echo ========================================
echo.

echo Checking Python...
python --version
echo.

echo Checking if TensorFlow is installed...
python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)" 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] TensorFlow not found!
    echo Installing TensorFlow... This may take 10-15 minutes.
    echo.
    pip install tensorflow==2.15.0
)

echo.
echo Checking other packages...
python -c "import flask; print('Flask: OK')" 2>nul || pip install flask flask-cors
python -c "import cv2; print('OpenCV: OK')" 2>nul || pip install opencv-python
python -c "import bcrypt; print('bcrypt: OK')" 2>nul || pip install bcrypt
python -c "import jwt; print('JWT: OK')" 2>nul || pip install PyJWT
python -c "from googletrans import Translator; print('Translator: OK')" 2>nul || pip install googletrans==4.0.0rc1
python -c "from gtts import gTTS; print('gTTS: OK')" 2>nul || pip install gTTS

echo.
echo ========================================
echo All packages installed!
echo ========================================
echo.
echo Starting server...
python app.py
