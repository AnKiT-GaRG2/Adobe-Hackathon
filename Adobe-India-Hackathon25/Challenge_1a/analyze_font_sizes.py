import fitz
from collections import Counter

def analyze_font_sizes():
    pdf_path = "sample_dataset/pdfs/file04.pdf"
    doc = fitz.open(pdf_path)
    
    font_sizes = []
    text_by_size = {}
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text_dict = page.get_text("dict")
        
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text and len(text) > 2:  # Skip very short text
                            size = round(span["size"], 1)
                            font_sizes.append(size)
                            
                            if size not in text_by_size:
                                text_by_size[size] = []
                            text_by_size[size].append(text)
    
    print("=== FONT SIZE ANALYSIS ===")
    size_counts = Counter(font_sizes)
    
    for size, count in sorted(size_counts.items(), reverse=True):
        print(f"\nSize {size} ({count} occurrences):")
        unique_texts = list(set(text_by_size[size]))[:10]  # Show first 10 unique texts
        for text in unique_texts:
            print(f"  '{text[:50]}{'...' if len(text) > 50 else ''}'")
    
    doc.close()

if __name__ == "__main__":
    analyze_font_sizes()
