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

The application requires Python 3.8+. Install the required Python packages:

```bash
pip install -r backend/requirements.txt
python -m spacy download en_core_web_sm
```

## Running the Application

1. **Start the Backend Server**:
   From the project root directory:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

2. **Serve the Frontend**:
   You can serve the `frontend/` directory using any web server. For example:
   ```bash
   cd frontend
   python3 -m http.server 3000
   ```

3. **Access on Mobile**:
   Navigate to `http://<your-ip-address>:3000` in your phone's browser. You can then use the "Add to Home Screen" feature to install it as a PWA.

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
