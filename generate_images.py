import fitz # PyMuPDF
import pdfplumber
import os
import json
import re
import glob

PDF_DIR = r"C:\Users\Nikhil\OneDrive\Desktop\pwd test website\questionsssss"
OUTPUT_DIR = r"C:\Users\Nikhil\OneDrive\Desktop\pwd test website\src\data"
IMG_DIR = r"C:\Users\Nikhil\OneDrive\Desktop\pwd test website\public\pdf_pages"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

SUBJECT_MAP = {
    "GCE": "General Civil Engineering",
    "Maths_APM": "Mathematics & Applied Mechanics",
    "Construction": "Construction, Construction Materials, Stores Account",
    "Surveying": "Surveying",
    "Drawing": "Drawing"
}

def clean_text(text):
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

def process_pdfs():
    pdfs = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    all_results = {}
    validation_reports = {}

    for pdf_path in pdfs:
        filename = os.path.basename(pdf_path)
        subject_key = next((k for k in SUBJECT_MAP if k in filename), None)
        if not subject_key: continue
        subject = SUBJECT_MAP[subject_key]
        
        print(f"Processing {filename}...")
        
        if subject not in all_results:
            all_results[subject] = []
            
        # We will parse page by page to keep page numbers tight
        doc = fitz.open(pdf_path)
        with pdfplumber.open(pdf_path) as pb_pdf:
            for page_num in range(len(doc)):
                # 1. Render Page Image
                fitz_page = doc.load_page(page_num)
                pix = fitz_page.get_pixmap(dpi=150)
                img_name = f"{subject_key}_{filename.replace('.pdf', '')}_p{page_num+1}.png"
                pix.save(os.path.join(IMG_DIR, img_name))
                
                # 2. Extract Text / Table
                pb_page = pb_pdf.pages[page_num]
                
                # Try table extraction first (for Surveying)
                tables = pb_page.extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text"})
                
                extracted_qs = []
                
                if tables and len(tables[0]) > 2:
                    # Likely Surveying format
                    for table in tables:
                        for row in table:
                            if not row or len(row) < 5: continue
                            sr_no = str(row[0]).strip()
                            if not sr_no.isdigit(): continue
                            
                            q_text = clean_text(str(row[1]))
                            options = [clean_text(str(o)) for o in row[2:6]]
                            while len(options) < 4: options.append("")
                            options = options[:4]
                            
                            # Surveying has NO answer key in the table, it says "No answer key"
                            # We will store it for manual validation
                            extracted_qs.append({
                                "id": f"{subject_key}_{sr_no}_{page_num+1}",
                                "subject": subject,
                                "originalQuestionNumber": int(sr_no),
                                "questionText": q_text,
                                "options": options,
                                "correctAnswerIndex": 0, # Needs Review
                                "sourcePdf": filename,
                                "sourcePage": page_num + 1,
                                "diagramPath": f"/pdf_pages/{img_name}",
                                "validationStatus": "needs_review",
                                "rawText": " | ".join([str(c) for c in row])
                            })
                else:
                    # Text format (GCE, Math)
                    text = pb_page.extract_text(layout=True)
                    # Use regex to find question blocks starting with a number and a dot
                    # e.g., "1. Question..."
                    q_blocks = re.split(r'\n\s*(\d+)\.\s+', "\n" + text)
                    
                    if len(q_blocks) > 2:
                        for i in range(1, len(q_blocks), 2):
                            q_num = int(q_blocks[i])
                            q_text_raw = q_blocks[i+1]
                            
                            # Try to extract options A, B, C, D
                            # We'll split by lines and look for A., B., C., D.
                            lines = [ln.strip() for ln in q_text_raw.split('\n') if ln.strip()]
                            
                            q_text_lines = []
                            options = ["", "", "", ""]
                            correct_opt = 0
                            
                            for ln in lines:
                                if re.match(r'^A\.', ln): options[0] = ln[2:].strip()
                                elif re.match(r'^B\.', ln): options[1] = ln[2:].strip()
                                elif re.match(r'^C\.', ln): options[2] = ln[2:].strip()
                                elif re.match(r'^D\.', ln): options[3] = ln[2:].strip()
                                elif "Correct Option:" in ln:
                                    m = re.search(r'Correct Option:\s*(\d)', ln)
                                    if m:
                                        correct_opt = int(m.group(1)) - 1
                                else:
                                    # If it doesn't match an option, it's part of the question text
                                    if not options[0]: # only if we haven't hit A yet
                                        q_text_lines.append(ln)
                            
                            extracted_qs.append({
                                "id": f"{subject_key}_{q_num}_{page_num+1}",
                                "subject": subject,
                                "originalQuestionNumber": q_num,
                                "questionText": clean_text(" ".join(q_text_lines)),
                                "options": options,
                                "correctAnswerIndex": max(0, correct_opt),
                                "sourcePdf": filename,
                                "sourcePage": page_num + 1,
                                "diagramPath": f"/pdf_pages/{img_name}",
                                "validationStatus": "needs_review",
                                "rawText": q_text_raw
                            })
                
                all_results[subject].extend(extracted_qs)

    # Save to JSON
    for subject, questions in all_results.items():
        # Clean up duplicates
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
            "subject": subject,
            "extracted": len(unique_qs),
            "manual_review": len([q for q in unique_qs if q['validationStatus'] == 'needs_review']),
            "verified": len([q for q in unique_qs if q['validationStatus'] == 'verified'])
        }

    with open(os.path.join(OUTPUT_DIR, "validation_summary.json"), "w", encoding="utf-8") as out:
        json.dump(validation_reports, out, indent=2)

if __name__ == "__main__":
    process_pdfs()
    print("Done generating images and base JSON data.")
