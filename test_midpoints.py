import pdfplumber
import os

PDF_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\source_pdfs"

def get_header_midpoints(page):
    words = page.extract_words()
    header_y = None
    for w in words:
        if w['text'] == 'Option':
            header_y = w['top']
            break
            
    if not header_y: return None
    
    header_words = [w for w in words if abs(w['top'] - header_y) < 5]
    header_words.sort(key=lambda w: w['x0'])
    
    # Let's find specific words:
    # "Question", "Correct", "1", "2", "3", "4"
    q_w = next((w for w in header_words if 'Question' in w['text']), None)
    correct_w = next((w for w in header_words if 'Correct' in w['text']), None)
    
    # Options have '1', '2', '3', '4' in header_words
    opt1_w = next((w for w in header_words if w['text'] == '1'), None)
    opt2_w = next((w for w in header_words if w['text'] == '2'), None)
    opt3_w = next((w for w in header_words if w['text'] == '3'), None)
    opt4_w = next((w for w in header_words if w['text'] == '4'), None)
    
    # Sr.no.
    sr_w = next((w for w in header_words if 'no' in w['text'].lower() or 'sr' in w['text'].lower()), None)
    
    print(f"Sr: {sr_w}")
    print(f"Question: {q_w}")
    print(f"Correct: {correct_w}")
    print(f"Opt1: {opt1_w}")
    print(f"Opt2: {opt2_w}")
    print(f"Opt3: {opt3_w}")
    print(f"Opt4: {opt4_w}")
    
    if not (sr_w and q_w and correct_w and opt1_w and opt2_w and opt3_w and opt4_w):
        return None
        
    vlines = [
        0,
        (sr_w['x1'] + q_w['x0']) / 2,
        (q_w['x1'] + correct_w['x0']) / 2,
        (correct_w['x1'] + opt1_w['x0'] - 30) / 2, # Note: "Option 1" has "Option" before "1"
        # We need the word "Option" for each to get the left boundary
    ]

filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Maths & APM.PDF")
with pdfplumber.open(filepath) as pb_pdf:
    page = pb_pdf.pages[0]
    get_header_midpoints(page)
