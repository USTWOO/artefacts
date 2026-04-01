import spacy
import re
from datetime import datetime

# Load SpaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # If not found, fall back to a mock or handle it
    nlp = None

def extract_info(text):
    data = {
        "vendor": "Unknown",
        "date": "Unknown",
        "amount": 0.0,
        "vat": 0.0,
        "total": 0.0,
        "category": "Miscellaneous"
    }

    if not text:
        return data

    doc = nlp(text) if nlp else None

    # --- Vendor Extraction ---
    # Try to find ORG in entities, usually the first one is the vendor
    if doc:
        for ent in doc.ents:
            if ent.label_ == "ORG":
                data["vendor"] = ent.text.strip()
                break

    # Fallback: often the first line is the vendor
    if data["vendor"] == "Unknown":
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if lines:
            data["vendor"] = lines[0].strip().replace('\n', '').replace('\r', '')

    # --- Date Extraction ---
    # Simple regex for DD/MM/YYYY or MM/DD/YYYY or YYYY-MM-DD
    date_patterns = [
        r"\d{1,2}/\d{1,2}/\d{2,4}",
        r"\d{4}-\d{1,2}-\d{1,2}",
        r"\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{2,4}"
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["date"] = match.group()
            break

    # --- Amount Extraction ---
    # Look for patterns like "Total: 12.34" or just "12.34" near the end
    # First, find all decimal numbers
    amounts = re.findall(r"(\d+\.\d{2})", text)
    if amounts:
        amounts = [float(a) for a in amounts]
        data["total"] = max(amounts)

        # Heuristic for VAT (often around 20% or 5-10% of total)
        # Look for keywords like "VAT", "Tax", "IVA"
        tax_match = re.search(r"(?:VAT|TAX|IVA)\s*:?\s*(\d+\.\d{2})", text, re.IGNORECASE)
        if tax_match:
            data["vat"] = float(tax_match.group(1))

        # Base amount
        data["amount"] = data["total"] - data["vat"]

    # --- Category Logic ---
    # Simple keyword-based categorization
    categories = {
        "Food": ["restaurant", "cafe", "food", "burger", "coffee", "lunch", "dinner", "pizza", "starbucks"],
        "Travel": ["uber", "taxi", "train", "flight", "hotel", "airline", "bus"],
        "Fuel": ["shell", "bp", "exxon", "fuel", "gas station", "petrol"],
        "Entertainment": ["amc", "theatre", "movie", "concert", "stadium", "netflix", "spotify"],
        "Supplies": ["stationery", "paper", "pen", "office", "staples", "amazon"],
        "Utilities": ["electric", "water", "internet", "phone"],
    }

    text_lower = text.lower()
    for cat, keywords in categories.items():
        if any(kw in text_lower for kw in keywords):
            data["category"] = cat
            break

    return data
