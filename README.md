# 🚀 Receipt Scanner (Mobile-First PWA)

A complete mobile application for scanning, OCR, and categorizing receipts. Designed to run as an app on your Android phone without needing to manually generate an APK.

---

## ⚡ 3-Step Quick Start (Windows)

1.  **Download and Install Python** from [python.org](https://www.python.org/downloads/) (if you don't have it).
2.  **Double-click `run_backend.bat`** (this installs everything and starts the server).
3.  **Double-click `run_frontend.bat`** (this starts the mobile-friendly web view).

---

## 📱 How to get it on your Phone (No APK needed!)

This application is a **Progressive Web App (PWA)**, which is the modern alternative to an APK. You can "Install" it to your phone's home screen as a standalone app:

1.  **Run the scripts** (Steps 2 and 3 above) on your PC.
2.  **Connect your phone** to the same Wi-Fi as your PC.
3.  **Find your PC's IP address** (open CMD, type `ipconfig`, look for "IPv4 Address").
4.  **Open Chrome on your Phone** and go to `http://<your-pc-ip>:3000`.
5.  **Install as App**: Tap the **⋮** menu in Chrome (top right) and select **"Add to Home screen"** or **"Install app"**.

**Your app is now on your home screen, ready to use!**

---

## 🛠️ Complete Local Install (Android / Termux)

If you want to run the *entire* app (server + web view) **only** on your phone without a computer:

1.  **Install Termux** from [F-Droid](https://f-droid.org/en/packages/com.termux/).
2.  **Copy-paste these commands** into Termux:
    ```bash
    pkg update && pkg upgrade
    pkg install python tesseract-ocr libjpeg-turbo libpng opencv
    pip install -r backend/requirements.txt
    python -m spacy download en_core_web_sm
    ```
3.  **Run the app**:
    -   Type `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &`
    -   Type `cd frontend && python -m http.server 3000`
4.  **Open Chrome** on your phone and go to `http://localhost:3000`.

---

## 🏗️ Architecture & Features

- **OCR & Extraction**: Scans Vendor, Date, Subtotal, VAT, and Total.
- **Persistence**: Uses a persistent SQLite database (retained even when power is off).
- **Categories**: Automatically categorizes (Fuel, Entertainment, etc.).
- **Analytical Views**: See monthly and category-based expense summaries.
- **Export**: Export all data to Excel.
- **Responsive**: Optimized for mobile use.

---

## 🧪 Testing

To run the internal verification tests:
```bash
python -m pytest tests/
```
