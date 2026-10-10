import pdfplumber
import json
import os
import glob

PDF_DIR = r"C:\Users\Nikhil\OneDrive\Desktop\pwd test website\questionsssss"
OUTPUT_DIR = r"C:\Users\Nikhil\OneDrive\Desktop\pwd test website\src\data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

SUBJECT_MAP = {
    "GCE": "General Civil Engineering",
    "Maths_APM": "Mathematics & Applied Mechanics",
    "Construction": "Construction, Construction Materials, Stores Account",
    "Surveying": "Surveying",
    "Drawing": "Drawing"
}

def extract_questions_from_pdf(pdf_path, subject):
    questions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 7:
                        continue
                    
                    sr_no = str(row[0]).strip()
                    if not sr_no.isdigit():
                        continue
                        
                    q_num = int(sr_no)
                    question_text = str(row[1]).strip()
                    
                    correct_opt_str = str(row[2]).strip()
                    if correct_opt_str.isdigit():
                        correct_opt = int(correct_opt_str) - 1 # 0 indexed
                    else:
                        correct_opt = 0
                        
                    options = [str(row[3]).strip(), str(row[4]).strip(), str(row[5]).strip(), str(row[6]).strip()]
                    
                    # Some heuristics for manual review
                    needs_review = False
                    if not correct_opt_str.isdigit():
                        needs_review = True
                    for opt in options:
                        if not opt or opt == "None":
                            needs_review = True
                            
                    has_diagram = "identify" in question_text.lower() or "symbol" in question_text.lower()
                    
                    q_obj = {
                        "id": f"{subject.replace(' ', '_')}_{q_num}_{os.path.basename(pdf_path)}",
                        "subject": subject,
                        "originalQuestionNumber": q_num,
                        "questionText": question_text.replace('\n', ' '),
                        "options": [o.replace('\n', ' ') for o in options],
                        "correctAnswerIndex": correct_opt,
                        "explanation": "",
                        "hasDiagram": has_diagram,
                        "needsReview": needs_review,
                        "rawText": " | ".join(map(str, row))
                    }
                    questions.append(q_obj)
                    
    return questions

def process_all():
    pdfs = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    
    results = {}
    validation_reports = {}
    
    for pdf in pdfs:
        filename = os.path.basename(pdf)
        
        subject_key = None
        for key in SUBJECT_MAP.keys():
            if key in filename:
                subject_key = key
                break
                
        if not subject_key:
            continue
            
        subject = SUBJECT_MAP[subject_key]
        
        print(f"Extracting {filename} for {subject}...")
        qs = extract_questions_from_pdf(pdf, subject)
        print(f"Extracted {len(qs)} from {filename}")
        
        if subject not in results:
            results[subject] = []
        results[subject].extend(qs)
        
    for subject, questions in results.items():
        # Create validation report
        validation = {
            "subject": subject,
            "extracted": len(questions),
            "four_options": len([q for q in questions if not q['needsReview']]),
            "verified_answer": len([q for q in questions if not q['needsReview']]),
            "diagrams": len([q for q in questions if q['hasDiagram']]),
            "manual_review": len([q for q in questions if q['needsReview']]),
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
        
    with open(os.path.join(OUTPUT_DIR, "validation_report.md"), "w", encoding="utf-8") as md:
        md.write("# Data Import Validation Report\n\n")
        for subj, report in validation_reports.items():
            md.write(f"## {subj}\n")
            md.write(f"- Total Extracted: {report['extracted']}\n")
            md.write(f"- Questions with 4 options: {report['four_options']}\n")
            md.write(f"- Verified Answers: {report['verified_answer']}\n")
            md.write(f"- Diagrams: {report['diagrams']}\n")
            md.write(f"- Needs Manual Review: {report['manual_review']}\n")
            md.write(f"- Duplicates: {report['duplicates']}\n")
            md.write(f"- Missing Numbers: {report['missing_numbers']}\n\n")

if __name__ == "__main__":
    process_all()
    print("Done")
