import fitz # PyMuPDF
import pdfplumber
import os
import json
import glob

PDF_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\source_pdfs"
OUTPUT_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\src\data"
IMG_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\public\pdf_pages"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

SUBJECT_MAP = {
    "GCE": "General Civil Engineering",
    "Maths & APM": "Mathematics & Applied Mechanics",
    "Construction": "Construction, Construction Materials, Stores Account",
    "Surveying": "Surveying",
    "Drawing": "Drawing"
}

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
    
    # Options array:
    # 0 -> 'Option' in 'Correct Option'
    # 1 -> 'Option' in 'Option 1'
    # 2 -> 'Option' in 'Option 2'
    # 3 -> 'Option' in 'Option 3'
    # 4 -> 'Option' in 'Option 4'
    
    # Note: 'Option' word has an x1. But there's a space and then '1' or '2'. 
    # To be extremely safe, we should just use the options['x0'] array and space them evenly.
    # Actually, the options headers are centered in their columns.
    # The midpoint between options[1]['x0'] and options[2]['x0'] is perfect.
    
    return [
        0,
        60,
        (q_w['x1'] + correct_w['x0']) / 2, # Midpoint Question -> Correct
        (correct_w['x1'] + options[1]['x0']) / 2, # Midpoint Correct -> Opt1
        (options[1]['x0'] + options[2]['x0']) / 2, # Midpoint Opt1 -> Opt2
        (options[2]['x0'] + options[3]['x0']) / 2, # Midpoint Opt2 -> Opt3
        (options[3]['x0'] + options[4]['x0']) / 2, # Midpoint Opt3 -> Opt4
        9999
    ], max(w['bottom'] for w in header_words) if header_words else 0

def extract_spatial(page, vlines, header_bottom):
    words = page.extract_words(x_tolerance=2, y_tolerance=2, keep_blank_chars=True)
    
    q_boundaries = []
    for w in words:
        if w['bottom'] < header_bottom + 2:
            continue
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
        if w['bottom'] < header_bottom + 2:
            continue
            
        x0 = w['x0']
        if x0 < vlines[1] and w['text'].isdigit():
            continue
            
        w_center_y = (w['top'] + w['bottom']) / 2
        assigned_q = None
        for i in range(len(q_boundaries)):
            if i == 0:
                start_y = header_bottom
            else:
                start_y = (q_boundaries[i-1]['bottom'] + q_boundaries[i]['top']) / 2
                
            if i + 1 < len(q_boundaries):
                end_y = (q_boundaries[i]['bottom'] + q_boundaries[i+1]['top']) / 2
            else:
                end_y = 9999
                
            if start_y <= w_center_y < end_y:
                assigned_q = q_boundaries[i]
                break
                
        if assigned_q:
            col_idx = 0
            for i in range(len(vlines) - 1):
                if vlines[i] <= x0 < vlines[i+1]:
                    col_idx = i
                    break
            assigned_q['words'].append({'col': col_idx, 'text': w['text'], 'top': w['top'], 'x0': w['x0']})
            
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
            'cols': cols
        })
        
    return questions

