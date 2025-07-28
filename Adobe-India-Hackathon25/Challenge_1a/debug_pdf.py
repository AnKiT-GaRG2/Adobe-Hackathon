import fitz
import json
from collections import Counter

def analyze_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    print(f"Analyzing: {pdf_path}")
    print(f"Total pages: {len(doc)}")
    
    all_text_elements = []
    
    for page_num, page in enumerate(doc, start=1):
        print(f"\n--- Page {page_num} ---")
        blocks = page.get_text("dict")["blocks"]
        page_elements = []
        
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip()
                        if text and len(text) > 1:
                            element = {
                                "text": text,
                                "size": round(s["size"], 1),
                                "page": page_num
                            }
                            all_text_elements.append(element)
                            page_elements.append(element)
        
        # Show first 10 text elements from this page
        print(f"Found {len(page_elements)} text elements on page {page_num}")
        for i, elem in enumerate(page_elements[:10]):
            print(f"  {i+1}. Size: {elem['size']}, Text: \"{elem['text'][:60]}...\"")
        
        if len(page_elements) > 10:
            print(f"  ... and {len(page_elements) - 10} more elements")
    
    # Analyze font sizes
    print(f"\n--- Font Size Analysis ---")
    sizes = [elem["size"] for elem in all_text_elements]
    size_counter = Counter(sizes)
    
    print("Font size frequency:")
    for size, count in size_counter.most_common(10):
        print(f"  Size {size}: {count} occurrences")
    
    # Find unique sizes
    unique_sizes = sorted(set(sizes), reverse=True)
    print(f"\nAll unique font sizes (largest first): {unique_sizes}")
    
    # Determine body text size
    if size_counter:
        body_text_size = size_counter.most_common(1)[0][0]
        print(f"Most common (body text) size: {body_text_size}")
        
        # Find potential heading sizes
        potential_heading_sizes = [sz for sz in unique_sizes if sz > body_text_size]
        print(f"Potential heading sizes (larger than body): {potential_heading_sizes}")
    
    doc.close()

if __name__ == "__main__":
    print("=== ANALYZING FILE01.PDF ===")
    analyze_pdf("sample_dataset/pdfs/file01.pdf")
    
    print("\n\n=== ANALYZING FILE02.PDF ===")
    analyze_pdf("sample_dataset/pdfs/file02.pdf")
