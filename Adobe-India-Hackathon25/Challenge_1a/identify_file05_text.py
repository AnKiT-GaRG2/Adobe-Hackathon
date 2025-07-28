import fitz
import json
from collections import Counter

def identify_all_text_file05():
    """
    Analyze all text in file05.pdf to understand content structure and styling patterns
    """
    pdf_path = "Challenge_1a/sample_dataset/pdfs/file05.pdf"
    doc = fitz.open(pdf_path)
    
    print("=== COMPLETE TEXT ANALYSIS FOR FILE05.PDF ===")
    
    all_text_elements = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        print(f"\n{'='*50}")
        print(f"PAGE {page_num}")
        print(f"{'='*50}")
        
        # Get all text with detailed formatting
        text_dict = page.get_text("dict")
        
        page_elements = []
        
        for block_num, block in enumerate(text_dict["blocks"]):
            if "lines" in block:  # Text block
                print(f"\n--- BLOCK {block_num} ---")
                
                for line_num, line in enumerate(block["lines"]):
                    line_text_parts = []
                    
                    for span_num, span in enumerate(line["spans"]):
                        text = span["text"]
                        if text.strip():  # Only process non-empty text
                            font_size = span["size"]
                            font_flags = span["flags"]
                            font_name = span["font"]
                            is_bold = bool(font_flags & 16)
                            is_italic = bool(font_flags & 2)
                            color = span.get("color", 0)
                            bbox = span["bbox"]
                            
                            # Store element details
                            element = {
                                "text": text.strip(),
                                "size": font_size,
                                "bold": is_bold,
                                "italic": is_italic,
                                "font": font_name,
                                "flags": font_flags,
                                "color": color,
                                "page": page_num,
                                "block": block_num,
                                "line": line_num,
                                "span": span_num,
                                "bbox": bbox,
                                "x": bbox[0],
                                "y": bbox[1],
                                "width": bbox[2] - bbox[0],
                                "height": bbox[3] - bbox[1]
                            }
                            
                            all_text_elements.append(element)
                            page_elements.append(element)
                            line_text_parts.append(text)
                            
                            print(f"  Span {span_num}: '{text.strip()}'")
                            print(f"    Font: {font_name}, Size: {font_size:.1f}")
                            print(f"    Bold: {is_bold}, Italic: {is_italic}")
                            print(f"    Color: {color}, Flags: {font_flags}")
                            print(f"    Position: ({bbox[0]:.1f}, {bbox[1]:.1f}) - ({bbox[2]:.1f}, {bbox[3]:.1f})")
                    
                    if line_text_parts:
                        line_full_text = "".join(line_text_parts)
                        print(f"  COMPLETE LINE: '{line_full_text}'")
        
        print(f"\n--- PAGE {page_num} SUMMARY ---")
        print(f"Total text elements: {len(page_elements)}")
        
        # Group by font size
        size_groups = {}
        for elem in page_elements:
            size = round(elem["size"], 1)
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(elem["text"])
        
        print("\nText by font size:")
        for size in sorted(size_groups.keys(), reverse=True):
            texts = size_groups[size]
            print(f"  Size {size}: {texts}")
    
    doc.close()
    
    print(f"\n{'='*60}")
    print("DOCUMENT-WIDE ANALYSIS")
    print(f"{'='*60}")
    
    print(f"\nTotal text elements across all pages: {len(all_text_elements)}")
    
    # Analyze font sizes
    print("\n--- FONT SIZE DISTRIBUTION ---")
    sizes = [elem["size"] for elem in all_text_elements]
    size_counts = Counter(sizes)
    
    for size, count in sorted(size_counts.items(), reverse=True):
        texts = [elem["text"] for elem in all_text_elements if elem["size"] == size]
        unique_texts = list(set(texts))
        print(f"Size {size:.1f} ({count} elements): {unique_texts}")
    
    # Analyze fonts
    print("\n--- FONT FAMILY DISTRIBUTION ---")
    fonts = [elem["font"] for elem in all_text_elements]
    font_counts = Counter(fonts)
    
    for font, count in font_counts.items():
        print(f"Font '{font}': {count} elements")
        # Show sample texts for each font
        sample_texts = [elem["text"] for elem in all_text_elements if elem["font"] == font][:5]
        print(f"  Sample texts: {sample_texts}")
    
    # Analyze colors
    print("\n--- COLOR DISTRIBUTION ---")
    colors = [elem["color"] for elem in all_text_elements]
    color_counts = Counter(colors)
    
    for color, count in color_counts.items():
        sample_texts = [elem["text"] for elem in all_text_elements if elem["color"] == color][:3]
        print(f"Color {color}: {count} elements - {sample_texts}")
    
    # Identify potential content categories
    print("\n--- CONTENT CATEGORIZATION ---")
    
    # URLs and web addresses
    urls = [elem for elem in all_text_elements if any(pattern in elem["text"].lower() for pattern in ['www.', '.com', '.org', '.net', 'http'])]
    if urls:
        print(f"URLs/Web addresses ({len(urls)}): {[elem['text'] for elem in urls]}")
    
    # Phone numbers
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    import re
    phones = [elem for elem in all_text_elements if re.search(phone_pattern, elem["text"])]
    if phones:
        print(f"Phone numbers ({len(phones)}): {[elem['text'] for elem in phones]}")
    
    # All caps text (potential headings or emphasis)
    all_caps = [elem for elem in all_text_elements if elem["text"].isupper() and len(elem["text"]) > 1]
    if all_caps:
        print(f"ALL CAPS text ({len(all_caps)}): {[elem['text'] for elem in all_caps]}")
    
    # Single words (potential decorative elements)
    single_words = [elem for elem in all_text_elements if len(elem["text"].split()) == 1]
    if single_words:
        single_word_texts = [elem["text"] for elem in single_words]
        print(f"Single words ({len(single_words)}): {single_word_texts}")
    
    # Large text (potential titles/headers)
    large_text = [elem for elem in all_text_elements if elem["size"] > 20]
    if large_text:
        print(f"Large text (>20pt) ({len(large_text)}): {[elem['text'] for elem in large_text]}")
    
    # TITLE DETECTION LOGIC
    print("\n--- TITLE DETECTION ANALYSIS ---")
    
    # Step 1: Find the largest font size (likely title)
    if all_text_elements:
        max_size = max(elem["size"] for elem in all_text_elements)
        title_candidates = [elem for elem in all_text_elements if elem["size"] == max_size]
        
        print(f"Largest font size: {max_size:.1f}pt")
        print(f"Title candidates (largest font): {[elem['text'] for elem in title_candidates]}")
        
        # Step 2: Check PDF metadata for title
        try:
            doc_for_metadata = fitz.open(pdf_path)  # Reopen for metadata since we closed earlier
            metadata_title = doc_for_metadata.metadata.get("title", "").strip()
            print(f"PDF Metadata title: '{metadata_title}' (length: {len(metadata_title)})")
            doc_for_metadata.close()
        except:
            metadata_title = ""
            print("PDF Metadata title: Not available")
        
        # Step 3: Apply title detection logic from process_pdfs.py
        detected_title = ""
        title_components = []
        
        if metadata_title:
            # Use metadata title as base
            detected_title = metadata_title
            title_components = [comp.strip().lower() for comp in metadata_title.replace("-", " ").split() if comp.strip()]
            print(f"Using metadata title: '{detected_title}'")
            print(f"Title components: {title_components}")
        else:
            # Fall back to largest font size text
            if title_candidates:
                # Combine all largest font text as potential title
                title_texts = [elem["text"].strip() for elem in title_candidates if elem["text"].strip()]
                detected_title = " ".join(title_texts)
                title_components = [comp.strip().lower() for comp in detected_title.replace("-", " ").split() if comp.strip()]
                print(f"Using largest font text as title: '{detected_title}'")
                print(f"Title components: {title_components}")
        
        # Step 4: Find title position for filtering other text
        title_y_position = None
        title_page = None
        
        if title_components:
            # Find the position of title text in the document
            for elem in all_text_elements:
                if elem["size"] == max_size and elem["page"] <= 2:  # Look in first 3 pages
                    clean_text = elem["text"].strip().lower()
                    if any(comp in clean_text for comp in title_components):
                        if title_y_position is None or elem["y"] < title_y_position:
                            title_y_position = elem["y"]
                            title_page = elem["page"]
            
            if title_y_position is not None:
                print(f"Title position: Page {title_page}, Y-coordinate {title_y_position:.1f}")
            else:
                print("Title position: Not found in document")
        
        # Step 5: Analyze text relative to title
        if title_y_position is not None and title_page is not None:
            above_title = []
            same_level_as_title = []
            below_title = []
            
            for elem in all_text_elements:
                if elem["page"] == title_page:
                    if elem["y"] < title_y_position - 5:  # 5pt tolerance
                        above_title.append(elem)
                    elif abs(elem["y"] - title_y_position) <= 5:  # Same level
                        same_level_as_title.append(elem)
                    else:
                        below_title.append(elem)
                elif elem["page"] < title_page:
                    above_title.append(elem)
                else:
                    below_title.append(elem)
            
            print(f"\nText above title ({len(above_title)} elements):")
            for elem in above_title[:5]:  # Show first 5
                print(f"  '{elem['text']}' (Size: {elem['size']:.1f})")
            
            print(f"\nText at title level ({len(same_level_as_title)} elements):")
            for elem in same_level_as_title:
                print(f"  '{elem['text']}' (Size: {elem['size']:.1f})")
            
            print(f"\nText below title ({len(below_title)} elements):")
            for elem in below_title[:10]:  # Show first 10
                print(f"  '{elem['text']}' (Size: {elem['size']:.1f})")
        
        # Step 6: Heading level analysis based on font sizes
        print("\n--- HEADING LEVEL ANALYSIS ---")
        
        # Get unique font sizes, sorted largest to smallest
        unique_sizes = sorted(set(elem["size"] for elem in all_text_elements), reverse=True)
        print(f"All font sizes (largest to smallest): {[f'{size:.1f}' for size in unique_sizes]}")
        
        # Determine body text size (most frequent)
        size_counts = Counter(elem["size"] for elem in all_text_elements)
        body_text_size = size_counts.most_common(1)[0][0]
        print(f"Body text size (most frequent): {body_text_size:.1f}pt")
        
        # Assign heading levels (excluding title size)
        title_size = unique_sizes[0]
        heading_candidate_sizes = [sz for sz in unique_sizes[1:] if sz > body_text_size]
        
        print(f"Title size: {title_size:.1f}pt")
        print(f"Heading candidate sizes: {[f'{size:.1f}' for size in heading_candidate_sizes[:3]]}")
        
        heading_levels = {}
        level_names = ["H1", "H2", "H3"]
        
        for i, sz in enumerate(heading_candidate_sizes[:3]):
            heading_levels[sz] = level_names[i]
        
        print(f"Assigned heading levels: {heading_levels}")
        
        # Show text for each heading level
        for size, level in heading_levels.items():
            level_texts = [elem["text"] for elem in all_text_elements if elem["size"] == size]
            print(f"{level} (Size {size:.1f}): {level_texts}")
        
        # Final title determination
        print(f"\n--- FINAL TITLE DETERMINATION ---")
        print(f"Detected title: '{detected_title if detected_title else 'Untitled Document'}'")
        
        title_detection_results = {
            "detected_title": detected_title if detected_title else "Untitled Document",
            "title_components": title_components,
            "title_position": {"page": title_page, "y": title_y_position} if title_y_position else None,
            "heading_levels": heading_levels,
            "body_text_size": body_text_size,
            "title_size": title_size
        }
    
    # Save comprehensive analysis to JSON file
    output_data = {
        "total_elements": len(all_text_elements),
        "font_size_distribution": dict(size_counts),
        "font_family_distribution": dict(font_counts),
        "color_distribution": dict(color_counts),
        "title_detection": title_detection_results,
        "all_elements": all_text_elements
    }
    
    with open("Challenge_1a/sample_dataset/outputs/file05_complete_text_analysis.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nComprehensive analysis with title detection saved to: Challenge_1a/sample_dataset/outputs/file05_complete_text_analysis.json")
    return title_detection_results

if __name__ == "__main__":
    identify_all_text_file05()
