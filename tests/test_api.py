from fastapi.testclient import TestClient
from backend.main import app
import os

client = TestClient(app)

def test_get_receipts_empty():
    # Ensure DB is empty or at least responding
    response = client.get("/receipts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_save_receipt():
    data = {
        "vendor": "Test Vendor",
        "date": "2023-12-01",
        "amount": 10.0,
        "vat": 2.0,
        "total": 12.0,
        "category": "Supplies"
    }
    response = client.post("/save", json=data)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Verify it was saved
    response = client.get("/receipts")
    receipts = response.json()
    assert any(r["vendor"] == "Test Vendor" for r in receipts)

def test_export():
    # Make sure there's data
    test_save_receipt()
    response = client.get("/export")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
