@echo off
echo === Pulling latest code from GitHub ===
git pull

echo.
echo === Installing/Updating Python dependencies ===
pip install -r requirements.txt

echo.
echo === Starting backend API ===
start cmd /k "uvicorn api:app --reload"

echo.
echo === Starting frontend (index.html) ===
start "" "file:///C:/Users/epatn/Desktop/averis_repo/averisaxiom-agent/index.html"

echo.
echo === ALL SYSTEMS GO ===
pause
