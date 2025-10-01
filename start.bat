@echo off
setlocal enabledelayedexpansion

echo ==================================
echo LMS Activity Monitor - Quick Start
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3 is not installed. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

echo [OK] Python 3 found

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found. Creating from template...
    copy .env.example .env
    echo [OK] Created .env file. Please edit it with your credentials.
    echo.
    set /p response="Edit .env now? (y/n): "
    if /i "!response!"=="y" (
        notepad .env
    ) else (
        echo Please edit .env before continuing.
        pause
        exit /b 0
    )
)

echo.
echo [INFO] Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [OK] Dependencies installed successfully!
echo.
echo What would you like to do?
echo 1) Run a test scan (with browser visible)
echo 2) Run a headless scan
echo 3) Send test email
echo 4) Start web dashboard
echo 5) Exit
echo.

set /p choice="Enter choice [1-5]: "

if "%choice%"=="1" (
    echo Running test scan with visible browser...
    python scraper.py --headless False
) else if "%choice%"=="2" (
    echo Running headless scan...
    python scraper.py
) else if "%choice%"=="3" (
    echo Sending test email...
    python scraper.py --test-email
) else if "%choice%"=="4" (
    echo Starting web dashboard...
    echo Open http://localhost:5000 in your browser
    python app.py
) else if "%choice%"=="5" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice
    pause
    exit /b 1
)

pause
