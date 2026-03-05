@echo off
REM AI Hide and Seek - Start Script for Windows
REM This script starts both backend and frontend servers

echo 🎮 Starting AI Hide and Seek Game...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16 or higher.
    pause
    exit /b 1
)

echo ✓ Python found
echo ✓ Node found
echo.

REM Start backend
echo 🚀 Starting backend server...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat

if not exist "venv\installed" (
    echo Installing backend dependencies...
    pip install -r requirements.txt
    echo. > venv\installed
)

REM Start backend in new window
start "AI Hide and Seek - Backend" cmd /k "venv\Scripts\activate.bat && python main.py"
echo ✓ Backend started
cd ..

REM Wait for backend to initialize
echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

REM Start frontend
echo 🎨 Starting frontend server...
cd frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

REM Start frontend in new window
start "AI Hide and Seek - Frontend" cmd /k "npm start"
echo ✓ Frontend started

echo.
echo ✅ Game is starting!
echo.
echo 📊 Backend API: http://localhost:8000
echo 🎮 Game UI: http://localhost:3000
echo.
echo Close the terminal windows to stop the servers
echo.
pause
