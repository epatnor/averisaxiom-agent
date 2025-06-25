@echo off
setlocal enabledelayedexpansion

:: Gå till repo-mappen
cd /d %~dp0

:: Uppdatera repo
git pull

:: Skapa venv om den inte finns
if not exist ".venv\" (
    python -m venv .venv
)

:: Aktivera venv
call .venv\Scripts\activate

:: Installera requirements
pip install --upgrade pip
pip install -r requirements.txt

:: Starta server
echo Starting backend...
uvicorn api:app --reload --host 127.0.0.1 --port 8000

endlocal
