# Personal Finance Manager

A mobile-first PWA for managing personal finances, featuring PDF bank statement OCR, expense reconciliation, and missed payment tracking.

## Features

- **Bank Statement OCR**: Import PDF statements and automatically extract transactions.
- **Expense Reconciliation**: Match transactions to defined recurring expenses.
- **Missed Payment Alerts**: Automatic warnings for expected payments that haven't occurred.
- **PWA Support**: Installable on Android home screens.
- **Excel Export**: Export all your data to a spreadsheet.
- **Secure**: JWT-based authentication.

## Setup

### Prerequisites

- Python 3.12+
- Tesseract OCR: `sudo apt-get install tesseract-ocr`
- Poppler: `sudo apt-get install poppler-utils`

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the backend:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. Serve the frontend:
   You can use any static file server, for example:
   ```bash
   python3 -m http.server 3000 --directory frontend
   ```

## Usage

1. Open `http://localhost:3000` on your mobile browser.
2. Log in with `admin` / `password123`.
3. Add your bank accounts and cards.
4. Define your recurring expense types (e.g., Rent, Utilities).
5. Import your bank statement PDFs to reconcile transactions.