def process_pdfs():
    pdfs = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    all_results = {}
    validation_reports = {}

    for pdf_path in pdfs:
        filename = os.path.basename(pdf_path)
        subject_key = next((k for k in SUBJECT_MAP if k.lower() in filename.lower()), None)
        if not subject_key: continue
            
        subject = SUBJECT_MAP[subject_key]
        print(f"Processing {filename}...")
        
        if subject not in all_results:
            all_results[subject] = []
            
        doc = fitz.open(pdf_path)
        with pdfplumber.open(pdf_path) as pb_pdf:
            vlines = None
            header_bottom = 0
            if len(pb_pdf.pages) > 0:
                res = get_vlines_from_header(pb_pdf.pages[0])
                if res:
                    vlines, header_bottom = res
            if not vlines: vlines = [0, 70, 312, 371, 423, 474, 526, 9999]
            
            for page_num in range(len(doc)):
                pb_page = pb_pdf.pages[page_num]
                
                # Check for header on THIS page
                page_header_bottom = 0
                res = get_vlines_from_header(pb_page)
                if res:
                    _, page_header_bottom = res
                
                # Save full page source
                fitz_page = doc.load_page(page_num)
                full_pix = fitz_page.get_pixmap(dpi=150)
                full_img_name = f"{subject_key.replace(' ', '_')}_full_p{page_num+1}.png"
                full_pix.save(os.path.join(IMG_DIR, full_img_name))
                source_page_path = f"/pdf_pages/{full_img_name}"
                
                qs = extract_spatial(pb_page, vlines, page_header_bottom)
                
                for q in qs:
                    q_num = q['q_num']
                    q_text = " ".join(q['cols'][1]).strip()
                    correct_opt_raw = " ".join(q['cols'][2]).strip()
                    opt1 = " ".join(q['cols'][3]).strip()
                    opt2 = " ".join(q['cols'][4]).strip()
                    opt3 = " ".join(q['cols'][5]).strip()
                    opt4 = " ".join(q['cols'][6]).strip()
                    
                    correct_idx = -1
                    if correct_opt_raw.isdigit():
                        correct_idx = int(correct_opt_raw) - 1
                        
                    # Find if this question has a diagram by checking page.images
                    # The vertical bounds of the question are q['top'] to q['bottom']
                    # However, q from extract_spatial doesn't have top/bottom directly.
                    # Let's calculate the bounding box of all words in this question.
                    q_words = q.get('words', [])
                    
                    has_diagram = False
                    diagram_path = ""
                    
                    if q_words:
                        q_top = min(w['top'] for w in q_words)
                        q_bottom = max(w['top'] for w in q_words) + 15 # approximate bottom
                        
                        images_in_row = []
                        for img in pb_page.images:
                            img_center_y = img['top'] + img['height'] / 2
                            if q_top - 20 <= img_center_y <= q_bottom + 20:
                                images_in_row.append(img)
                                
                        if images_in_row:
                            has_diagram = True
                            cols_with_images = set()
                            for img in images_in_row:
                                x0 = img['x0']
                                col = -1
                                for j in range(len(vlines) - 1):
                                    if vlines[j] <= x0 < vlines[j+1]:
                                        col = j
                                        break
                                if col == 0: col = 1 # merge with question
                                if col != -1: cols_with_images.add(col)
                                
                            if cols_with_images:
                                min_col = min(cols_with_images)
                                max_col = max(cols_with_images)
                                
                                crop_x0 = max(0, vlines[min_col] - 10)
                                crop_x1 = vlines[max_col+1] + 10 if max_col+1 < len(vlines) else pb_page.width
                                crop_y0 = max(0, q_top - 15)
                                crop_y1 = q_bottom + 25
                                
                                img_name = f"{subject_key.replace(' ', '_')}_{q_num}_p{page_num+1}.png"
                                fitz_page = doc.load_page(page_num)
                                rect = fitz.Rect(crop_x0, crop_y0, crop_x1, crop_y1)
                                pix = fitz_page.get_pixmap(dpi=200, clip=rect)
                                pix.save(os.path.join(IMG_DIR, img_name))
                                diagram_path = f"/pdf_pages/{img_name}"
                        
                        # Fallback heuristic: If no image found, but text suggests a diagram, crop the question cell
                        elif "identify" in q_text.lower() or "symbol" in q_text.lower() or "figure" in q_text.lower():
                            has_diagram = True
                            crop_x0 = max(0, vlines[1] - 10)
                            crop_x1 = vlines[2] + 10
                            crop_y0 = max(0, q_top - 15)
                            crop_y1 = q_bottom + 25
                            
                            img_name = f"{subject_key.replace(' ', '_')}_{q_num}_p{page_num+1}.png"
                            fitz_page = doc.load_page(page_num)
                            rect = fitz.Rect(crop_x0, crop_y0, crop_x1, crop_y1)
                            pix = fitz_page.get_pixmap(dpi=200, clip=rect)
                            pix.save(os.path.join(IMG_DIR, img_name))
                            diagram_path = f"/pdf_pages/{img_name}"
                    
                    # --- Option Validation Rules ---
                    needs_review = False
                    
                    # 1. Any of the four options is empty
                    if not opt1 or not opt2 or not opt3 or not opt4:
                        needs_review = True
                        
                    # 2. Correct option number missing or outside valid range (0-3)
                    if correct_idx < 0 or correct_idx > 3:
                        needs_review = True
                        
                    # 3. Same text copied into multiple options (duplicate strings)
                    opts_non_empty = [o for o in [opt1, opt2, opt3, opt4] if o]
                    if len(set(opts_non_empty)) < len(opts_non_empty) and len(opts_non_empty) > 1:
                        needs_review = True
                        
                    # 4. Adjacent options merged or exceptionally long? 
                    # If an option has > 10 words it might be merged
                    for opt in [opt1, opt2, opt3, opt4]:
                        if len(opt.split()) > 15:
                            needs_review = True
                            
                    # All diagrams must be reviewed
                    if has_diagram:
                        needs_review = True
                        
                    q_obj = {
                        "id": f"{subject_key.replace(' ', '')}_{q_num}_{page_num+1}",
                        "subject": subject,
                        "originalQuestionNumber": q_num,
                        "questionText": q_text,
                        "options": [opt1, opt2, opt3, opt4],
                        "correctAnswerIndex": correct_idx,
                        "sourcePdf": filename,
                        "sourcePage": page_num + 1,
                        "sourcePagePath": source_page_path,
                        "diagramPath": diagram_path,
                        "validationStatus": "needs_review" if needs_review else "verified",
                        "hasDiagram": has_diagram
                    }
                    all_results[subject].append(q_obj)

    # Save
    for subject, questions in all_results.items():
        unique_qs = []
        seen = set()
        for q in questions:
            if q['id'] not in seen:
                unique_qs.append(q)
                seen.add(q['id'])
                
        safe_name = subject.replace(' ', '_').replace('&', 'and').replace(',', '')
        with open(os.path.join(OUTPUT_DIR, f"{safe_name}.json"), "w", encoding="utf-8") as out:
            json.dump(unique_qs, out, indent=2)
            
        validation_reports[subject] = {
            "extracted": len(unique_qs),
            "four_options": len([q for q in unique_qs if all(q['options'])]),
            "verified_answer": len([q for q in unique_qs if q['correctAnswerIndex'] >= 0]),
            "diagrams": len([q for q in unique_qs if q['hasDiagram']]),
            "manual_review": len([q for q in unique_qs if q['validationStatus'] == 'needs_review']),
            "verified": len([q for q in unique_qs if q['validationStatus'] == 'verified'])
        }

    with open(os.path.join(OUTPUT_DIR, "validation_summary.json"), "w", encoding="utf-8") as out:
        json.dump(validation_reports, out, indent=2)
        
    with open(os.path.join(OUTPUT_DIR, "validation_report.md"), "w", encoding="utf-8") as md:
        md.write("# Source-to-Question Validation Report\n\n")
        for subj, report in validation_reports.items():
            md.write(f"## {subj}\n")
            md.write(f"- Questions extracted: {report['extracted']}\n")
            md.write(f"- 4 valid options: {report['four_options']}\n")
            md.write(f"- Verified answer index: {report['verified_answer']}\n")
            md.write(f"- Image/Diagram based: {report['diagrams']}\n")
            md.write(f"- Requires manual review: {report['manual_review']}\n")
            md.write(f"- Passed validation automatically: {report['verified']}\n\n")

if __name__ == "__main__":
    process_pdfs()
    print("Extraction complete.")
