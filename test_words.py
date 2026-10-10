import pdfplumber
import os

PDF_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\source_pdfs"

filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Surveying.PDF")
with pdfplumber.open(filepath) as pdf:
    page = pdf.pages[0]
    words = page.extract_words()
    
    with open("pdf_out_words.txt", "w", encoding="utf-8") as f:
        # Find the header row
        header_y = None
        for w in words:
            if w['text'] == 'Sr.':
                header_y = w['top']
                break
                
        if header_y:
            f.write(f"Header found at top={header_y}\n")
            # Get all words roughly on this line
            header_words = [w for w in words if abs(w['top'] - header_y) < 5]
            # sort by x0
            header_words.sort(key=lambda w: w['x0'])
            for w in header_words:
                f.write(f"Word: '{w['text']}' at x0={w['x0']:.2f}, x1={w['x1']:.2f}\n")
        else:
            f.write("Header not found\n")
