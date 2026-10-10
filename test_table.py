import pdfplumber
import os

PDF_DIR = r"c:\Users\Nikhil\OneDrive\Desktop\pwd test website\source_pdfs"
filepath = os.path.join(PDF_DIR, "Sample Questions CEA - Surveying.PDF")

# We define vertical boundaries for the columns.
v_lines = [40, 70, 310, 365, 415, 465, 515, 580]

with pdfplumber.open(filepath) as pdf:
    for page in pdf.pages[1:3]: # test page 2 and 3
        # Extract table with explicit vertical lines
        tables = page.extract_tables({
            "vertical_strategy": "explicit",
            "explicit_vertical_lines": v_lines,
            "horizontal_strategy": "text"
        })
        
        with open("pdf_out_table_test.txt", "a", encoding="utf-8") as f:
            f.write(f"\n--- PAGE ---\n")
            if tables:
                for row in tables[0]:
                    f.write(str(row) + "\n")
