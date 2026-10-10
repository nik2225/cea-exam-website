import pdfplumber
import json
import os
import glob
import re

PDF_DIR = r"C:\Users\Nikhil\OneDrive\Desktop\pwd test website\questionsssss"
OUTPUT_DIR = r"C:\Users\Nikhil\OneDrive\Desktop\pwd test website\src\data"

SUBJECT_MAP = {
    "GCE": "General Civil Engineering",
    "Maths_APM": "Mathematics & Applied Mechanics",
    "Construction": "Construction, Construction Materials, Stores Account",
    "Surveying": "Surveying",
    "Drawing": "Drawing"
}

def extract_questions(pdf_path, subject):
    questions = []
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text(layout=True) + "\n"
            
    # Heuristic parsing for text
    # The format seems to be tabular:
    # 1. Question Text...
    # Correct Option ...
    # Option 1 ...
    # We will try our best, but mark as needsReview=True
    
    # Just split by numbers at the start of a line
    q_splits = re.split(r'\n\s*(\d+)\s+', "\n" + text)
    
    if len(q_splits) > 2:
        for i in range(1, len(q_splits), 2):
            q_num = int(q_splits[i])
            q_text_raw = q_splits[i+1].strip()
            
            # Very naive split
            parts = [p.strip() for p in q_text_raw.split('\n') if p.strip()]
            q_text = parts[0] if parts else ""
            options = ["Option A", "Option B", "Option C", "Option D"]
            if len(parts) >= 5:
                options = parts[-4:]
                
            questions.append({
                "id": f"{subject.replace(' ', '_')}_{q_num}",
                "subject": subject,
                "originalQuestionNumber": q_num,
                "questionText": q_text,
                "options": options,
                "correctAnswerIndex": 0,
                "explanation": "",
                "hasDiagram": False,
                "needsReview": True,
                "rawText": q_text_raw
            })
            
    return questions

def process_all():
    pdfs = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    results = {}
    validation_reports = {}
    
    for pdf in pdfs:
        filename = os.path.basename(pdf)
        subject_key = next((k for k in SUBJECT_MAP if k in filename), None)
        if not subject_key: continue
        
        subject = SUBJECT_MAP[subject_key]
        qs = extract_questions(pdf, subject)
        
        if subject not in results:
            results[subject] = []
        results[subject].extend(qs)
        
    for subject, questions in results.items():
        validation = {
            "subject": subject,
            "extracted": len(questions),
            "four_options": 0,
            "verified_answer": 0,
            "diagrams": 0,
            "manual_review": len(questions),
            "duplicates": 0,
            "missing_numbers": []
        }
        
        seen_ids = set()
        for q in questions:
            if q['originalQuestionNumber'] in seen_ids:
                validation['duplicates'] += 1
            seen_ids.add(q['originalQuestionNumber'])
            
        validation_reports[subject] = validation
        
        safe_name = subject.replace(' ', '_').replace('&', 'and').replace(',', '')
        with open(os.path.join(OUTPUT_DIR, f"{safe_name}.json"), "w", encoding="utf-8") as out:
            json.dump(questions, out, indent=2)

    with open(os.path.join(OUTPUT_DIR, "validation_report.json"), "w", encoding="utf-8") as vr:
        json.dump(validation_reports, vr, indent=2)

if __name__ == "__main__":
    process_all()
    print("Done")
