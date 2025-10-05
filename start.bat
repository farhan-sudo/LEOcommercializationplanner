@echo off
echo ========================================
echo   Satellite Tracking System Launcher
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
echo.
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
    echo Dependencies installed successfully!
) else (
    echo Dependencies already installed.
)

echo.
echo ========================================
echo   Starting Flask Application...
echo ========================================
echo.
echo Access the application at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Start Flask app
python app.py

pause
