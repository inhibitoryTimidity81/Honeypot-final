# Honeypot API - Start Server Script
# This script starts the Honeypot API server

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*69) -ForegroundColor Cyan
Write-Host "  HONEYPOT AGENT API - SERVER STARTUP" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*69) -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create it first with: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Make sure you have GEMINI_API_KEY configured" -ForegroundColor Yellow
}

Write-Host "🚀 Starting Honeypot API Server..." -ForegroundColor Green
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "  GET  http://localhost:8000/           - Health check" -ForegroundColor White
Write-Host "  POST http://localhost:8000/api/v1/chat - Chat endpoint" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*69) -ForegroundColor Cyan
Write-Host ""

# Start the server
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
