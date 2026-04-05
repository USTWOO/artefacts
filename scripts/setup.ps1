Write-Host "--- Receipt Scanner Setup (Windows) ---" -ForegroundColor Cyan

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

Write-Host "Activating virtual environment..."
. venv\Scripts\Activate.ps1

Write-Host "Installing backend dependencies..."
pip install -r backend/requirements.txt

Write-Host "Downloading NLP model..."
python -m spacy download en_core_web_sm

Write-Host "`nSetup Complete! To start the app, run:" -ForegroundColor Green
Write-Host ".\venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
