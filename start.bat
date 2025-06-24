@echo off
setlocal

:: Gå till repo-mappen
cd /d %~dp0

:: Visa repo status
echo ================================
echo Updating repository...
git pull
git status
echo ================================

:: Kolla om venv finns
if exist ".venv\Scripts\activate" (
    echo Activating virtual environment...
    call .venv\Scripts\activate
) else (
    echo WARNING: Ingen venv hittades. Kör pip install först!
)

:: Kör uvicorn med mer loggning
echo Starting backend server...
uvicorn api:app --reload --log-level debug

:: Öppna browsern (om frontend ligger lokalt)
start "" http://localhost:8000

pause
endlocal
