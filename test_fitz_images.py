import fitz
import os

PDF_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\source_pdfs"

filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Maths & APM.PDF")
doc = fitz.open(filepath)
for i in range(min(5, len(doc))):
    page = doc.load_page(i)
    images = page.get_images()
    print(f"Maths Page {i+1} Images: {len(images)}")
