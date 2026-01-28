# Test Disease Detection WITHOUT Login (Anonymous)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Anonymous Disease Detection" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Detecting disease WITHOUT login..." -ForegroundColor Yellow
Write-Host "This will work but history won't be saved" -ForegroundColor Gray
Write-Host ""

# Detect disease without authentication
$result = curl.exe -X POST "http://localhost:5000/api/diagnosis/detect" -F "image=@sample.JPG" -F "crop=tomato"

Write-Host "Result:" -ForegroundColor Green
Write-Host $result
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Anonymous detection successful!" -ForegroundColor Green
Write-Host "Note: History was NOT saved (no login)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
