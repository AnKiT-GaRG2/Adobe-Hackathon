import fitz
import re
from collections import Counter

def debug_heading_logic(pdf_path):
    doc = fitz.open(pdf_path)
    text_elements = []

    # Collect text with font sizes
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text_elements.append({
                            "text": s["text"].strip(),
                            "size": round(s["size"], 1),
                            "flags": s["flags"],
                            "page": page_num
                        })

    # Determine body text size and heading levels
    sizes = [t["size"] for t in text_elements if len(t["text"]) > 3]
    most_common = Counter(sizes).most_common()
    body_text_size = most_common[0][0]

    unique_sizes = sorted(set(sizes), reverse=True)
    title_size = unique_sizes[0] if unique_sizes else body_text_size
    
    print(f"Body text size: {body_text_size}")
    print(f"Title size: {title_size}")
    print(f"All unique sizes: {unique_sizes}")
    
    heading_candidate_sizes = [sz for sz in unique_sizes[1:] if sz > body_text_size]
    print(f"Heading candidate sizes: {heading_candidate_sizes}")
    
    heading_levels = {}
    level_names = ["H1", "H2", "H3"]
    
    for i, sz in enumerate(heading_candidate_sizes[:3]):
        heading_levels[sz] = level_names[i]
    
    print(f"Assigned heading levels: {heading_levels}")
    
    # Show what text gets what classification
    print(f"\n=== TEXT CLASSIFICATION ===")
    
    title_components = []
    for t in text_elements:
        text = t["text"]
        if not text or len(text) < 2:
            continue
            
        clean_text = re.sub(r"^[0-9.\-\)\(]+\s*", "", text).strip()
        
        if (t["size"] == title_size and 
            t["page"] <= 2 and 
            len(title_components) < 5 and
            clean_text):
            title_components.append(clean_text)
            print(f"TITLE COMPONENT: '{clean_text}' (size: {t['size']}, page: {t['page']})")
    
    print(f"\nFull title: '{' '.join(title_components)}'")
    
    print(f"\n=== OUTLINE ITEMS ===")
    for t in text_elements:
        text = t["text"]
        if not text or len(text) < 2:
            continue

        clean_text = re.sub(r"^[0-9.\-\)\(]+\s*", "", text).strip()

        if (t["size"] in heading_levels and 
            clean_text and 
            clean_text not in title_components):
            print(f"{heading_levels[t['size']]}: '{clean_text}' (size: {t['size']}, page: {t['page']})")

if __name__ == "__main__":
    debug_heading_logic('sample_dataset/pdfs/file02.pdf')
