import pdfplumber
import os

PDF_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\source_pdfs"

print("Started scanning...")
for filename in os.listdir(PDF_DIR):
    if not filename.lower().endswith(".pdf"): continue
    filepath = os.path.join(PDF_DIR, filename)
    with pdfplumber.open(filepath) as pb_pdf:
        total_images = sum(len(page.images) for page in pb_pdf.pages)
        total_curves = sum(len(page.curves) for page in pb_pdf.pages)
        print(f"{filename}: Images={total_images}, Curves={total_curves}")
