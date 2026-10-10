import fitz # PyMuPDF
import pdfplumber
import os
import json
import re
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

def clean_text(text):
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

def process_pdfs():
    pdfs = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    all_results = {}
    validation_reports = {}

    for pdf_path in pdfs:
        filename = os.path.basename(pdf_path)
        subject_key = next((k for k in SUBJECT_MAP if k.lower() in filename.lower()), None)
        if not subject_key: 
            print(f"Unknown subject for {filename}")
            continue
            
        subject = SUBJECT_MAP[subject_key]
        print(f"Processing {filename} ({subject})...")
        
        if subject not in all_results:
            all_results[subject] = []
            
        doc = fitz.open(pdf_path)
        with pdfplumber.open(pdf_path) as pb_pdf:
            # Stats for this PDF
            total_extracted = 0
            has_four_options = 0
            diagrams_detected = 0
            
            for page_num in range(len(doc)):
                # 1. Render Page Image
                fitz_page = doc.load_page(page_num)
                pix = fitz_page.get_pixmap(dpi=150)
                img_name = f"{subject_key.replace(' ', '_')}_p{page_num+1}.png"
                pix.save(os.path.join(IMG_DIR, img_name))
                
                # 2. Extract Text using layout
                pb_page = pb_pdf.pages[page_num]
                text = pb_page.extract_text(layout=True)
                if not text: continue
                
                # Split by newline + digits + space (handles "12 What is...", " 12 What is...")
                q_blocks = re.split(r'\n\s*(\d+)\s+', "\n" + text)
                
                if len(q_blocks) > 2:
                    for i in range(1, len(q_blocks), 2):
                        q_num_str = q_blocks[i]
                        if not q_num_str.isdigit(): continue
                        q_num = int(q_num_str)
                        
                        q_text_raw = q_blocks[i+1]
                        
                        # Just store the raw block as questionText for now, it's safer than guessing wrong.
                        # The admin will verify it. We try our best to guess options.
                        lines = [ln.strip() for ln in q_text_raw.split('\n') if ln.strip()]
                        
                        options = ["", "", "", ""]
                        correct_opt = 0
                        has_diagram = "identify" in q_text_raw.lower() or "symbol" in q_text_raw.lower() or "figure" in q_text_raw.lower()
                        
                        if has_diagram: diagrams_detected += 1
                        
                        extracted_qs = {
                            "id": f"{subject_key.replace(' ', '')}_{q_num}_{page_num+1}",
                            "subject": subject,
                            "originalQuestionNumber": q_num,
                            "questionText": clean_text(" ".join(lines)), # Dump everything into question text
                            "options": options,
                            "correctAnswerIndex": correct_opt,
                            "sourcePdf": filename,
                            "sourcePage": page_num + 1,
                            "diagramPath": f"/pdf_pages/{img_name}",
                            "validationStatus": "needs_review",
                            "hasDiagram": has_diagram,
                            "rawText": q_text_raw
                        }
                        
                        all_results[subject].append(extracted_qs)
                        total_extracted += 1

    # Save to JSON
    for subject, questions in all_results.items():
        # Clean duplicates
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
            "manual_review": len(unique_qs),
            "verified": 0
        }

    with open(os.path.join(OUTPUT_DIR, "validation_summary.json"), "w", encoding="utf-8") as out:
        json.dump(validation_reports, out, indent=2)
        
    # Generate Validation Report MD
    with open(os.path.join(OUTPUT_DIR, "validation_report.md"), "w", encoding="utf-8") as md:
        md.write("# Source-to-Question Validation Report\n\n")
        for subj, report in validation_reports.items():
            md.write(f"## {subj}\n")
            md.write(f"- Questions extracted (requires review): {report['extracted']}\n")
            md.write(f"- Verified: {report['verified']}\n\n")

if __name__ == "__main__":
    process_pdfs()
    print("Extraction complete.")
