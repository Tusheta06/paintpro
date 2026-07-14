"""
PaintPro Inventory Management System
=====================================
Barcode & QR Code Generator Utility  |  utils/barcode_gen.py

Generates in-memory Barcodes and QR Codes for products.
"""

import qrcode
import barcode
from barcode.writer import ImageWriter
from io import BytesIO

def generate_qr_code(data_str: str) -> BytesIO:
    """
    Generates a QR Code for the given string (e.g., product SKU).
    Returns a BytesIO stream containing the PNG image.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data_str)
    qr.make(fit=True)

    # Use the PaintPro primary brand color (#6C63FF) for the QR code
    img = qr.make_image(fill_color="#6C63FF", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def generate_barcode(data_str: str) -> BytesIO:
    """
    Generates a Code128 Barcode for the given string (e.g., product SKU).
    Returns a BytesIO stream containing the PNG image.
    """
    # Use Code128 since it supports alphanumeric characters (unlike EAN13)
    code_class = barcode.get_barcode_class('code128')
    
    # We strip any non-ascii characters just in case, though SKUs should be clean.
    clean_data = "".join(c for c in data_str if ord(c) < 128)
    if not clean_data:
        clean_data = "UNKNOWN"
        
    code_instance = code_class(clean_data, writer=ImageWriter())
    
    buf = BytesIO()
    # Write image to buffer
    options = {
        'module_width': 0.2,
        'module_height': 15.0,
        'quiet_zone': 6.5,
        'font_size': 10,
        'text_distance': 5.0,
        'background': 'white',
        'foreground': 'black',
    }
    code_instance.write(buf, options=options)
    buf.seek(0)
    return buf
