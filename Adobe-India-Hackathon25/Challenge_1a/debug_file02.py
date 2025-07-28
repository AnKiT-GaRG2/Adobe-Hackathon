import fitz  # PyMuPDF
import os
import json
import re
from collections import Counter
from process_pdfs import *

def debug_file02():
    """Debug specific issues with file02.pdf heading extraction"""
    
    pdf_path = "sample_dataset/pdfs/file02.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    print("=== DEBUGGING FILE02.PDF ===")
    
    doc = fitz.open(pdf_path)
    text_elements = []

    # Collect text with font sizes and position information
    for page_num, page in enumerate(doc, start=1):
        page_height = page.rect.height
        page_width = page.rect.width
        blocks = page.get_text("dict")["blocks"]
        
        print(f"\n--- PAGE {page_num} ---")
        
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        raw_text = s["text"].strip()
                        if not raw_text:
                            continue
                            
                        normalized_text = normalize_unicode_characters(raw_text)
                        y_position = s["bbox"][1]
                        relative_y = y_position / page_height
                        x_position = s["bbox"][0]
                        relative_x = x_position / page_width
                        
                        element = {
                            "text": normalized_text,
                            "size": round(s["size"], 1),
                            "flags": s["flags"],
                            "page": page_num,
                            "y_position": y_position,
                            "relative_y": relative_y,
                            "x_position": x_position,
                            "relative_x": relative_x
                        }
                        
                        text_elements.append(element)
                        
                        # Debug output for page 4 where issues are
                        if page_num == 4:
                            is_bold = s["flags"] & 16
                            print(f"  Text: '{normalized_text}' | Size: {s['size']:.1f} | Bold: {bool(is_bold)} | Y: {y_position:.1f} | X: {x_position:.1f}")

    # Analyze font sizes
    sizes = [t["size"] for t in text_elements if len(t["text"]) > 3]
    most_common = Counter(sizes).most_common()
    body_text_size = most_common[0][0]
    unique_sizes = sorted(set(sizes), reverse=True)
    
    print(f"\n=== FONT ANALYSIS ===")
    print(f"Body text size: {body_text_size}")
    print(f"Font sizes (largest to smallest): {unique_sizes}")
    print(f"Font size distribution: {most_common}")

    # Detect table regions
    table_regions = detect_table_regions(text_elements)
    print(f"\n=== TABLE DETECTION ===")
    print(f"Detected {len(table_regions)} table regions")
    for i, table in enumerate(table_regions):
        print(f"  Table {i+1}: Page {table['page']}, Y-range: {table['y_start']:.1f}-{table['y_end']:.1f}")
        print(f"    Elements in table: {len(table['elements'])}")
        for elem in table['elements'][:5]:  # Show first 5 elements
            print(f"      '{elem['text']}' (Size: {elem['size']}, Y: {elem['y_position']:.1f})")
        if len(table['elements']) > 5:
            print(f"      ... and {len(table['elements']) - 5} more elements")

    # Focus on the problematic headings
    problematic_texts = [
        "Revision History Table of Contents",
        "Introduction to the Foundation Level Extensions Introduction to Foundation Level Agile Tester Extension",
        "Overview of the Foundation Level Extension",
        "Agile Tester Syllabus"
    ]
    
    print(f"\n=== ANALYZING PROBLEMATIC HEADINGS ===")
    for prob_text in problematic_texts:
        print(f"\nAnalyzing: '{prob_text}'")
        
        # Find elements that contain this text
        matching_elements = []
        for elem in text_elements:
            if prob_text.lower() in elem["text"].lower() or elem["text"].lower() in prob_text.lower():
                matching_elements.append(elem)
                
        print(f"  Found {len(matching_elements)} matching elements:")
        for elem in matching_elements:
            is_bold = elem["flags"] & 16
            print(f"    Page {elem['page']}: '{elem['text']}' | Size: {elem['size']:.1f} | Bold: {bool(is_bold)} | Y: {elem['y_position']:.1f}")
            
            # Check if it's in a table
            in_table = is_text_in_table(elem, table_regions)
            print(f"      In table: {in_table}")
            
            # Check various filters
            is_date = contains_date(elem["text"])
            is_form = is_form_field_or_generic_term(elem["text"])
            print(f"      Is date: {is_date}, Is form field: {is_form}")

    # Show the actual extraction result
    print(f"\n=== ACTUAL EXTRACTION RESULT ===")
    result = extract_outline(pdf_path)
    print(f"Title: {result['title']}")
    print(f"Outline ({len(result['outline'])} items):")
    for item in result['outline']:
        print(f"  {item['level']}: {item['text']} (Page {item['page']})")

if __name__ == "__main__":
    debug_file02()
