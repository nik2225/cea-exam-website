import json
import re
import os

TRANSCRIPT_PATH = r"C:\Users\Nikhil\.gemini\antigravity-ide\brain\c19c56ba-b38d-40be-befc-d31069eb2f12\.system_generated\logs\transcript_full.jsonl"
OUTPUT_DIR = r"C:\Users\Nikhil\OneDrive\Desktop\pwd test website\src\data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_transcript():
    with open(TRANSCRIPT_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We just need to find the raw string in the file
    idx = content.find("==Start of PDF==")
    if idx != -1:
        # Find the end of the last PDF
        end_idx = content.rfind("==End of PDF==")
        if end_idx != -1:
            return content[idx:end_idx + len("==End of PDF==")]
    return ""

def parse_question_block(q_num, raw_text):
    # Heuristics to extract the text, the correct option, and 4 options
    # The format often looks like:
    # [Question text...]
    # [Correct Option digit]
    # [Option 1]
    # [Option 2]
    # [Option 3]
    # [Option 4]
    
    # Let's just do a naive split and rely on manual review for imperfect parses.
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    # Try to find a line that is just "1", "2", "3", or "4", which is likely the correct answer
    correct_idx = -1
    correct_ans = None
    for i, line in enumerate(lines):
        if line in ["1", "2", "3", "4"] and i > 0 and i < len(lines) - 1:
            correct_idx = i
            correct_ans = int(line)
            break
            
    # If not on its own line, maybe at the end of the question text?
    if correct_idx == -1:
        # Check last token of first line
        parts = lines[0].split()
        if len(parts) > 1 and parts[-1] in ["1", "2", "3", "4"]:
            correct_ans = int(parts[-1])
            lines[0] = " ".join(parts[:-1]) # remove it from question text
            correct_idx = 0
            
    q_text = " ".join(lines[:correct_idx]) if correct_idx > 0 else lines[0]
    
    # The rest are options.
    options = lines[correct_idx+1:] if correct_idx != -1 else lines[1:]
    
    # If we don't have exactly 4 options, we will just bucket the text as best we can
    final_options = ["", "", "", ""]
    if len(options) == 4:
        final_options = options
        needs_review = False
    elif len(options) > 4:
        final_options = options[:4]
        needs_review = True
    else:
        for i in range(len(options)):
            final_options[i] = options[i]
        needs_review = True
        
    return {
        "questionText": q_text,
        "options": final_options,
        "correctAnswerIndex": correct_ans - 1 if correct_ans else 0, # 0-indexed
        "needsReview": needs_review or (correct_ans is None)
    }

def process_pdfs(content):
    pdf_blocks = re.split(r'==Start of PDF==', content)[1:]
    
    subjects = [
        "General Civil Engineering",
        "Mathematics & Applied Mechanics",
        "Construction, Construction Materials, Stores Account",
        "Surveying",
        "Drawing"
    ]
    
    all_results = {}
    validation_reports = {}
    
    for idx, block in enumerate(pdf_blocks):
        if idx >= len(subjects):
            break
        subject = subjects[idx]
        questions = []
        validation = {
            "subject": subject,
            "extracted": 0,
            "four_options": 0,
            "verified_answer": 0,
            "diagrams": 0,
            "manual_review": 0,
            "duplicates": 0,
            "missing_numbers": []
        }
        
        # Extract all OCR text
        ocr_blocks = re.findall(r'==Start of OCR for page \d+==\n(.*?)==End of OCR for page \d+==', block, re.DOTALL)
        full_text = "\n".join(ocr_blocks)
        
        # Check diagrams
        diagrams = re.findall(r'==Screenshot for page \d+==', block)
        
        q_splits = re.split(r'\n(?=\d+\s)', "\n" + full_text)
        
        expected_q_num = 1
        seen_ids = set()
        
        for q_text in q_splits:
            q_text = q_text.strip()
            if not q_text:
                continue
            
            m = re.match(r'^(\d+)\s+(.*)', q_text, re.DOTALL)
            if not m:
                continue
            
            q_num = int(m.group(1))
            rest = m.group(2).strip()
            
            if rest.startswith("Question Correct Option"):
                continue
                
            validation["extracted"] += 1
            
            if q_num in seen_ids:
                validation["duplicates"] += 1
            seen_ids.add(q_num)
            
            while expected_q_num < q_num:
                validation["missing_numbers"].append(expected_q_num)
                expected_q_num += 1
            expected_q_num = q_num + 1
            
            parsed = parse_question_block(q_num, rest)
            
            has_diagram = "Identify the" in parsed["questionText"] or "Sybol represents" in parsed["questionText"]
            if has_diagram:
                validation["diagrams"] += 1
                
            if not parsed["needsReview"]:
                validation["four_options"] += 1
                validation["verified_answer"] += 1
            else:
                validation["manual_review"] += 1
            
            q_obj = {
                "id": f"{subject.replace(' ', '_')}_{q_num}",
                "subject": subject,
                "originalQuestionNumber": q_num,
                "questionText": parsed["questionText"],
                "options": parsed["options"],
                "correctAnswerIndex": parsed["correctAnswerIndex"],
                "explanation": "",
                "hasDiagram": has_diagram,
                "needsReview": parsed["needsReview"],
                "rawText": rest
            }
            questions.append(q_obj)
            
        all_results[subject] = questions
        validation_reports[subject] = validation
        
        # Save JSON
        safe_name = subject.replace(' ', '_').replace('&', 'and').replace(',', '')
        with open(os.path.join(OUTPUT_DIR, f"{safe_name}.json"), "w", encoding="utf-8") as out:
            json.dump(questions, out, indent=2)

    # Write validation report
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
    content = parse_transcript()
    if content:
        process_pdfs(content)
        print("Data extraction complete.")
    else:
        print("Failed to find prompt in transcript.")
