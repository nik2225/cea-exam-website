import pdfplumber
import os

PDF_DIR = r"C:\Users\Nikhil\OneDrive\Desktop\pwd test website\questionsssss"

for filename in ["CEA_Surveying_Set_1.pdf", "CEA_GCE_Set_1.pdf"]:
    print(f"\n\n--- {filename} ---")
    with pdfplumber.open(os.path.join(PDF_DIR, filename)) as pdf:
        text = pdf.pages[0].extract_text()
        print(text[:1500])
