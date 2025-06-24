@echo off
setlocal enabledelayedexpansion

:: Go to repo folder
cd /d %~dp0

:: Update repository
echo.
echo ================================
echo Updating repository...
git pull
git status
echo ================================

:: Check for venv
if not exist ".venv\" (
    echo Creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo Virtual environment created.
)

:: Activate venv
call .venv\Scripts\activate

:: Install requirements
echo.
echo ================================
echo Installing requirements...
pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install requirements!
    pause
    exit /b 1
)
echo ================================

:: Start backend server in new window
echo Starting backend server...
start "Backend Server" cmd /k uvicorn api:app --reload --log-level debug

:: Open frontend
echo Opening frontend...
start "" http://localhost:8000

endlocal
