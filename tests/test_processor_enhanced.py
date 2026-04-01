from backend.processor import extract_info

def test_extract_info_detailed():
    text = "Starbucks\nDate: 2023-12-05\nTotal: 15.50\nVAT: 2.50"
    data = extract_info(text)
    assert data["vendor"] == "Starbucks"
    assert data["date"] == "2023-12-05"
    assert data["total"] == 15.50
    assert data["vat"] == 2.50
    assert data["amount"] == 13.00 # This is what processor.py currently outputs as amount
    assert data["category"] == "Food"

def test_extract_info_fuel():
    text = "Shell Gas Station\n2023-11-20\nTotal: 50.00\nFuel"
    data = extract_info(text)
    assert data["vendor"] == "Shell Gas Station"
    assert data["category"] == "Fuel"

def test_extract_info_entertainment():
    text = "AMC Theatres\n2023-11-20\nTotal: 30.00\nMovie tickets"
    data = extract_info(text)
    assert data["vendor"] == "AMC Theatres"
    assert data["category"] == "Entertainment"
