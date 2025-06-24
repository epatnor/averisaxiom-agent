@echo off
setlocal enabledelayedexpansion

:: Gå till repo-foldern (oavsett varifrån bat-filen körs)
cd /d %~dp0

:: Uppdatera repository
echo.
echo ================================
echo Updating repository...
git pull
git status
echo ================================

:: Kontrollera om venv finns
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

:: Installera requirements
echo.
echo ================================
echo Installing/updating Python packages...
pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install requirements!
    pause
    exit /b 1
)
echo ================================

:: Starta backend server i nytt fönster
echo Starting backend server...
start "Backend Server" cmd /k ".venv\Scripts\activate && uvicorn api:app --reload --log-level debug"

:: Öppna frontend (index.html i frontend-mappen)
echo Opening frontend in browser...
start "" "%cd%\frontend\index.html"

endlocal
