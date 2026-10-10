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
    words = page.extract_words(
        x_tolerance=2, 
        y_tolerance=2,
        keep_blank_chars=True
    )
    
    # Identify question boundaries
    q_boundaries = []
    for w in words:
        x0 = w['x0']
        if x0 < vlines[1] and w['text'].isdigit():
            q_boundaries.append({
                'q_num': int(w['text']),
                'top': w['top'],
                'bottom': w['bottom'],
                'words': []
            })
            
    q_boundaries.sort(key=lambda q: q['top'])
    
    # Assign words to boundaries
    for w in words:
        x0 = w['x0']
        # Skip the Sr No numbers themselves
        if x0 < vlines[1] and w['text'].isdigit():
            continue
            
        w_center_y = (w['top'] + w['bottom']) / 2
        
        # Find which q_boundary this word belongs to
        assigned_q = None
        for i in range(len(q_boundaries)):
            start_y = q_boundaries[i]['top'] - 10 # small buffer
            end_y = q_boundaries[i+1]['top'] - 5 if i + 1 < len(q_boundaries) else 9999
            if start_y <= w_center_y < end_y:
                assigned_q = q_boundaries[i]
                break
                
        if assigned_q:
            # Determine column
            col_idx = 0
            for i in range(len(vlines) - 1):
                if vlines[i] <= x0 < vlines[i+1]:
                    col_idx = i
                    break
            assigned_q['words'].append({'col': col_idx, 'text': w['text'], 'top': w['top'], 'x0': w['x0']})
            
    # Compile text
    questions = []
    for q in q_boundaries:
        cols = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
        
        # Sort words inside question to maintain reading order
        # First group by lines (top approx), then sort by x0
        q['words'].sort(key=lambda w: (round(w['top'] / 5) * 5, w['x0']))
        
        for w in q['words']:
            if w['col'] > 0:
                cols[w['col']].append(w['text'])
                
        questions.append({
            'q_num': q['q_num'],
            'cols': cols
        })
        
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
