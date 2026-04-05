@echo off
setlocal

:: Get the directory where the script is located
set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

echo --- Receipt Scanner: Starting Frontend ---

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install it from python.org.
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [ERROR] 'frontend' folder not found in %CD%. Please run this from the project root.
    pause
    exit /b 1
)

echo [SUCCESS] Frontend is starting at http://localhost:3000
echo.
cd frontend
python -m http.server 3000

pause
