import pdfplumber
import os
import json

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
        0,
        70,
        correct_w['x0'] - 5,
        options[1]['x0'] - 5,
        options[2]['x0'] - 5,
        options[3]['x0'] - 5,
        options[4]['x0'] - 5,
        9999
    ]

def extract_spatial(page, vlines):
    words = page.extract_words()
    # Sort primarily by top, then by x0 to read left-to-right top-to-bottom
    words.sort(key=lambda w: (w['top'], w['x0']))
    
    questions = []
    current_q = None
    
    for w in words:
        # Determine column
        x0 = w['x0']
        col_idx = 0
        for i in range(len(vlines) - 1):
            if vlines[i] <= x0 < vlines[i+1]:
                col_idx = i
                break
                
        text = w['text']
        
        # If we see a digit in column 0, it's a new question
        if col_idx == 0 and text.isdigit():
            if current_q:
                questions.append(current_q)
            current_q = {
                'q_num': int(text),
                'cols': {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
            }
        elif current_q and col_idx > 0:
            current_q['cols'][col_idx].append(text)
            
    if current_q:
        questions.append(current_q)
        
    return questions

filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Maths & APM.PDF")
with pdfplumber.open(filepath) as pb_pdf:
    page = pb_pdf.pages[0]
    vlines = get_vlines_from_header(page)
    
    qs = extract_spatial(page, vlines)
    for q in qs[:3]:
        print(f"Q{q['q_num']}: {' '.join(q['cols'][1])}")
        print(f"  Ans: {' '.join(q['cols'][2])}")
        print(f"  Op1: {' '.join(q['cols'][3])}")
        print(f"  Op2: {' '.join(q['cols'][4])}")
        print(f"  Op3: {' '.join(q['cols'][5])}")
        print(f"  Op4: {' '.join(q['cols'][6])}")
        print("-" * 20)
