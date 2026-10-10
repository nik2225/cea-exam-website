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
    
    sr_w = next((w for w in header_words if 'Sr' in w['text'] or 'No' in w['text'] or 'sr' in w['text'].lower()), None)
    
    if sr_w and q_w:
        vline1 = (sr_w['x1'] + q_w['x0']) / 2
    else:
        vline1 = q_w['x0'] - 20
        
    return [
        0,
        vline1,
        (q_w['x1'] + correct_w['x0']) / 2,
        (correct_w['x1'] + options[1]['x0']) / 2,
        (options[1]['x0'] + options[2]['x0']) / 2,
        (options[2]['x0'] + options[3]['x0']) / 2,
        (options[3]['x0'] + options[4]['x0']) / 2,
        9999
    ], max(w['bottom'] for w in header_words) if header_words else 0

filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Surveying.PDF")
with pdfplumber.open(filepath) as pb_pdf:
    page = pb_pdf.pages[0]
    res = get_vlines_from_header(page)
    print(res[0] if res else "None")
