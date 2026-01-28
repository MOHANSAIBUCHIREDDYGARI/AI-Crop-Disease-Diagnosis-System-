# AI Crop Diagnosis - Test Disease Detection
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Disease Detection API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Login to get token
Write-Host "Step 1: Logging in..." -ForegroundColor Yellow
$loginResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/user/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{"email":"farmer@test.com","password":"test123"}'

$token = $loginResponse.token
Write-Host "✓ Login successful!" -ForegroundColor Green
Write-Host "Token: $token" -ForegroundColor Gray
Write-Host ""

# Step 2: Detect disease
Write-Host "Step 2: Detecting disease from sample.JPG..." -ForegroundColor Yellow
Write-Host "This may take a few seconds..." -ForegroundColor Gray
Write-Host ""

# Use curl.exe (real curl, not PowerShell alias)
$result = curl.exe -X POST "http://localhost:5000/api/diagnosis/detect" `
    -H "Authorization: Bearer $token" `
    -F "image=@sample.JPG" `
    -F "crop=tomato"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESULT:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host $result
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Test completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
