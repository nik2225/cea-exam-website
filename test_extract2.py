import json

TRANSCRIPT_PATH = r"C:\Users\Nikhil\.gemini\antigravity-ide\brain\c19c56ba-b38d-40be-befc-d31069eb2f12\.system_generated\logs\transcript_full.jsonl"

with open(TRANSCRIPT_PATH, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('type') == 'USER_INPUT':
                content = data.get('content', '')
                print("Found USER_INPUT. Length:", len(content))
                print("First 100 chars:", repr(content[:100]))
                if '==Start of PDF==' in content:
                    print("Found ==Start of PDF== in this block!")
        except Exception as e:
            pass
