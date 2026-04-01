@echo off
setlocal

echo --- Receipt Scanner: Starting Frontend ---

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install it from python.org.
    pause
    exit /b 1
)

echo [SUCCESS] Frontend is starting at http://localhost:3000
echo.
cd frontend
python -m http.server 3000

pause
