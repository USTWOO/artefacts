from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import os
import shutil
from datetime import datetime
from .ocr import perform_ocr
from .processor import extract_info
from .database import save_receipt, get_receipts, delete_receipt, get_monthly_stats, get_category_stats

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for receipt images
IMAGES_DIR = "database/images"
os.makedirs(IMAGES_DIR, exist_ok=True)
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

class ReceiptData(BaseModel):
    vendor: str
    date: str
    subtotal: float
    vat: float
    total: float
    category: str
    image_path: str = None

@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    # Save the file temporarily to perform OCR
    # or just use bytes
    contents = await file.read()

    # Save image for later reference
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(IMAGES_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    try:
        text = perform_ocr(contents)
        extracted_data = extract_info(text)
        # Include image path for later association
        extracted_data["image_path"] = f"/images/{filename}"
        # Rename amount to subtotal for frontend consistency
        extracted_data["subtotal"] = extracted_data.pop("amount", 0.0)
        return extracted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save")
async def save_endpoint(data: ReceiptData):
    try:
        save_receipt(data.model_dump())
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/receipts")
async def get_receipts_endpoint():
    return get_receipts()

@app.get("/stats/monthly")
async def get_monthly_stats_endpoint():
    return get_monthly_stats()

@app.get("/stats/category")
async def get_category_stats_endpoint():
    return get_category_stats()

@app.delete("/receipts/{receipt_id}")
async def delete_receipt_endpoint(receipt_id: int):
    delete_receipt(receipt_id)
    return {"status": "success"}

@app.get("/export")
async def export_endpoint():
    receipts = get_receipts()
    if not receipts:
        raise HTTPException(status_code=404, detail="No receipts to export")

    df = pd.DataFrame(receipts)
    export_path = "receipts_export.xlsx"
    df.to_excel(export_path, index=False)

    return FileResponse(export_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="receipts.xlsx")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
