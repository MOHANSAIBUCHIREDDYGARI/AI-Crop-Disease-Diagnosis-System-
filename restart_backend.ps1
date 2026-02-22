# Quick Backend Restart Script
# This restarts the backend server to load the latest code changes

Write-Host "Stopping backend server..." -ForegroundColor Yellow
# The server should be stopped manually with Ctrl+C

Write-Host "`nStarting backend server..." -ForegroundColor Green
cd backend
python app.py
