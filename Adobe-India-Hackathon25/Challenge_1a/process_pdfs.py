import fitz  # PyMuPDF
import os
import json
import re
from collections import Counter

def normalize_unicode_characters(text):
    """
    Normalize special characters to their proper Unicode representations
    """
    if not text:
        return text
    
    # Define character replacements
    unicode_replacements = {
        # Replace various dash characters with en dash (U+2013)
        '-': '\u2013',          # hyphen-minus to en dash
        '—': '\u2014',          # em dash (keep as em dash)
        '–': '\u2013',          # en dash (already correct)
        
        # Replace various quote characters
        '"': '\u201C',          # left double quotation mark
        '"': '\u201D',          # right double quotation mark
        "'": '\u2018',          # left single quotation mark
        "'": '\u2019',          # right single quotation mark
        '`': '\u2018',          # grave accent to left single quotation mark
        
        # Replace various apostrophes
        "'": '\u2019',          # apostrophe to right single quotation mark
        
        # Replace ellipsis
        '...': '\u2026',        # horizontal ellipsis
        
        # Replace bullet points
        '•': '\u2022',          # bullet (already correct)
        '·': '\u00B7',          # middle dot
        
        # Replace trademark and copyright symbols
        '(TM)': '\u2122',       # trade mark sign
        '(tm)': '\u2122',       # trade mark sign
        '(R)': '\u00AE',        # registered sign
        '(r)': '\u00AE',        # registered sign
        '(C)': '\u00A9',        # copyright sign
        '(c)': '\u00A9',        # copyright sign
    }
    
    # Apply replacements
    normalized_text = text
    for old_char, new_char in unicode_replacements.items():
        normalized_text = normalized_text.replace(old_char, new_char)
    
    return normalized_text

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    text_elements = []

    # --- 1. Collect text with font sizes ---
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        # Apply Unicode normalization to the text
                        raw_text = s["text"].strip()
                        normalized_text = normalize_unicode_characters(raw_text)
                        text_elements.append({
                            "text": normalized_text,
                            "size": round(s["size"], 1),
                            "flags": s["flags"],
                            "page": page_num
                        })

    # --- 2. Determine title & heading levels ---
    sizes = [t["size"] for t in text_elements if len(t["text"]) > 3]
    most_common = Counter(sizes).most_common()
    body_text_size = most_common[0][0]  # most frequent = normal text size

    # Sort unique sizes (largest first)
    unique_sizes = sorted(set(sizes), reverse=True)
    heading_levels = {}
    level_names = ["H1", "H2", "H3"]

    # Only assign heading levels to sizes that are SIGNIFICANTLY larger than body text
    # and skip the largest size (which is likely the title)
    title_size = unique_sizes[0] if unique_sizes else body_text_size
    
    heading_candidate_sizes = [sz for sz in unique_sizes[1:] if sz > body_text_size]
    
    for i, sz in enumerate(heading_candidate_sizes[:3]):
        heading_levels[sz] = level_names[i]

    title = ""
    outline = []
    title_components = []  # Store all components that make up the title
    
    # First pass: collect potential title components (largest size text on first few pages)
    for t in text_elements:
        text = t["text"]
        if not text or len(text) < 2:
            continue
            
        # Clean text by removing numbering/bullets (including Unicode dashes)
        clean_text = re.sub(r"^[0-9.\-\u2013\u2014\)\(]+\s*", "", text).strip()
        
        # Consider text as title component if:
        # 1. It's the largest font size (title_size)
        # 2. It's on the first 2 pages (to catch multi-page titles)
        # 3. We haven't collected too many components yet (max 5 to avoid noise)
        if (t["size"] == title_size and 
            t["page"] <= 2 and 
            len(title_components) < 5 and
            clean_text):
            title_components.append(clean_text)
    
    # Construct title from components
    if title_components:
        title = " ".join(title_components)
    
    # Second pass: build outline excluding title components and consolidating split headings
    potential_headings = []
    
    for t in text_elements:
        text = t["text"]
        if not text or len(text) < 2:
            continue

        # Clean text by removing numbering/bullets (including Unicode dashes)
        clean_text = re.sub(r"^[0-9.\-\u2013\u2014\)\(]+\s*", "", text).strip()

        # Collect potential heading elements
        if (t["size"] in heading_levels and 
            clean_text and 
            clean_text not in title_components):
            potential_headings.append({
                "level": heading_levels[t["size"]],
                "text": clean_text,
                "page": t["page"],
                "size": t["size"],
                "original_text": text.strip()
            })
    
    # Consolidate consecutive headings of the same level on the same page
    consolidated_headings = []
    i = 0
    
    while i < len(potential_headings):
        current = potential_headings[i]
        combined_text = current["text"]
        
        # Look ahead for consecutive headings of same level and page
        j = i + 1
        while (j < len(potential_headings) and 
               potential_headings[j]["level"] == current["level"] and
               potential_headings[j]["page"] == current["page"]):
            
            # Check if they should be combined (same page, same level, reasonable text length)
            next_heading = potential_headings[j]
            
            # Combine if the next text looks like a continuation
            # (not starting with a number, or very short text)
            if (not re.match(r'^\d+\.', next_heading["text"]) and 
                len(next_heading["text"]) < 20):
                combined_text += " " + next_heading["text"]
                j += 1
            else:
                break
        
        # Only add if the combined text doesn't look like fragmented parts
        # Skip very short headings that are likely fragments (including Unicode dashes)
        fragment_chars = ['\u2013', '\u2014', '-', '\u2022', '•', '\u00B7', '·']
        if len(combined_text.strip()) > 3 and combined_text.strip() not in fragment_chars:
            consolidated_headings.append({
                "level": current["level"],
                "text": combined_text.strip(),
                "page": current["page"]
            })
        
        i = j if j > i + 1 else i + 1
    
    outline = consolidated_headings

    return {
        "title": title if title else "Untitled Document",
        "outline": outline
    }

def process_pdfs(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for file in os.listdir(input_dir):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, file.replace(".pdf", ".json"))
            result = extract_outline(pdf_path)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"Processed: {file} → {output_path}")

if __name__ == "__main__":
    # Use relative paths for local execution, absolute paths for Docker
    script_dir = os.path.dirname(os.path.abspath(__file__))
    INPUT_DIR = os.path.join(script_dir, "sample_dataset", "pdfs")
    OUTPUT_DIR = os.path.join(script_dir, "sample_dataset", "outputs")
    process_pdfs(INPUT_DIR, OUTPUT_DIR)
