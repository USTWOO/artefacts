# Receipt Scanner and Categorizer

A mobile-optimized Progressive Web App (PWA) that allows you to scan, OCR, and categorize receipts directly using your phone's camera.

## Features

- **Scan Receipts**: Use your device's camera for immediate receipt capture via the web interface.
- **Intelligent OCR**: Preprocesses images with OpenCV and performs OCR with Tesseract to extract text from receipts.
- **Automated Extraction**: Uses SpaCy Named Entity Recognition (NER) and regex to extract:
  - Vendor Name
  - Date
  - Subtotal and Total Amount
  - VAT (Tax)
- **Automatic Categorization**: Categorizes expenses (Food, Travel, Supplies, etc.) based on extracted keywords.
- **Confirmation Flow**: Presents extracted data in a form for user review and correction before saving.
- **Persistent Storage**: Saves confirmed data to a local SQLite database that persists even if the phone is turned off.
- **Excel Export**: Exports your receipt history to an Excel file for expense reporting.
- **PWA Support**: Can be "installed" to your Android home screen as a standalone application.

## Prerequisites

### System Dependencies

Before running the application, ensure you have the Tesseract OCR engine and necessary system libraries installed.

**On Ubuntu/Linux (and our sandbox):**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr libtesseract-dev libgl1
```

### Python Dependencies

The application requires Python 3.8+. It is **highly recommended** to use a virtual environment:

#### Windows (PowerShell)
```powershell
# Create virtual environment
python -m venv venv
# Activate it
.\venv\Scripts\Activate.ps1
# Install dependencies
pip install -r backend/requirements.txt
# Download NLP model
python -m spacy download en_core_web_sm
```

#### Ubuntu/Linux/macOS
```bash
# Create virtual environment
python3 -m venv venv
# Activate it
source venv/bin/activate
# Install dependencies
pip install -r backend/requirements.txt
# Download NLP model
python3 -m spacy download en_core_web_sm
```

## Running the Application

Ensure your virtual environment is **activated** before running these commands.

1. **Start the Backend Server**:
   From the project root directory:
   ```bash
   # Using python -m uvicorn ensures the command is found
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

2. **Serve the Frontend**:
   You can serve the `frontend/` directory using any web server. For example:
   ```bash
   cd frontend
   python3 -m http.server 3000
   ```

3. **Access on Mobile**:
   Navigate to `http://<your-ip-address>:3000` in your phone's browser. You can then use the "Add to Home Screen" feature to install it as a PWA.

## Running Locally on a Mobile Device (Android/Termux)

To run the *complete* app (backend + frontend) entirely on your Android phone without a PC:

1. **Install Termux**: Download and install the [Termux](https://termux.dev/) app.
2. **Setup the Environment**:
   Open Termux and run:
   ```bash
   pkg update && pkg upgrade
   pkg install python tesseract libjpeg-turbo libpng opencv
   ```
3. **Clone and Install**:
   ```bash
   # Clone your project or copy files to the phone
   pip install -r backend/requirements.txt
   python -m spacy download en_core_web_sm
   ```
4. **Run the Backend**:
   ```bash
   uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
   ```
5. **Run the Frontend**:
   ```bash
   cd frontend
   python3 -m http.server 3000
   ```
6. **Open in Browser**:
   Navigate to `http://localhost:3000` in Chrome on your phone. You can then "Install" it to your home screen.

## Architecture

- **Frontend**: Vanilla HTML/CSS/JS with a focus on responsive, mobile-first design.
- **Backend**: FastAPI (Python) for handling OCR, extraction logic, and database operations.
- **Database**: SQLite for local persistence.
- **OCR Engine**: Tesseract with OpenCV for image preprocessing.
- **Extraction & NLP**: SpaCy (`en_core_web_sm`) for entity recognition and regex for pattern matching.

## Testing

Run the included tests to ensure the extraction logic and API are working correctly:

```bash
export PYTHONPATH=$PYTHONPATH:.
pytest tests/
```
