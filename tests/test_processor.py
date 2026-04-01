from backend.processor import extract_info

def test_extract_info_simple():
    text = "Starbucks\nDate: 12/05/2023\nTotal: 15.50\nVAT: 2.50"
    data = extract_info(text)
    assert data["vendor"] == "Starbucks"
    assert data["date"] == "12/05/2023"
    assert data["total"] == 15.50
    assert data["vat"] == 2.50
    assert data["amount"] == 13.00
    assert data["category"] == "Food"

def test_extract_info_empty():
    text = ""
    data = extract_info(text)
    assert data["vendor"] == "Unknown"
    assert data["amount"] == 0.0

def test_extract_info_travel():
    text = "Uber Trip\n2023-11-20\nTotal: 25.00"
    data = extract_info(text)
    assert data["vendor"] == "Uber Trip"
    assert data["date"] == "2023-11-20"
    assert data["total"] == 25.00
    assert data["category"] == "Travel"
