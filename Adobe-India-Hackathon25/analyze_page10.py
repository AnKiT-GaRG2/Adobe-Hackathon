import fitz
import re
from collections import Counter

def analyze_page_10(pdf_path):
    doc = fitz.open(pdf_path)
    
    print("=== ANALYZING PAGE 10 SPECIFICALLY ===")
    
    if len(doc) >= 10:
        page = doc[9]  # Page 10 (0-indexed)
        blocks = page.get_text("dict")["blocks"]
        
        print("\nAll text elements on page 10:")
        page_elements = []
        
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip()
                        if text and len(text) > 1:
                            page_elements.append({
                                "text": text,
                                "size": round(s["size"], 1),
                                "flags": s["flags"],
                                "bbox": s["bbox"]  # bounding box for position
                            })
                            print(f"Size: {s['size']:.1f}, Flags: {s['flags']}, Position: {s['bbox']}, Text: '{text}'")
        
        # Analyze the context around "Agile Tester" and "Syllabus"
        print(f"\n=== CONTEXT ANALYSIS ===")
        
        for i, elem in enumerate(page_elements):
            if "agile tester" in elem["text"].lower() or "syllabus" in elem["text"].lower():
                print(f"\nFound '{elem['text']}' at position {i}:")
                print(f"  Current: Size {elem['size']}, Flags {elem['flags']}, Text: '{elem['text']}'")
                
                # Show surrounding elements for context
                start = max(0, i-2)
                end = min(len(page_elements), i+3)
                
                print("  Context:")
                for j in range(start, end):
                    marker = " >>> " if j == i else "     "
                    print(f"{marker}[{j}] Size {page_elements[j]['size']}, Text: '{page_elements[j]['text']}'")
    
    doc.close()

def analyze_multiline_headings(pdf_path):
    doc = fitz.open(pdf_path)
    print("\n=== CHECKING FOR MULTILINE HEADINGS ===")
    
    all_elements = []
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip()
                        if text and len(text) > 1:
                            all_elements.append({
                                "text": text,
                                "size": round(s["size"], 1),
                                "flags": s["flags"],
                                "page": page_num,
                                "bbox": s["bbox"]
                            })
    
    # Look for patterns where text might be split across spans
    for i, elem in enumerate(all_elements):
        if elem["page"] == 10 and elem["size"] == 16.0:  # H2 size
            # Check if this might be part of a larger heading
            print(f"\nH2-sized element on page 10: '{elem['text']}'")
            
            # Check nearby elements
            nearby = [e for e in all_elements[max(0,i-3):i+4] if e["page"] == 10]
            for j, near_elem in enumerate(nearby):
                marker = " >>> " if near_elem["text"] == elem["text"] else "     "
                print(f"{marker}Size {near_elem['size']}, Text: '{near_elem['text']}'")

if __name__ == "__main__":
    analyze_page_10('sample_dataset/pdfs/file02.pdf')
    analyze_multiline_headings('sample_dataset/pdfs/file02.pdf')
