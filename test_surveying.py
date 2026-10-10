import pdfplumber
import os

PDF_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\source_pdfs"
filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Surveying.PDF")

with pdfplumber.open(filepath) as pb_pdf:
    page = pb_pdf.pages[0]
    words = page.extract_words()
    
    print("Words in first page:")
    for w in words[:150]:
        try:
            print(f"'{w['text']}' at x0={w['x0']:.2f}, top={w['top']:.2f}")
        except UnicodeEncodeError:
            print(f"Unicode character at x0={w['x0']:.2f}, top={w['top']:.2f}")
