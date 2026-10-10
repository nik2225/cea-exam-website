import pdfplumber
import os

PDF_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\source_pdfs"

filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Drawing.PDF")
with pdfplumber.open(filepath) as pb_pdf:
    page = pb_pdf.pages[0]
    for img in page.images:
        print(f"Image: x0={img['x0']}, top={img['top']}, width={img['width']}, height={img['height']}")
