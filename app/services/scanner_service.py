# File: app/services/scanner_service.py
import base64
import asyncio
import numpy as np
import cv2
import zxingcpp

def _decode_barcode_sync(image_base64: str) -> str:
    """Synchronous core logic for decoding."""
    img_str = image_base64
    if ',' in img_str:
        img_str = img_str.split(',')[1]
    
    try:
        img_bytes = base64.b64decode(img_str)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img_opencv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img_opencv is None:
            raise ValueError("Failed to decode image format. Ensure payload is a valid base64 image.")
        
        decoded_objects = zxingcpp.read_barcodes(img_opencv)

        if not decoded_objects:
            raise ValueError("Barcode unreadable. Please ensure the ID Card image is clear and well-lit.")

        return decoded_objects[0].text
    except Exception as e:
        raise ValueError(f"Image processing failure: {str(e)}")

async def extract_barcode_from_base64(image_base64: str) -> str:
    """
    Silicon Valley Standard: Offloads heavy CPU-bound image processing 
    to a separate thread, keeping the async event loop 100% responsive.
    """
    return await asyncio.to_thread(_decode_barcode_sync, image_base64)