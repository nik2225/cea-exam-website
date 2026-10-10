import pdfplumber
import os

PDF_DIR = r"C:\Users\Nikhil\OneDrive\Desktop\pwd test website\questionsssss"
test_pdf = os.path.join(PDF_DIR, "CEA_Maths_APM_Set_1.pdf")

with pdfplumber.open(test_pdf) as pdf:
    page = pdf.pages[0]
    # Try different table settings
    table = page.extract_table({
        "vertical_strategy": "text",
        "horizontal_strategy": "text"
    })
    
    if table:
        print("Found table with text strategy! Rows:", len(table))
        for row in table[:3]:
            print(row)
    else:
        print("No table found with text strategy.")
        
    text = page.extract_text(layout=True)
    print("\n--- RAW LAYOUT TEXT ---")
    print(text[:1000])
