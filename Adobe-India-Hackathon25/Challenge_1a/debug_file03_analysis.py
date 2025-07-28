import fitz
import json
import re
from collections import Counter

def debug_file03_heading_detection():
    """Debug why Background and Summary headings are not being detected in file03.pdf"""
    
    pdf_path = 'sample_dataset/pdfs/file03.pdf'
    doc = fitz.open(pdf_path)
    
    print("=== DEBUGGING FILE03 HEADING DETECTION ===\n")
    
    # Extract all text elements with their properties
    text_elements = []
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
                            
                            text_elements.append({
                                "text": raw_text,
                                "size": round(s["size"], 1),
                                "flags": s["flags"],
                                "font": s.get("font", ""),  # Add font information
                                "page": page_num,
                                "y_position": y_position,
                                "relative_y": relative_y,
                                "x_position": x_position,
                                "relative_x": relative_x
                            })
    
    # Find "Background" and "Summary" elements
    target_elements = []
    for elem in text_elements:
        text_lower = elem["text"].lower()
        if "background" in text_lower or "summary" in text_lower:
            target_elements.append(elem)
    
    print(f"Found {len(target_elements)} elements containing 'background' or 'summary':")
    for i, elem in enumerate(target_elements, 1):
        print(f"\n{i}. Text: '{elem['text']}'")
        print(f"   Page: {elem['page']}")
        print(f"   Font Size: {elem['size']}")
        print(f"   Font: {elem['font']}")
        print(f"   Bold: {bool(elem['flags'] & 16)}")
        print(f"   Position: ({elem['x_position']:.1f}, {elem['y_position']:.1f})")
        print(f"   Relative Position: ({elem['relative_x']:.2f}, {elem['relative_y']:.2f})")
    
    # Analyze font sizes in the document
    sizes = [t["size"] for t in text_elements if len(t["text"]) > 3]
    most_common = Counter(sizes).most_common()
    body_text_size = most_common[0][0]
    unique_sizes = sorted(set(sizes), reverse=True)
    
    print(f"\n=== FONT SIZE ANALYSIS ===")
    print(f"Body text size (most common): {body_text_size}")
    print(f"All unique sizes: {unique_sizes[:10]}...")  # Show first 10
    print(f"Top 5 most common sizes: {most_common[:5]}")
    
    # Determine heading levels as the main code does
    heading_levels = {}
    level_names = ["H1", "H2", "H3", "H4"]
    title_size = unique_sizes[0] if unique_sizes else body_text_size
    
    # Add sizes significantly larger than body text
    heading_candidate_sizes = []
    for sz in unique_sizes:
        if sz > body_text_size * 1.2:
            heading_candidate_sizes.append(sz)
    
    # Sort and assign levels (skip title size)
    heading_candidate_sizes = sorted(set(heading_candidate_sizes), reverse=True)
    for i, sz in enumerate(heading_candidate_sizes):
        if sz == title_size:
            continue
        if len(heading_levels) < len(level_names):
            heading_levels[sz] = level_names[len(heading_levels)]
    
    print(f"\nHeading levels detected: {heading_levels}")
    
    # Now analyze why each target element fails the filtering
    print(f"\n=== FILTERING ANALYSIS ===")
    
    # Calculate frequency of all text
    all_text_frequency = Counter()
    for t in text_elements:
        text = t["text"]
        clean_text = re.sub(r"^[0-9.\-\u2013\u2014\)\(©®™]+\s*", "", text).strip()
        if clean_text:
            all_text_frequency[clean_text] += 1
    
    for i, elem in enumerate(target_elements, 1):
        print(f"\n--- Analysis for element {i}: '{elem['text']}' ---")
        
        text = elem["text"]
        clean_text = re.sub(r"^[0-9.\-\u2013\u2014\)\(©®™]+\s*", "", text).strip()
        
        # Check each filtering criterion
        is_bold = elem["flags"] & 16
        is_heading_size = elem["size"] in heading_levels
        
        print(f"  Clean text: '{clean_text}'")
        print(f"  Is bold: {bool(is_bold)}")
        print(f"  Font size in heading levels: {is_heading_size}")
        print(f"  Font size vs body ({body_text_size}): {elem['size']/body_text_size:.2f}x")
        
        # Check potential heading by formatting
        # Check potential heading by formatting (updated logic)
        font_family = elem.get("font", "").lower()
        is_heading_font = any(indicator in font_family for indicator in ['black', 'bold', 'heavy', 'semibold'])
        
        is_potential_heading_by_formatting = (
            (is_bold or is_heading_font) and 
            elem["size"] >= body_text_size * 0.9 and
            len(clean_text.split()) >= 1 and  # Changed from 2 to 1
            len(clean_text.split()) <= 12 and
            not re.match(r'^[A-Z]\.?[A-Z]?\.?[A-Z]?o?\.?$', clean_text) and
            not clean_text.lower() in ['name', 'date', 'signature', 'remarks', 'amount', 'total'] and
            not re.match(r'^[\.\u2026]+$', clean_text) and
            not re.match(r'^[\.\u2026\s]+$', clean_text)
        )
        
        print(f"  Font family: '{elem.get('font', 'Unknown')}'")
        print(f"  Is heading font (Arial-Black, etc.): {is_heading_font}")
        print(f"  Meets enhanced formatting criteria: {is_potential_heading_by_formatting}")
        print(f"  Text frequency: {all_text_frequency[clean_text]}")
        print(f"  Text length (words): {len(clean_text.split())}")
        print(f"  Right side of page (x > 70%): {elem['relative_x'] > 0.7}")
        
        # Overall qualification with updated logic
        qualifies = (is_heading_size or is_potential_heading_by_formatting) and \
                   clean_text and \
                   all_text_frequency[clean_text] <= 5 and \
                   elem['relative_x'] <= 0.7
        
        print(f"  >>> QUALIFIES AS HEADING: {qualifies}")
        
        if not qualifies:
            reasons = []
            if not (is_heading_size or is_potential_heading_by_formatting):
                reasons.append("doesn't meet size or formatting criteria")
            if not clean_text:
                reasons.append("no clean text")
            if all_text_frequency[clean_text] > 5:
                reasons.append("appears too frequently")
            if elem['relative_x'] > 0.7:
                reasons.append("on right side of page")
            print(f"  >>> EXCLUDED because: {', '.join(reasons)}")
    
    doc.close()

if __name__ == "__main__":
    import sys
    # Redirect output to file for better readability
    with open('debug_output.txt', 'w', encoding='utf-8') as f:
        old_stdout = sys.stdout
        sys.stdout = f
        debug_file03_heading_detection()
        sys.stdout = old_stdout
    
    print("Debug analysis written to debug_output.txt")
    
    # Also print key findings to console
    debug_file03_heading_detection()
