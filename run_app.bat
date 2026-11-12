@echo off
echo ========================================================
echo   Launching Standalone AI Resume Parser Application
echo ========================================================
echo Starting Backend (FastAPI on http://127.0.0.1:8000)...
start "AI Resume Parser - Backend" cmd /k "cd /d %~dp0backend && call .\venv\Scripts\activate && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo Waiting 3 seconds for backend initialization...
timeout /t 3 /nobreak > nul

echo Starting Frontend (Vite on http://localhost:5173)...
start "AI Resume Parser - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Application launched!
echo Backend Swagger API: http://127.0.0.1:8000/docs
echo Frontend Dashboard:  http://localhost:5173
echo.
pause

