import pytesseract
from pdf2image import convert_from_path
import re
from datetime import datetime

def extract_text_from_pdf(pdf_path):
    # Convert PDF to images
    images = convert_from_path(pdf_path)

    full_text = ""
    for image in images:
        text = pytesseract.image_to_string(image)
        full_text += text + "\n"

    return full_text

def parse_transactions(text):
    # This is a basic parser. In a real scenario, this would be highly dependent on the statement format.
    # We'll look for lines like "DD/MM/YYYY description amount"
    transactions = []

    # Example regex: 2023-10-25 SOME VENDOR 123.45
    # Or 25/10/2023 SOME VENDOR 123.45
    date_regex = r'(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})'

    lines = text.split('\n')
    for line in lines:
        match = re.search(date_regex, line)
        if match:
            date_str = match.group(0)
            try:
                if '/' in date_str:
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
                else:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

                # Try to find amount at the end of the line
                amount_match = re.search(r'(-?\d+[\.,]\d{2})\s*$', line)
                if amount_match:
                    amount_str = amount_match.group(1).replace(',', '.')
                    amount = float(amount_str)

                    description = line.replace(date_str, '').replace(amount_match.group(1), '').strip()

                    transactions.append({
                        "date": date_obj,
                        "description": description,
                        "amount": abs(amount),
                        "is_income": amount > 0  # Assuming positive is credit, negative is debit
                    })
            except ValueError:
                continue

    return transactions
