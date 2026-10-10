import pdfplumber
import os

PDF_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\source_pdfs"

for filename in os.listdir(PDF_DIR):
    if not filename.lower().endswith(".pdf"): continue
    filepath = os.path.join(PDF_DIR, filename)
    print(f"\n\n{'='*40}\nFile: {filename}\n{'='*40}")
    
    with pdfplumber.open(filepath) as pdf:
        if len(pdf.pages) > 0:
            page = pdf.pages[0]
            
            with open("pdf_out.txt", "a", encoding="utf-8") as f:
                f.write(f"\n\n{'='*40}\nFile: {filename}\n{'='*40}\n")
                
                # Print some text layout
                text = page.extract_text(layout=True)
                f.write("--- TEXT ---\n")
                f.write(text[:1000] if text else "No text found")
                
                # Print table check
                tables = page.extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text"})
                if tables:
                    f.write("\n--- TABLES FOUND ---\n")
                    for row in tables[0][:3]:
                        f.write(str(row) + "\n")
