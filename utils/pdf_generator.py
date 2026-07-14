"""
PaintPro Inventory Management System
=====================================
PDF Generator Utility  |  utils/pdf_generator.py

Generates professional PDF invoices using fpdf2.
"""

from fpdf import FPDF
import os
from streamlit import pdf
from utils.formatting import format_currency, format_date

class InvoicePDF(FPDF):
    def header(self):
        # Company Logo / Brand
        self.set_font("helvetica", "B", 24)
        self.set_text_color(108, 99, 255) # Primary color
        self.cell(0, 10, "PaintPro IMS", border=0, new_x="LMARGIN", new_y="NEXT", align="L")
        
        self.set_font("helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "123 Color Street, Design District, 400001", border=0, new_x="LMARGIN", new_y="NEXT", align="L")
        self.cell(0, 5, "Phone: +91 9876543210 | GSTIN: 22AAAAA0000A1Z5", border=0, new_x="LMARGIN", new_y="NEXT", align="L")
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} - Thank you for your business!", border=0, align="C")

def generate_sale_invoice_pdf(sale_data: dict, items: list[dict]) -> bytes:
    """Generate a PDF invoice and return it as bytes."""
    pdf = InvoicePDF()
    
    # Add Unicode Font for the ₹ symbol
    # Make sure 'DejaVuSans.ttf' exists in your project root or utils folder!
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    bold_font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans-Bold.ttf")

    print("Font path:", font_path)
    print("Regular exists:", os.path.exists(font_path))
    print("Bold exists:", os.path.exists(bold_font_path))

    pdf.add_font("DejaVu", "", font_path)
    pdf.add_font("DejaVu", "B", bold_font_path)

    print("Fonts loaded successfully")

    pdf.alias_nb_pages()
    pdf.add_page()
    
    # ─── Invoice Header Info ──────────────────────────────────────────────────
    
    # Left Side: Bill To
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(100, 6, "Billed To:", border=0, new_x="RIGHT", new_y="TOP")
    
    # Right Side: Invoice Meta
    pdf.cell(90, 6, "INVOICE DETAILS", border=0, new_x="LMARGIN", new_y="NEXT", align="R")
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(100, 5, sale_data.get('customer_name', 'Walk-in Customer'), border=0, new_x="RIGHT", new_y="TOP")
    pdf.cell(90, 5, f"Invoice #: {sale_data['invoice_number']}", border=0, new_x="LMARGIN", new_y="NEXT", align="R")
    
    addr = sale_data.get('customer_address') or ''
    pdf.cell(100, 5, addr[:50] if addr else "N/A", border=0, new_x="RIGHT", new_y="TOP")
    pdf.cell(90, 5, f"Date: {format_date(sale_data['invoice_date'])}", border=0, new_x="LMARGIN", new_y="NEXT", align="R")
    
    gst = sale_data.get('customer_gst') or ''
    pdf.cell(100, 5, f"GSTIN: {gst}" if gst else "", border=0, new_x="RIGHT", new_y="TOP")
    pdf.cell(90, 5, f"Payment: {sale_data['payment_status'].upper()}", border=0, new_x="LMARGIN", new_y="NEXT", align="R")
    
    pdf.ln(15)
    
    # ─── Items Table ──────────────────────────────────────────────────────────
    
    # Table Header
    pdf.set_fill_color(240, 240, 245)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("helvetica", "B", 10)
    
    pdf.cell(20, 10, "SKU", border=1, fill=True, align="C")
    pdf.cell(80, 10, "Description", border=1, fill=True, align="L")
    pdf.cell(15, 10, "Qty", border=1, fill=True, align="C")
    pdf.cell(25, 10, "Rate", border=1, fill=True, align="R")
    pdf.cell(20, 10, "GST", border=1, fill=True, align="R")
    pdf.cell(30, 10, "Amount", border=1, fill=True, new_x="LMARGIN", new_y="NEXT", align="R")
    
    # Table Body
    pdf.set_font("helvetica", "", 9)
    for item in items:
        pdf.cell(20, 8, item.get('sku', ''), border=1, align="C")
        product_name = item.get('product_name', '').replace("—", "-")
        pdf.cell(80, 8, product_name[:45], border=1, align="L")
        pdf.cell(15, 8, str(int(item.get('quantity', 0))), border=1, align="C")
        pdf.cell(25, 8, f"{item.get('unit_price', 0):.2f}", border=1, align="R")
        pdf.cell(20, 8, f"{item.get('gst_percentage', 0)}%", border=1, align="R")
        pdf.cell(30, 8, f"{item.get('total_price', 0):.2f}", border=1, new_x="LMARGIN", new_y="NEXT", align="R")
        
    pdf.ln(10)
    
    # ─── Totals ───────────────────────────────────────────────────────────────
    
    pdf.set_font("helvetica", "", 10)
    
    # Move to the right side
    start_x = pdf.w - 80 - pdf.r_margin
    
    # For amounts containing ₹, we MUST use the DejaVu font
    font_name = "DejaVu" if os.path.exists(font_path) else "helvetica"
    
    print(font_name)
    print(font_path)
    print(os.path.exists(font_path))

    pdf.set_x(start_x)
    pdf.cell(40, 6, "Subtotal:", border=0)
    pdf.set_font(font_name, "", 10)
    pdf.cell(40, 6, format_currency(sale_data['subtotal']), border=0, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    
    pdf.set_x(start_x)
    pdf.cell(40, 6, "Tax Total:", border=0)
    pdf.set_font(font_name, "", 10)
    pdf.cell(40, 6, format_currency(sale_data['gst_amount']), border=0, align="R", new_x="LMARGIN", new_y="NEXT")
    print(sale_data.keys()) 
    pdf.set_font("helvetica", "", 10)
    
    if float(sale_data.get('discount_amount', 0)) > 0:
        pdf.set_x(start_x)
        pdf.cell(40, 6, "Discount:", border=0)
        pdf.set_text_color(220, 53, 69) # Red
        pdf.set_font(font_name, "", 10)
        pdf.cell(40, 6, f"-{format_currency(sale_data['discount_amount'])}", border=0, align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(50, 50, 50)
        pdf.set_font("helvetica", "", 10)
        
    pdf.set_x(start_x)
    pdf.set_font(font_name, "B", 12)
    pdf.cell(40, 8, "Grand Total:", border="T")
    pdf.cell(40, 8, format_currency(sale_data['grand_total']), border="T", align="R", new_x="LMARGIN", new_y="NEXT")
    

    # Finalize
    return bytes(pdf.output(dest="S"))
    # pdf.set_text_color(50, 50, 50)
            
    # pdf.set_x(start_x)
    # pdf.set_font("DejaVu", "B", 12)
    # pdf.cell(40, 8, "Grand Total:", border="T")
    # pdf.cell(40, 8, format_currency(sale_data['grand_total']), border="T", align="R", new_x="LMARGIN", new_y="NEXT")
        
    #     # Finalize
    # return pdf.output(dest="S")
