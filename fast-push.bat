@echo off

:: Generate a timestamp for the commit message
for /f "tokens=1-4 delims=/:. " %%a in ("%date% %time%") do (
    set TIMESTAMP=%%a-%%b-%%c_%%d-%%e-%%f
)

:: Git commands
git add .
git commit -m "Auto commit - %TIMESTAMP%"
git push

echo ✅ All files pushed with commit timestamp '%TIMESTAMP%'