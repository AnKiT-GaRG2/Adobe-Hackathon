import fitz
import re
from collections import Counter

# Check if Summary is in a table in file03.pdf
pdf_path = 'sample_dataset/pdfs/file03.pdf'
doc = fitz.open(pdf_path)

print('=== TABLE DETECTION FOR SUMMARY ===')

# Import the table detection functions from process_pdfs
import sys
sys.path.append('.')
from process_pdfs import detect_table_regions, is_text_in_table

all_text_elements = []

# Extract all text elements like in process_pdfs.py
for page_num, page in enumerate(doc, start=1):
    page_height = page.rect.height
    page_width = page.rect.width
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if "lines" in b:
            for l in b["lines"]:
                for s in l["spans"]:
                    raw_text = s["text"].strip()
                    if raw_text:
                        y_position = s["bbox"][1]
                        relative_y = y_position / page_height
                        x_position = s["bbox"][0]
                        relative_x = x_position / page_width
                        
                        all_text_elements.append({
                            "text": raw_text,
                            "size": round(s["size"], 1),
                            "flags": s["flags"],
                            "page": page_num,
                            "y_position": y_position,
                            "relative_y": relative_y,
                            "x_position": x_position,
                            "relative_x": relative_x
                        })

# Run table detection
table_regions = detect_table_regions(all_text_elements)

print(f'Total table regions detected: {len(table_regions)}')
for i, table in enumerate(table_regions):
    print(f'Table {i+1}: Page {table["page"]}, Y-range: {table["y_start"]:.1f}-{table["y_end"]:.1f}')

# Find Summary element
summary_element = None
for elem in all_text_elements:
    if elem["text"].strip().lower() == "summary":
        summary_element = elem
        break

if summary_element:
    print(f'\nSummary element found:')
    print(f'  Text: "{summary_element["text"]}"')
    print(f'  Page: {summary_element["page"]}')
    print(f'  Y-position: {summary_element["y_position"]:.1f}')
    print(f'  X-position: {summary_element["x_position"]:.1f}')
    
    # Check if Summary is in any table
    in_table = is_text_in_table(summary_element, table_regions)
    print(f'  Is in table: {in_table}')
    
    if in_table:
        print(f'  *** SUMMARY IS BEING FILTERED OUT DUE TO TABLE DETECTION ***')
        
        # Find which table it's in
        for i, table in enumerate(table_regions):
            if (summary_element["page"] == table["page"] and
                table["y_start"] <= summary_element["y_position"] <= table["y_end"]):
                print(f'  Summary is in Table {i+1}')
                print(f'    Table Y-range: {table["y_start"]:.1f}-{table["y_end"]:.1f}')
                print(f'    Summary Y-position: {summary_element["y_position"]:.1f}')
    else:
        print(f'  Summary is NOT in a table')

else:
    print('Summary element not found!')
