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
    
    # Calculate midpoints for robust boundaries!
    def midpoint(w1, w2):
        if not w1 or not w2: return 0
        return (w1['x1'] + w2['x0']) / 2
        
    # Find the words right before each Option to calculate midpoint
    # "Question" -> "Correct Option"
    question_w = next((w for w in header_words if w['text'] == 'Question'), None)
    
    # It's better to just use the actual visual table lines!
    # Let's see if we can extract the actual vertical lines from the page curves/lines.
    return []

filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Maths & APM.PDF")
with pdfplumber.open(filepath) as pb_pdf:
    page = pb_pdf.pages[0]
    
    # Print the coordinates of all vertical lines in the page!
    v_lines = [l for l in page.lines if abs(l['x0'] - l['x1']) < 1]
    v_lines.sort(key=lambda l: l['x0'])
    
    print(f"Found {len(v_lines)} vertical lines.")
    xs = sorted(list(set([round(l['x0']) for l in v_lines])))
    print("Unique X coordinates:", xs)
