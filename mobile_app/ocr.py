import cv2
import pytesseract
import numpy as np
from PIL import Image
import io

def preprocess_image(image_bytes):
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return None

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply thresholding
    # Using adaptive thresholding for better results with varying lighting
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Optional: Noise removal
    # kernel = np.ones((1, 1), np.uint8)
    # thresh = cv2.dilate(thresh, kernel, iterations=1)
    # thresh = cv2.erode(thresh, kernel, iterations=1)

    return thresh

def perform_ocr(image_bytes):
    processed_img = preprocess_image(image_bytes)

    if processed_img is None:
        # Fallback to original image if preprocessing fails
        img = Image.open(io.BytesIO(image_bytes))
    else:
        img = Image.fromarray(processed_img)

    # Perform OCR
    text = pytesseract.image_to_string(img)
    return text
