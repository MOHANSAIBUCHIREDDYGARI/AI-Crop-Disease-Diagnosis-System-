@echo off
echo ========================================
echo Testing AI Crop Diagnosis API
echo ========================================
echo.

echo Step 1: Registering user...
curl -X POST http://localhost:5000/api/user/register -H "Content-Type: application/json" -d "{\"email\":\"farmer@test.com\",\"password\":\"test123\",\"name\":\"Test Farmer\",\"farm_size\":5}"
echo.
echo.

echo Step 2: Logging in...
echo Please copy the TOKEN from the response above!
curl -X POST http://localhost:5000/api/user/login -H "Content-Type: application/json" -d "{\"email\":\"farmer@test.com\",\"password\":\"test123\"}"
echo.
echo.

echo ========================================
echo COPY THE TOKEN FROM ABOVE
echo ========================================
echo.
echo To test disease detection, run this command:
echo (Replace YOUR_TOKEN_HERE with the actual token)
echo.
echo curl -X POST http://localhost:5000/api/diagnosis/detect -H "Authorization: Bearer YOUR_TOKEN_HERE" -F "image=@sample.JPG" -F "crop=tomato"
echo.
pause
