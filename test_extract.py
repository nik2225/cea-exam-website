import json
import re

TRANSCRIPT_PATH = r"C:\Users\Nikhil\.gemini\antigravity-ide\brain\c19c56ba-b38d-40be-befc-d31069eb2f12\.system_generated\logs\transcript_full.jsonl"

with open(TRANSCRIPT_PATH, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('type') == 'USER_INPUT':
                content = data.get('content', '')
                if '==Start of PDF==' in content:
                    print("Found prompt! Length:", len(content))
                    # Check first block
                    pdf_blocks = re.split(r'==Start of PDF==', content)[1:]
                    print("Found", len(pdf_blocks), "PDF blocks.")
                    if len(pdf_blocks) > 0:
                        ocr_blocks = re.findall(r'==Start of OCR for page \d+==\n(.*?)==End of OCR for page \d+==', pdf_blocks[0], re.DOTALL)
                        print("Found", len(ocr_blocks), "OCR blocks in first PDF.")
                    break
        except Exception as e:
            pass
