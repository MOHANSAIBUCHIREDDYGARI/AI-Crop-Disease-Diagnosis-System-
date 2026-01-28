# Test Disease Detection
Write-Host "Testing Disease Detection..." -ForegroundColor Cyan

# Login
$login = Invoke-RestMethod -Uri "http://localhost:5000/api/user/login" -Method Post -ContentType "application/json" -Body '{"email":"farmer@test.com","password":"test123"}'
$token = $login.token

Write-Host "Token received: $token" -ForegroundColor Green
Write-Host ""
Write-Host "Detecting disease... Please wait..." -ForegroundColor Yellow
Write-Host ""

# Detect disease using curl.exe
$result = curl.exe -X POST "http://localhost:5000/api/diagnosis/detect" -H "Authorization: Bearer $token" -F "image=@sample.JPG" -F "crop=tomato"

Write-Host "Result:" -ForegroundColor Green
Write-Host $result
