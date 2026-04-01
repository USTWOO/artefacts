@echo off
setlocal

echo --- Receipt Scanner: Starting Backend ---

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install it from python.org.
    pause
    exit /b 1
)

:: Create Venv if not exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate Venv
echo Activating virtual environment...
call venv\Scripts\activate

:: Install Dependencies
echo Checking/Installing dependencies (this may take a minute)...
pip install -r backend/requirements.txt --quiet

:: Download NLP Model
echo Checking NLP model...
python -m spacy download en_core_web_sm --quiet

:: Start Backend
echo.
echo [SUCCESS] Backend is starting at http://localhost:8000
echo.
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

pause
