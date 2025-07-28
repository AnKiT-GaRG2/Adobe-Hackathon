import fitz  # PyMuPDF
import json
import re
from collections import Counter

def debug_missing_headings(pdf_path):
    """Debug why specific headings are missing from the output"""
    
    # The headings we're looking for
    target_headings = ["Summary", "Timeline:", "Background"]
    
    doc = fitz.open(pdf_path)
    text_elements = []
    
    print(f"Debugging PDF: {pdf_path}")
    print("=" * 50)
    
    # Collect all text elements
    for page_num, page in enumerate(doc, start=1):
        page_height = page.rect.height
        page_width = page.rect.width
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        raw_text = s["text"].strip()
                        if raw_text:  # Only include non-empty text
                            y_position = s["bbox"][1]
                            relative_y = y_position / page_height
                            x_position = s["bbox"][0]
                            relative_x = x_position / page_width
                            
                            text_elements.append({
                                "text": raw_text,
                                "size": round(s["size"], 1),
                                "flags": s["flags"],
                                "page": page_num,
                                "y_position": y_position,
                                "relative_y": relative_y,
                                "x_position": x_position,
                                "relative_x": relative_x
                            })
    
    # Analyze font sizes
    sizes = [t["size"] for t in text_elements if len(t["text"]) > 3]
    most_common = Counter(sizes).most_common()
    body_text_size = most_common[0][0] if most_common else 12
    unique_sizes = sorted(set(sizes), reverse=True)
    
    print(f"Body text size: {body_text_size}")
    print(f"Font sizes found: {unique_sizes[:10]}")  # Show top 10 sizes
    print()
    
    # Find elements containing target headings
    for target in target_headings:
        print(f"Looking for: '{target}'")
        print("-" * 30)
        
        found_elements = []
        for element in text_elements:
            text = element["text"].strip()
            # Check both exact match and cleaned match
            clean_text = re.sub(r"^[0-9.\-\u2013\u2014\)\(©®™]+\s*", "", text).strip()
            
            if (target.lower() in text.lower() or 
                target.lower() in clean_text.lower() or
                text.lower() == target.lower() or
                clean_text.lower() == target.lower()):
                found_elements.append(element)
        
        if not found_elements:
            print(f"  ❌ NOT FOUND: '{target}'")
            # Try fuzzy search
            print("  Fuzzy search results:")
            for element in text_elements:
                text = element["text"].strip()
                if any(word in text.lower() for word in target.lower().split()):
                    print(f"    Similar: '{text}' (Page {element['page']}, Size {element['size']}, Bold: {bool(element.get('flags', 0) & 16)})")
        else:
            print(f"  ✅ FOUND {len(found_elements)} instances:")
            for element in found_elements:
                text = element["text"]
                is_bold = bool(element.get("flags", 0) & 16)
                print(f"    Text: '{text}'")
                print(f"    Page: {element['page']}")
                print(f"    Font size: {element['size']} (body: {body_text_size})")
                print(f"    Bold: {is_bold}")
                print(f"    Position: Y={element['y_position']:.1f}, X={element['x_position']:.1f}")
                print(f"    Relative position: Y={element['relative_y']:.2f}, X={element['relative_x']:.2f}")
                
                # Check why it might be filtered out
                print("    Filtering checks:")
                
                # 1. Font size check
                larger_than_body = element['size'] > body_text_size * 1.2
                print(f"      - Large font (>{body_text_size * 1.2}): {larger_than_body}")
                
                # 2. Bold check
                print(f"      - Bold formatting: {is_bold}")
                
                # 3. Position checks
                on_right_side = element['relative_x'] > 0.7
                print(f"      - On right side (>70%): {on_right_side}")
                
                # 4. Date check
                contains_date_check = any(pattern in text.lower() for pattern in [
                    'january', 'february', 'march', 'april', 'may', 'june',
                    'july', 'august', 'september', 'october', 'november', 'december',
                    'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
                ])
                print(f"      - Contains date: {contains_date_check}")
                
                # 5. Form field check
                form_fields = ['name', 'date', 'signature', 'address', 'phone', 'email']
                is_form_field = text.lower().strip() in form_fields
                print(f"      - Is form field: {is_form_field}")
                
                # 6. Page position relative to title
                on_first_two_pages = element['page'] <= 2
                print(f"      - On first 2 pages: {on_first_two_pages}")
                
                # 7. Text frequency check
                text_count = sum(1 for e in text_elements if e['text'].strip() == text.strip())
                frequent_text = text_count > 5
                print(f"      - Appears frequently ({text_count} times): {frequent_text}")
                
                print()
        
        print()

# Run the debug
pdf_path = r"c:\Users\BIT\OneDrive\Desktop\Adobe India Hackathon\Adobe-India-Hackathon25\Challenge_1a\sample_dataset\pdfs\file03.pdf"
debug_missing_headings(pdf_path)
