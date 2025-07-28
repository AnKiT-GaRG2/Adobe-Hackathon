from process_pdfs import extract_outline
import fitz

def debug_heading_sizes():
    # Get the raw heading detection before stack processing
    doc = fitz.open('sample_dataset/pdfs/file02.pdf')
    text_elements = []

    # Collect text with font sizes
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        raw_text = s["text"].strip()
                        if raw_text and len(raw_text) > 3:
                            text_elements.append({
                                "text": raw_text,
                                "size": round(s["size"], 1),
                                "page": page_num,
                            })

    # Determine body text size
    from collections import Counter
    sizes = [t["size"] for t in text_elements]
    most_common = Counter(sizes).most_common()
    body_text_size = most_common[0][0]
    
    unique_sizes = sorted(set(sizes), reverse=True)
    title_size = unique_sizes[0]
    heading_candidate_sizes = [sz for sz in unique_sizes[1:] if sz > body_text_size]
    
    print(f"Body text size: {body_text_size}")
    print(f"Title size: {title_size}")
    print(f"Heading candidate sizes: {heading_candidate_sizes}")
    print()
    
    # Show examples of text at each heading size
    for size in heading_candidate_sizes:
        print(f"Size {size} examples:")
        examples = [t for t in text_elements if t["size"] == size][:3]
        for ex in examples:
            print(f"  - \"{ex['text'][:50]}...\" (Page {ex['page']})")
        print()

if __name__ == "__main__":
    debug_heading_sizes()
