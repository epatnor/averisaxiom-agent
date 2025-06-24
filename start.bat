@echo off
setlocal enabledelayedexpansion

:: Gå till rätt mapp
cd /d %~dp0

:: Uppdatera repo
echo ================================
echo Updating repository...
git pull
git status
echo ================================

:: Kontrollera venv
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

:: Aktivera venv
call .venv\Scripts\activate

:: Installera krav
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

:: Starta backend
echo Starting backend server...
start "Backend Server" cmd /k uvicorn api:app --reload --log-level debug

:: Öppna frontend i webbläsare
echo Opening frontend...
start "" http://localhost:8000/

endlocal
