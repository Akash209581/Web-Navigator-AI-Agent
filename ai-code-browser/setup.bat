@echo off
title AI Code Browser Setup

echo 🚀 Setting up AI Code Browser...

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16 or higher.
    pause
    exit /b 1
)
echo ✅ Node.js found

npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm.
    pause
    exit /b 1
)
echo ✅ npm found

echo 📦 Setting up backend...
cd backend
call npm install
if not exist .env copy ..\.env.example .env
echo ⚠️  Please edit backend\.env and add your OpenAI API key
cd ..

echo 📦 Setting up frontend...
cd frontend
call npm install
cd ..

echo cd backend > start-backend.bat
echo npm run dev >> start-backend.bat

echo cd frontend > start-frontend.bat
echo npm run electron-dev >> start-frontend.bat

echo @echo off > start-all.bat
echo echo 🚀 Starting AI Code Browser... >> start-all.bat
echo cd backend ^&^& start /b npm run dev >> start-all.bat
echo timeout /t 5 /nobreak ^>nul >> start-all.bat
echo cd ..\frontend ^&^& npm run electron-dev >> start-all.bat

echo ✅ Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Edit backend\.env and add your OpenAI API key
echo 2. Run: start-all.bat
echo 3. The app will open as an Electron desktop application
pause
