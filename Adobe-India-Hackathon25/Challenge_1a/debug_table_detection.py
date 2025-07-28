#!/usr/bin/env python3
"""
Debug script to analyze table detection for file01.pdf
This will help understand why table content is being detected as headings
"""

import fitz  # PyMuPDF
import re
from collections import defaultdict

def extract_text_elements(pdf_path):
    """Extract all text elements with their properties"""
    text_elements = []
    doc = fitz.open(pdf_path)
    
    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("dict")
        
        for block in blocks["blocks"]:
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                for span in line["spans"]:
                    if span["text"].strip():
                        element = {
                            "page": page_num,
                            "text": span["text"],
                            "x_position": span["bbox"][0],
                            "y_position": span["bbox"][1],
                            "size": span["size"],
                            "flags": span["flags"],
                            "font": span["font"],
                            "relative_x": span["bbox"][0] / page.rect.width if page.rect.width > 0 else 0
                        }
                        text_elements.append(element)
    
    doc.close()
    return text_elements

def group_elements_into_rows(elements, y_threshold=3):
    """Group text elements into rows based on Y-coordinate proximity"""
    if not elements:
        return []
    
    # Sort by page and Y position
    sorted_elements = sorted(elements, key=lambda x: (x["page"], x["y_position"]))
    
    rows = []
    current_row = [sorted_elements[0]]
    current_y = sorted_elements[0]["y_position"]
    
    for element in sorted_elements[1:]:
        if abs(element["y_position"] - current_y) <= y_threshold:
            current_row.append(element)
        else:
            if current_row:
                rows.append(sorted(current_row, key=lambda x: x["x_position"]))
            current_row = [element]
            current_y = element["y_position"]
    
    if current_row:
        rows.append(sorted(current_row, key=lambda x: x["x_position"]))
    
    return rows

def is_table_row(row, context_rows=None):
    """
    Check if a row shows table characteristics
    """
    if not row or len(row) < 2:
        return False
    
    # Check for multiple columns (elements with reasonable spacing)
    x_positions = [elem["x_position"] for elem in row]
    x_positions.sort()
    
    # Look for consistent spacing that suggests columns
    column_gaps = []
    for i in range(1, len(x_positions)):
        gap = x_positions[i] - x_positions[i-1]
        if gap > 20:  # Minimum gap to consider separate columns
            column_gaps.append(gap)
    
    if len(column_gaps) < 1:  # Need at least 2 columns
        return False
    
    # Check for table-like content
    table_content_indicators = 0
    total_elements = len(row)
    
    for elem in row:
        text = elem["text"].strip()
        
        # Form field indicators
        if any(indicator in text.lower() for indicator in [
            'name', 'date', 'designation', 'service', 'pay', 'whether', 'concession',
            'relationship', 'address', 'phone', 'email', 'signature'
        ]):
            table_content_indicators += 2
        
        # Short text (typical in tables)
        elif len(text.split()) <= 3:
            table_content_indicators += 1
        
        # Numbers or codes
        elif re.match(r'^[\d\.\-\+]+$', text) or re.match(r'^[A-Z]{1,3}\d*$', text):
            table_content_indicators += 1
        
        # Colon endings (form labels)
        elif text.endswith(':'):
            table_content_indicators += 1
    
    # If more than 60% of elements show table characteristics, consider it a table row
    return (table_content_indicators / total_elements) > 0.6

def analyze_table_detection(pdf_path):
    """Analyze table detection for the given PDF"""
    print(f"\n=== Table Detection Analysis for {pdf_path} ===")
    
    # Extract text elements
    elements = extract_text_elements(pdf_path)
    print(f"Total text elements: {len(elements)}")
    
    # Group into rows
    all_rows = []
    for page_num in range(1, max(elem["page"] for elem in elements) + 1):
        page_elements = [elem for elem in elements if elem["page"] == page_num]
        page_rows = group_elements_into_rows(page_elements)
        all_rows.extend([(page_num, i, row) for i, row in enumerate(page_rows)])
    
    print(f"Total rows: {len(all_rows)}")
    
    # Analyze each row
    table_rows = []
    for page_num, row_idx, row in all_rows:
        if is_table_row(row):
            table_rows.append((page_num, row_idx, row))
    
    print(f"Detected table rows: {len(table_rows)}")
    
    # Show the problematic heading
    problematic_text = "Designation Service PAY + SI + NPA Whether the concession is to be availed for a) If the concession is to visit anywhere in shortest route. Persons in respect of whom LTC is proposed to be availed. Relationship"
    
    print(f"\n=== Analyzing Problematic 'Heading' ===")
    print(f"Text: {problematic_text[:100]}...")
    
    # Find elements that match parts of this text
    matching_elements = []
    for elem in elements:
        if any(word in elem["text"] for word in ["Designation", "Service", "PAY", "concession", "Relationship"]):
            matching_elements.append(elem)
    
    print(f"\nFound {len(matching_elements)} elements containing key words:")
    for elem in matching_elements:
        print(f"  Page {elem['page']}: '{elem['text']}' (size: {elem['size']}, bold: {bool(elem['flags'] & 16)}, y: {elem['y_position']:.1f})")
    
    # Group these elements by Y position to see if they form rows
    if matching_elements:
        rows_with_matches = group_elements_into_rows(matching_elements)
        print(f"\nThese elements form {len(rows_with_matches)} rows:")
        for i, row in enumerate(rows_with_matches):
            print(f"  Row {i+1}: {len(row)} elements")
            for elem in row:
                print(f"    '{elem['text']}' (x: {elem['x_position']:.1f}, y: {elem['y_position']:.1f})")
            
            # Check if this row would be detected as a table row
            is_table = is_table_row(row)
            print(f"    -> Is table row: {is_table}")
    
    # Show detected table regions
    if table_rows:
        print(f"\n=== Detected Table Regions ===")
        
        # Group consecutive table rows into table regions
        page_table_groups = defaultdict(list)
        for page_num, row_idx, row in table_rows:
            page_table_groups[page_num].append((row_idx, row))
        
        for page_num, page_tables in page_table_groups.items():
            page_tables.sort(key=lambda x: x[0])  # Sort by row index
            
            current_table_start = None
            current_table_rows = []
            
            for row_idx, row in page_tables:
                if current_table_start is None:
                    current_table_start = row_idx
                    current_table_rows = [row]
                elif row_idx == current_table_start + len(current_table_rows):  # Consecutive row
                    current_table_rows.append(row)
                else:
                    # End of current table, start new one
                    if len(current_table_rows) >= 3:  # Require at least 3 consecutive rows
                        print(f"Table on page {page_num}: rows {current_table_start} to {current_table_start + len(current_table_rows) - 1}")
                        for i, table_row in enumerate(current_table_rows):
                            print(f"  Row {i+1}: {[elem['text'][:20] + '...' if len(elem['text']) > 20 else elem['text'] for elem in table_row]}")
                    
                    current_table_start = row_idx
                    current_table_rows = [row]
            
            # Handle last table
            if current_table_rows and len(current_table_rows) >= 3:
                print(f"Table on page {page_num}: rows {current_table_start} to {current_table_start + len(current_table_rows) - 1}")
                for i, table_row in enumerate(current_table_rows):
                    print(f"  Row {i+1}: {[elem['text'][:20] + '...' if len(elem['text']) > 20 else elem['text'] for elem in table_row]}")
    else:
        print("\nNo table regions detected!")

if __name__ == "__main__":
    pdf_path = "sample_dataset/pdfs/file01.pdf"
    analyze_table_detection(pdf_path)
