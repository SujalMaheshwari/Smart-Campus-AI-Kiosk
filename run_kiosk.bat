@echo off
cd /d "%~dp0"
title RGPV AI Kiosk Launcher

echo =================================================
echo      STARTING RGPV AI KIOSK SYSTEM...
echo =================================================

echo 1. Waking up AI Brain (Ollama)...
start "Ollama Server" cmd /k "ollama serve"

echo.
echo 2. Starting Backend Server (Python)...
cd backend
:: Activating Virtual Environment and starting Uvicorn
start "RGPV Backend" cmd /k "call venv\Scripts\activate && uvicorn main:app --reload"

echo.
echo 3. Launching Frontend Interface...
cd ..
cd frontend
start "RGPV Frontend" cmd /k "npm run dev"

echo.
echo =================================================
echo      SYSTEM IS READY! 
echo      Opening Browser in 5 seconds...
echo =================================================

:: 5 Second ka wait taaki server start ho sake
timeout /t 5 /nobreak >nul

:: Browser auto-open karega
start http://localhost:5173

:: Agar Kiosk Mode (Full Screen) chahiye toh upar wali line hata kar neeche wali use karna:
:: start chrome --kiosk "http://localhost:5173"

pause