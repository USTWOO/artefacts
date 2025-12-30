import os
import shutil
import uuid
import re
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
import pytesseract
import pandas as pd
from PIL import Image
from datetime import datetime
import io
import spacy

from . import models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Load spacy model
nlp = spacy.load('en_core_web_sm')

# Mount the frontend directory as a static path
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def preprocess_image(image_path):
    """
    Loads an image and applies advanced preprocessing steps to improve OCR accuracy.
    """
    img = cv2.imread(image_path)
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply thresholding to binarize the image
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    # Denoise the image
    denoised = cv2.fastNlMeansDenoising(binary, h=10, searchWindowSize=21, templateWindowSize=7)
    return denoised

def parse_receipt(ocr_text):
    """
    Parses the OCR output using spaCy for NER.
    """
    vendor = "Unknown"
    date = datetime.now().date()
    amount = 0.0
    vat = 0.0
    total_amount = 0.0

    doc = nlp(ocr_text)

    # Find vendor (ORG entity)
    for ent in doc.ents:
        if ent.label_ == 'ORG':
            vendor = ent.text
            break
    if vendor == "Unknown" and ocr_text:
        vendor = ocr_text.split('\n')[0] # Fallback to first line

    # Find date (DATE entity)
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            try:
                date = pd.to_datetime(ent.text).date()
                break
            except (ValueError, pd.errors.ParserError):
                continue

    # Find amounts (MONEY entity) and identify total
    money_entities = [float(re.sub(r'[^\d.]', '', ent.text)) for ent in doc.ents if ent.label_ == 'MONEY']
    if money_entities:
        total_amount = max(money_entities)

    amount = total_amount
    vat = 0.0 # Placeholder for now

    return {
        "vendor": vendor,
        "date": date,
        "amount": amount,
        "vat": vat,
        "total_amount": total_amount
    }

@app.post("/upload/")
async def upload_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        preprocessed_image = preprocess_image(file_path)
        ocr_text = pytesseract.image_to_string(preprocessed_image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {e}")

    receipt_data = parse_receipt(ocr_text)

    db_receipt = models.Receipt(**receipt_data)
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)

    return {"filename": file.filename, "receipt_data": receipt_data, "receipt_id": db_receipt.id}

@app.get("/receipts/")
def read_receipts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    receipts = db.query(models.Receipt).offset(skip).limit(limit).all()
    return receipts

@app.get("/export/")
def export_receipts(db: Session = Depends(get_db)):
    receipts = db.query(models.Receipt).all()
    if not receipts:
        raise HTTPException(status_code=404, detail="No receipts to export")

    receipts_data = [
        {
            "Date": r.date,
            "Vendor": r.vendor,
            "Amount": r.amount,
            "TAX": r.vat,
            "Total amount": r.total_amount,
        }
        for r in receipts
    ]

    df = pd.DataFrame(receipts_data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Receipts')

    return StreamingResponse(
        io.BytesIO(output.getvalue()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=receipts.xlsx"}
    )

@app.get("/")
def read_root():
    return FileResponse('frontend/index.html')
