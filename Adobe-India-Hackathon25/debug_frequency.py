import fitz
import re
from collections import Counter

def debug_frequency_detection(pdf_path):
    doc = fitz.open(pdf_path)
    text_elements = []

    # Collect all text elements
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        raw_text = s["text"].strip()
                        if raw_text:
                            text_elements.append({
                                "text": raw_text,
                                "size": round(s["size"], 1),
                                "flags": s["flags"],
                                "page": page_num
                            })

    # Find text frequency for heading-sized text
    sizes = [t["size"] for t in text_elements if len(t["text"]) > 3]
    most_common = Counter(sizes).most_common()
    body_text_size = most_common[0][0]
    unique_sizes = sorted(set(sizes), reverse=True)
    
    heading_candidate_sizes = [sz for sz in unique_sizes[1:] if sz > body_text_size]
    heading_levels = {}
    level_names = ["H1", "H2", "H3"]
    for i, sz in enumerate(heading_candidate_sizes[:3]):
        heading_levels[sz] = level_names[i]
    
    print(f"Heading levels: {heading_levels}")
    print(f"Body text size: {body_text_size}")
    
    # Check frequency of heading-sized text
    text_frequency = {}
    heading_texts = []
    
    for elem in text_elements:
        if elem["size"] in heading_levels and len(elem["text"]) > 5:
            clean_elem_text = re.sub(r"^[0-9.\-\u2013\u2014\)\(]+\s*", "", elem["text"]).strip().lower()
            if clean_elem_text:
                text_frequency[clean_elem_text] = text_frequency.get(clean_elem_text, 0) + 1
                heading_texts.append({
                    "text": clean_elem_text,
                    "original": elem["text"],
                    "page": elem["page"],
                    "size": elem["size"]
                })
    
    print(f"\n=== TEXT FREQUENCY ANALYSIS ===")
    for text, count in sorted(text_frequency.items(), key=lambda x: x[1], reverse=True):
        if count > 1:
            print(f"'{text}' appears {count} times")
    
    print(f"\n=== FREQUENT TEXTS (3+ times) ===")
    frequent_texts = {text for text, count in text_frequency.items() if count >= 3}
    for text in frequent_texts:
        print(f"'{text}' - would be skipped")
    
    print(f"\n=== ALL HEADING-SIZED TEXTS ===")
    for item in heading_texts:
        freq = text_frequency[item["text"]]
        skip_marker = " [SKIP]" if item["text"] in frequent_texts else ""
        print(f"Page {item['page']}, Size {item['size']}: '{item['original']}' (freq: {freq}){skip_marker}")

if __name__ == "__main__":
    debug_frequency_detection('sample_dataset/pdfs/file02.pdf')
