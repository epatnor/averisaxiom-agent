@echo off
setlocal enabledelayedexpansion

:: Gå till repo-mappen
cd /d %~dp0

:: Uppdatera repo
echo.
echo ================================
echo Uppdaterar repository...
git pull
git status
echo ================================

:: Kontrollera om venv finns
if not exist ".venv\" (
    echo Skapar virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo Misslyckades skapa virtual environment!
        pause
        exit /b 1
    )
    echo Virtual environment skapad.
)

:: Aktivera venv
call .venv\Scripts\activate

:: Installera requirements
echo.
echo ================================
echo Installerar requirements...
pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Misslyckades installera requirements!
    pause
    exit /b 1
)
echo ================================

:: Starta backend i ny konsol
echo Startar backend-server...
start "Backend Server" cmd /k uvicorn api:app --reload --log-level debug

:: Vänta kort så servern startar upp (annars hinner browser öppna för snabbt)
timeout /t 2 >nul

:: Öppna frontend i browser
echo Öppnar frontend...
start "" http://127.0.0.1:8000/

endlocal
