import os
import shutil
import uuid
import re
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
import pytesseract
import pandas as pd
from PIL import Image
from datetime import datetime, date
import io
import spacy
from pydantic import BaseModel

from . import models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Pydantic model for saving receipt
class ReceiptCreate(BaseModel):
    vendor: str
    date: date
    amount: float
    vat: float
    total_amount: float

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
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    denoised = cv2.fastNlMeansDenoising(binary, h=10, searchWindowSize=21, templateWindowSize=7)
    return denoised

def parse_receipt(ocr_text):
    """
    Parses the OCR output using spaCy for NER.
    """
    vendor = "Unknown"
    date_str = datetime.now().strftime('%Y-%m-%d')
    amount = 0.0
    vat = 0.0
    total_amount = 0.0

    doc = nlp(ocr_text)

    for ent in doc.ents:
        if ent.label_ == 'ORG':
            vendor = ent.text
            break
    if vendor == "Unknown" and ocr_text:
        vendor = ocr_text.split('\n')[0]

    for ent in doc.ents:
        if ent.label_ == 'DATE':
            try:
                date_str = pd.to_datetime(ent.text).strftime('%Y-%m-%d')
                break
            except (ValueError, pd.errors.ParserError):
                continue

    money_entities = [float(re.sub(r'[^\d.]', '', ent.text)) for ent in doc.ents if ent.label_ == 'MONEY']
    if money_entities:
        total_amount = max(money_entities)

    amount = total_amount
    vat = 0.0

    return {
        "vendor": vendor,
        "date": date_str,
        "amount": amount,
        "vat": vat,
        "total_amount": total_amount
    }

@app.post("/upload/")
async def upload_receipt(file: UploadFile = File(...)):
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

    return JSONResponse(content=receipt_data)

@app.post("/save/")
async def save_receipt(receipt: ReceiptCreate, db: Session = Depends(get_db)):
    db_receipt = models.Receipt(**receipt.model_dump())
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)
    return db_receipt

@app.get("/receipts/")
def read_receipts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    receipts = db.query(models.Receipt).offset(skip).limit(limit).all()
    return receipts

@app.get("/export/")
def export_receipts(db: Session = Depends(get_db)):
    # This endpoint remains the same
    pass

@app.get("/")
def read_root():
    return FileResponse('frontend/index.html')
