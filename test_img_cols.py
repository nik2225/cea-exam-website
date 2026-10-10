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
    ]

filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Drawing.PDF")
with pdfplumber.open(filepath) as pb_pdf:
    for i in range(min(5, len(pb_pdf.pages))):
        page = pb_pdf.pages[i]
        vlines = get_vlines_from_header(page)
        if not vlines: continue
        for img in page.images:
            col = -1
            for j in range(len(vlines) - 1):
                if vlines[j] <= img['x0'] < vlines[j+1]:
                    col = j
                    break
            print(f"Page {i+1} Image at col {col}: x0={img['x0']}, top={img['top']}, width={img['width']}, height={img['height']}")
