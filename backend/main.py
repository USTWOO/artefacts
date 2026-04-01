from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import os
from .ocr import perform_ocr
from .processor import extract_info
from .database import save_receipt, get_receipts, delete_receipt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReceiptData(BaseModel):
    vendor: str
    date: str
    amount: float
    vat: float
    total: float
    category: str

@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        text = perform_ocr(contents)
        extracted_data = extract_info(text)
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
