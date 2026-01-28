@echo off
echo ========================================
echo AI CROP DIAGNOSIS - QUICK START
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo.

echo [2/4] Installing dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [3/4] Initializing database...
cd ..\database\seed
python seed_database.py
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)
cd ..\..\backend
echo.

echo [4/4] Starting server...
echo.
echo ========================================
echo Server will start at http://localhost:5000
echo Press Ctrl+C to stop the server
echo ========================================
echo.
python app.py
