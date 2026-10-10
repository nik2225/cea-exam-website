import pdfplumber
import os

PDF_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\source_pdfs"

def get_vlines_from_header(page):
    words = page.extract_words()
    # Find word 'Option'
    header_y = None
    for w in words:
        if w['text'] == 'Option':
            header_y = w['top']
            break
            
    if not header_y: return None
    
    header_words = [w for w in words if abs(w['top'] - header_y) < 5]
    header_words.sort(key=lambda w: w['x0'])
    
    # We want to find the x coordinates that separate the columns
    # 1. Sr. No. -> left bound of page
    # 2. Question -> just before "Question"
    # 3. Correct Option -> just before "Correct"
    # 4. Option 1 -> just before "Option 1"
    # 5. Option 2 -> just before "Option 2"
    # 6. Option 3 -> just before "Option 3"
    # 7. Option 4 -> just before "Option 4"
    
    col_starts = []
    
    # Let's find "Correct"
    correct_w = next((w for w in header_words if w['text'] == 'Correct'), None)
    opt1_w = next((w for w in header_words if w['text'] == '1'), None)
    opt2_w = next((w for w in header_words if w['text'] == '2'), None)
    opt3_w = next((w for w in header_words if w['text'] == '3'), None)
    opt4_w = next((w for w in header_words if w['text'] == '4'), None)
    
    if not (correct_w and opt1_w and opt2_w and opt3_w and opt4_w):
        return None
        
    # Find option words
    options = [w for w in header_words if w['text'] == 'Option']
    if len(options) < 5: return None
    
    # We can estimate boundaries exactly in the middle of headers
    vlines = [
        30, # Left edge
        70, # After Sr No
        correct_w['x0'] - 5,
        options[1]['x0'] - 5, # Option 1
        options[2]['x0'] - 5, # Option 2
        options[3]['x0'] - 5, # Option 3
        options[4]['x0'] - 5, # Option 4
        page.width - 20 # Right edge
    ]
    return vlines

for filename in os.listdir(PDF_DIR):
    if not filename.lower().endswith(".pdf"): continue
    filepath = os.path.join(PDF_DIR, filename)
    print(f"\n--- {filename} ---")
    with pdfplumber.open(filepath) as pdf:
        page = pdf.pages[0]
        vlines = get_vlines_from_header(page)
        print("vlines:", vlines)
