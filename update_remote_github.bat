@echo off
setlocal

echo ====================================
echo Synkar lokala ändringar till GitHub
echo ====================================

:: Add all changes
git add -A

:: Commit med automatiskt meddelande
git commit -m "Sync local changes to GitHub"

:: Pull för säkerhets skull innan push (hanterar ev. remote ändringar)
git pull --rebase

:: Push till remote
git push

echo ====================================
echo Klar! GitHub är nu uppdaterat.
echo ====================================

pause
endlocal
