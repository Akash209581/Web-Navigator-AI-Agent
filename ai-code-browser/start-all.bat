@echo off
echo 🚀 Starting AI Code Browser...
cd backend && start /b npm run dev
timeout /t 5 /nobreak >nul
cd ..\frontend && npm run electron-dev