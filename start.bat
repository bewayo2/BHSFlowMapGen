@echo off
echo Starting Process Map Generator...
echo.

echo Starting the Flask server...
start "Process Map Generator" cmd /k "python app.py"

echo.
echo Application is starting...
echo Server will be available at: http://localhost:5000
echo.
echo Press any key to close this window...
pause >nul 