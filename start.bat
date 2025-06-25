@echo off
setlocal enabledelayedexpansion

cd /d %~dp0

echo.
echo ================================
echo Updating repository...
git pull
git status
echo ================================

if not exist ".venv\" (
    echo Creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo Failed creating venv!
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate

echo.
echo ================================
echo Installing requirements...
pip install --upgrade pip
pip install -r requirements.txt
echo ================================

echo.
echo Starting backend server...
uvicorn api:app --reload

endlocal
