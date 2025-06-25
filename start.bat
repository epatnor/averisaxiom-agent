@echo off
setlocal enabledelayedexpansion

:: Gå till repo-mappen
cd /d %~dp0

:: Uppdatera repo
echo.
echo ================================
echo Updating repository...
git pull
git status
echo ================================

:: Kontrollera venv
if not exist ".venv\" (
    echo Skapar virtuell miljö...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo Misslyckades skapa venv!
        pause
        exit /b 1
    )
    echo Virtuell miljö skapad.
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

:: Starta backend i nytt fönster
echo Startar backend server...
start "Backend Server" cmd /k uvicorn api:app --host 127.0.0.1 --port 8000 --reload

:: Starta frontend i nytt fönster
echo Startar frontend server...
start "Frontend Server" cmd /k python -m http.server 8080

echo.
echo Frontend: http://127.0.0.1:8080/index.html
echo Backend API: http://127.0.0.1:8000

endlocal
