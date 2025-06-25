@echo off
setlocal enabledelayedexpansion

:: Gå till repo mappen
cd /d %~dp0

:: Uppdatera repo
echo.
echo ================================
echo Uppdaterar repository...
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
echo Installerar dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Misslyckades installera dependencies!
    pause
    exit /b 1
)
echo ================================

:: Starta backend + frontend server
echo Startar server på http://localhost:8000 ...
start "AverisAxiom Server" cmd /k uvicorn api:app --reload

endlocal
