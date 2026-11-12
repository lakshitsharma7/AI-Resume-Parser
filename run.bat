@echo off
title AI Resume Parser - Launcher
color 0A
cls

echo ================================================================
echo               AI RESUME PARSER - 1-CLICK LAUNCHER
echo ================================================================
echo.
echo [1/3] Starting Backend (FastAPI on http://127.0.0.1:8000)...
start "AI Resume Parser - Backend" cmd /k "cd /d "%~dp0backend" && call .\venv\Scripts\activate && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/3] Waiting for Backend to initialize...
timeout /t 3 /nobreak > nul

echo [3/3] Starting Frontend (React + Vite on http://localhost:5173)...
start "AI Resume Parser - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

timeout /t 2 /nobreak > nul

echo.
echo Opening Dashboard in your default browser...
start http://localhost:5173

echo.
echo ================================================================
echo                    APPLICATION IS RUNNING!
echo ================================================================
echo  * Frontend Dashboard : http://localhost:5173
echo  * Backend API Docs   : http://127.0.0.1:8000/docs
echo  * Health Endpoint    : http://127.0.0.1:8000/api/v1/health
echo ================================================================
echo.
echo Note: Don't close the Backend and Frontend command windows.
pause

