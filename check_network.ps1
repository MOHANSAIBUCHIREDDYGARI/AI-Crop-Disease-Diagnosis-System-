# AI Crop Diagnosis - Network Diagnostic Script
# This script helps find why your phone can't talk to your PC's backend.

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   AI CROP DIAGNOSIS NETWORK DIAGNOSTIC" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Backend Server Status
Write-Host "[1/3] Checking if Backend is running..." -NoNewline
$connection = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }

if ($connection) {
    Write-Host " OK (Listening on port 5000)" -ForegroundColor Green
} else {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "      ERROR: The backend server is not running on port 5000."
    Write-Host "      ACTION: Run 'python backend/app.py' or 'start_server.bat' first."
}

# 2. Get IP Address
Write-Host "[2/3] Getting your local IP Address..." -NoNewline
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -match "Wi-Fi|Ethernet" -and $_.IPv4Address -notlike "169.*" }).IPv4Address[0]

if ($ip) {
    Write-Host " OK ($ip)" -ForegroundColor Green
    Write-Host "      Check: Is 'http://$ip:5000/api/' in your frontend/services/api.ts?"
} else {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "      ERROR: Could not find a valid Wi-Fi/Ethernet IP."
}

# 3. Check Firewall
Write-Host "[3/3] Checking Firewall for Port 5000..." -NoNewline
$rule = Get-NetFirewallRule -DisplayName "AI Crop Diagnosis API" -ErrorAction SilentlyContinue

if ($rule -and $rule.Enabled -eq 'True') {
    Write-Host " OK (Rule Exists)" -ForegroundColor Green
} else {
    Write-Host " MISSING/DISABLED" -ForegroundColor Yellow
    Write-Host "      ACTION: Creating firewall rule to allow port 5000..."
    
    # Try to create the rule (needs Admin)
    try {
        New-NetFirewallRule -DisplayName "AI Crop Diagnosis API" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -ErrorAction Stop
        Write-Host "      SUCCESS: Firewall rule created!" -ForegroundColor Green
    } catch {
        Write-Host "      FAILED: Could not create firewall rule automatically." -ForegroundColor Red
        Write-Host "      MANUAL ACTION: Please run this command in an ADMIN PowerShell:"
        Write-Host "      New-NetFirewallRule -DisplayName 'AI Crop Diagnosis API' -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "                  NEXT STEPS" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "1. Ensure your phone is on the same Wi-Fi as your PC."
Write-Host "2. Open http://$ip:5000/health in your PHONE'S browser."
Write-Host "3. If you can't see the health page on your phone, the app won't work."
Write-Host "4. If using Expo Tunnel, you might need a backend tunnel like ngrok."
Write-Host "===============================================" -ForegroundColor Cyan
