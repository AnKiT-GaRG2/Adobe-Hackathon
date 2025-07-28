import fitz  # PyMuPDF
import sys
from collections import Counter

def analyze_font_properties(pdf_path):
    """Analyze font properties including size, flags (boldness), and font names"""
    print(f"\n=== Analyzing font properties for {pdf_path} ===")
    
    doc = fitz.open(pdf_path)
    font_info = []
    
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip()
                        if text and len(text) > 2:  # Only meaningful text
                            # PyMuPDF flags: 
                            # 16 = bold
                            # 2 = italic 
                            # 8 = monospace
                            flags = s["flags"]
                            is_bold = bool(flags & 16)
                            is_italic = bool(flags & 2)
                            font_name = s.get("font", "Unknown")
                            
                            font_info.append({
                                "text": text,
                                "page": page_num,
                                "size": round(s["size"], 1),
                                "flags": flags,
                                "is_bold": is_bold,
                                "is_italic": is_italic,
                                "font": font_name,
                                "bbox": s["bbox"]
                            })
    
    doc.close()
    
    # Group by font properties
    print(f"\n--- Font Size Distribution ---")
    sizes = [f["size"] for f in font_info]
    size_counts = Counter(sizes).most_common()
    for size, count in size_counts:
        print(f"Size {size}: {count} occurrences")
    
    print(f"\n--- Bold Text Analysis ---")
    bold_texts = [f for f in font_info if f["is_bold"]]
    print(f"Total bold texts: {len(bold_texts)}")
    
    if bold_texts:
        bold_sizes = Counter([f["size"] for f in bold_texts]).most_common()
        print("Bold text sizes:")
        for size, count in bold_sizes:
            print(f"  Size {size}: {count} bold texts")
        
        print("\nSample bold texts (first 10):")
        for i, text_info in enumerate(bold_texts[:10]):
            print(f"  Page {text_info['page']}: '{text_info['text']}' (size: {text_info['size']}, font: {text_info['font']})")
    
    print(f"\n--- Font Family Analysis ---")
    fonts = Counter([f["font"] for f in font_info]).most_common()
    for font, count in fonts[:10]:  # Top 10 fonts
        print(f"  {font}: {count} occurrences")
    
    return font_info

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_font_properties.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    analyze_font_properties(pdf_path)
