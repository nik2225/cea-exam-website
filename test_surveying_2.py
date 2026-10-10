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
    
    q_w = next((w for w in header_words if 'Question' in w['text']), None)
    correct_w = next((w for w in header_words if 'Correct' in w['text']), None)
    options = [w for w in header_words if w['text'] == 'Option']
    if not correct_w or not q_w or len(options) < 5: return None
    
    return [
        0,
        70,
        (q_w['x1'] + correct_w['x0']) / 2,
        (correct_w['x1'] + options[1]['x0']) / 2,
        (options[1]['x0'] + options[2]['x0']) / 2,
        (options[2]['x0'] + options[3]['x0']) / 2,
        (options[3]['x0'] + options[4]['x0']) / 2,
        9999
    ], max(w['bottom'] for w in header_words) if header_words else 0

def extract_spatial(page, vlines, header_bottom):
    words = page.extract_words(x_tolerance=2, y_tolerance=2, keep_blank_chars=True)
    
    q_boundaries = []
    for w in words:
        if w['bottom'] < header_bottom + 2: continue
        x0 = w['x0']
        if x0 < vlines[1] and w['text'].isdigit():
            q_boundaries.append({
                'q_num': int(w['text']),
                'top': w['top'],
                'bottom': w['bottom'],
                'words': []
            })
            
    q_boundaries.sort(key=lambda q: q['top'])
    
    for w in words:
        if w['bottom'] < header_bottom + 2: continue
            
        x0 = w['x0']
        if x0 < vlines[1] and w['text'].isdigit(): continue
            
        w_center_y = (w['top'] + w['bottom']) / 2
        assigned_q = None
        for i in range(len(q_boundaries)):
            if i == 0: start_y = header_bottom
            else: start_y = (q_boundaries[i-1]['bottom'] + q_boundaries[i]['top']) / 2
                
            if i + 1 < len(q_boundaries): end_y = (q_boundaries[i]['bottom'] + q_boundaries[i+1]['top']) / 2
            else: end_y = 9999
                
            if start_y <= w_center_y < end_y:
                assigned_q = q_boundaries[i]
                break
                
        if assigned_q:
            col_idx = 0
            for i in range(len(vlines) - 1):
                if vlines[i] <= x0 < vlines[i+1]:
                    col_idx = i
                    break
            assigned_q['words'].append({'col': col_idx, 'text': w['text'], 'top': w['top'], 'x0': w['x0'], 'w_center_y': w_center_y})
            
    questions = []
    for q in q_boundaries:
        cols = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
        q['words'].sort(key=lambda w: (round(w['top'] / 5) * 5, w['x0']))
        for w in q['words']:
            if w['col'] > 0:
                cols[w['col']].append(w['text'])
        questions.append({
            'q_num': q['q_num'],
            'words': q['words'],
            'cols': cols,
            'top': q['top'],
            'bottom': q['bottom']
        })
    return questions

filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Surveying.PDF")
with pdfplumber.open(filepath) as pb_pdf:
    page = pb_pdf.pages[0]
    vlines, header_bottom = get_vlines_from_header(page)
    qs = extract_spatial(page, vlines, header_bottom)
    
    print(f"vlines: {vlines}")
    print(f"header_bottom: {header_bottom}")
    
    q1 = qs[0]
    print(f"Q1 words:")
    for w in q1['words']:
        print(f"  Col {w['col']}: '{w['text']}' (x0={w['x0']:.2f}, cy={w['w_center_y']:.2f})")
