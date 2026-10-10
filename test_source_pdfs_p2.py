import pdfplumber
import os

PDF_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\source_pdfs"

for filename in os.listdir(PDF_DIR):
    if not filename.lower().endswith(".pdf"): continue
    filepath = os.path.join(PDF_DIR, filename)
    
    with pdfplumber.open(filepath) as pdf:
        if len(pdf.pages) > 1:
            page = pdf.pages[1]
            
            with open("pdf_out_p2.txt", "a", encoding="utf-8") as f:
                f.write(f"\n\n{'='*40}\nFile: {filename}\n{'='*40}\n")
                
                # Try table
                tables = page.extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text"})
                if tables:
                    f.write("--- TABLE ---\n")
                    for row in tables[0][:5]:
                        f.write(str(row) + "\n")
                else:
                    f.write("--- TEXT ---\n")
                    text = page.extract_text(layout=True)
                    f.write(text[:1000] if text else "No text found")
