import fitz
import json
from collections import Counter
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from process_pdfs import extract_outline

def analyze_file05_styling():
    pdf_path = "sample_dataset/pdfs/file05.pdf"
    doc = fitz.open(pdf_path)
    
    print("=== FILE05.PDF STYLING ANALYSIS ===")
    
    for page_num, page in enumerate(doc):
        print(f"\nPage {page_num}:")
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip()
                        if text:
                            print(f"  Text: '{text}' | Size: {s['size']:.1f} | Font: {s.get('font', 'N/A')} | Flags: {s['flags']}")
    
    doc.close()

    # Also run the extract_outline to see what it currently detects
    print("\n=== CURRENT OUTLINE EXTRACTION ===")
    result = extract_outline(pdf_path)
    print(f"Title: {result['title']}")
    print(f"Headings: {len(result['outline'])}")
    for heading in result['outline']:
        print(f"  {heading['level']}: {heading['text']}")

if __name__ == "__main__":
    analyze_file05_styling()
    
    all_elements = []
    
    for page_num in range(min(3, len(doc))):  # First 3 pages
        page = doc[page_num]
        print(f"\n--- PAGE {page_num} ---")
        
        # Get all text with detailed formatting
        text_dict = page.get_text("dict")
        
        for block_num, block in enumerate(text_dict["blocks"]):
            if "lines" in block:  # Text block
                print(f"\nBlock {block_num}:")
                for line_num, line in enumerate(block["lines"]):
                    for span_num, span in enumerate(line["spans"]):
                        text = span["text"].strip()
                        if text:
                            font_size = span["size"]
                            font_flags = span["flags"]
                            font_name = span["font"]
                            is_bold = bool(font_flags & 16)
                            is_italic = bool(font_flags & 2)
                            color = span.get("color", 0)
                            
                            # Store for analysis
                            all_elements.append({
                                "text": text,
                                "size": font_size,
                                "bold": is_bold,
                                "italic": is_italic,
                                "font": font_name,
                                "flags": font_flags,
                                "color": color,
                                "page": page_num,
                                "bbox": span["bbox"]
                            })
                            
                            print(f"  Line {line_num}, Span {span_num}:")
                            print(f"    Text: '{text}'")
                            print(f"    Size: {font_size}")
                            print(f"    Bold: {is_bold}")
                            print(f"    Italic: {is_italic}")
                            print(f"    Font: {font_name}")
                            print(f"    Color: {color}")
                            print(f"    Flags: {font_flags}")
                            print(f"    BBox: {span['bbox']}")
    
    print("\n=== FONT SIZE DISTRIBUTION ===")
    sizes = [e["size"] for e in all_elements]
    size_counts = Counter(sizes)
    for size, count in sorted(size_counts.items(), reverse=True):
        texts = [e["text"] for e in all_elements if e["size"] == size]
        print(f"Size {size:.1f} ({count} occurrences): {texts[:5]}")
    
    print("\n=== FONT ANALYSIS ===")
    fonts = [e["font"] for e in all_elements]
    font_counts = Counter(fonts)
    for font, count in font_counts.items():
        print(f"Font '{font}': {count} occurrences")
    
    print("\n=== COLOR ANALYSIS ===")
    colors = [e["color"] for e in all_elements]
    color_counts = Counter(colors)
    for color, count in color_counts.items():
        texts = [e["text"] for e in all_elements if e["color"] == color]
        print(f"Color {color}: {count} occurrences - {texts[:3]}")
    
    print("\n=== DECORATIVE PATTERNS ===")
    # Look for decorative patterns
    decorative_indicators = []
    for element in all_elements:
        text = element["text"]
        # Check for decorative patterns
        if any(char in text for char in "●○◆◇■□▲△▼▽★☆♦♣♠♥"):
            decorative_indicators.append(f"Symbols: '{text}'")
        elif text.isupper() and len(text.split()) <= 3:
            decorative_indicators.append(f"All caps short: '{text}'")
        elif "www." in text.lower() or ".com" in text.lower():
            decorative_indicators.append(f"URL: '{text}'")
        elif len(set(text)) <= 3 and len(text) > 3:  # Repetitive characters
            decorative_indicators.append(f"Repetitive: '{text}'")
    
    print("Decorative elements found:")
    for indicator in decorative_indicators[:10]:
        print(f"  {indicator}")
    
    doc.close()

if __name__ == "__main__":
    analyze_file05_styling()
