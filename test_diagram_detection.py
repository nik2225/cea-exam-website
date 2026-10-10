import pdfplumber
import os

PDF_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\source_pdfs"

filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Drawing.PDF")
with pdfplumber.open(filepath) as pb_pdf:
    for i in range(min(5, len(pb_pdf.pages))):
        page = pb_pdf.pages[i]
        print(f"Page {i+1}:")
        print(f"  Images: {len(page.images)}")
        print(f"  Curves: {len(page.curves)}")
        print(f"  Rects: {len(page.rects)}")
        print(f"  Lines: {len(page.lines)}")
        
filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Maths & APM.PDF")
with pdfplumber.open(filepath) as pb_pdf:
    for i in range(min(5, len(pb_pdf.pages))):
        page = pb_pdf.pages[i]
        print(f"Maths Page {i+1}:")
        print(f"  Images: {len(page.images)}")
        print(f"  Curves: {len(page.curves)}")
        print(f"  Rects: {len(page.rects)}")
        print(f"  Lines: {len(page.lines)}")
