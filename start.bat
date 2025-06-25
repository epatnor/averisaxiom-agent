@echo off
setlocal enabledelayedexpansion

cd /d %~dp0

echo ============================
echo Updating repository...
git pull
git status
echo ============================

if not exist ".venv\" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate

echo Installing requirements...
pip install --upgrade pip
pip install -r requirements.txt

echo Starting backend server...
start "" uvicorn api:app --reload

echo Open http://localhost:8000/index.html in your browser!

endlocal
