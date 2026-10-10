import fitz # PyMuPDF
import pdfplumber
import os

PDF_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\source_pdfs"

def get_vlines_from_header(page):
    words = page.extract_words()
    header_y = None
    for w in words:
        if w['text'] == 'Option':
            header_y = w['top']
            break
            
    if not header_y: return None
    
    header_words = [w for w in words if abs(w['top'] - header_y) < 5]
    header_words.sort(key=lambda w: w['x0'])
    
    correct_w = next((w for w in header_words if w['text'] == 'Correct'), None)
    options = [w for w in header_words if w['text'] == 'Option']
    if not correct_w or len(options) < 5: return None
    
    return [
        30,
        70,
        correct_w['x0'] - 5,
        options[1]['x0'] - 5,
        options[2]['x0'] - 5,
        options[3]['x0'] - 5,
        options[4]['x0'] - 5,
        page.width - 20
    ]

filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Maths & APM.PDF")
with pdfplumber.open(filepath) as pb_pdf:
    page = pb_pdf.pages[0]
    vlines = get_vlines_from_header(page)
    
    tables = page.extract_tables({
        "vertical_strategy": "explicit",
        "explicit_vertical_lines": vlines,
        "horizontal_strategy": "lines"
    })
    
    with open("pdf_out_debug.txt", "w", encoding="utf-8") as f:
        if tables:
            for row in tables[0]:
                f.write(f"Row Length: {len(row)} | Data: {row}\n")
