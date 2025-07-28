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

def convert_special_chars_to_hex(text):
    """
    Convert special characters to their hex representation
    """
    if not text:
        return text
    
    # Define which characters should be converted to hex
    special_chars_to_convert = {
        '\u2013': '\\x{2013}',  # en dash
        '\u2014': '\\x{2014}',  # em dash
        '\u201C': '\\x{201C}',  # left double quotation mark
        '\u201D': '\\x{201D}',  # right double quotation mark
        '\u2018': '\\x{2018}',  # left single quotation mark
        '\u2019': '\\x{2019}',  # right single quotation mark
        '\u2026': '\\x{2026}',  # horizontal ellipsis
        '\u2022': '\\x{2022}',  # bullet
        '\u00B7': '\\x{00B7}',  # middle dot
        '\u2122': '\\x{2122}',  # trade mark sign
        '\u00AE': '\\x{00AE}',  # registered sign
        '\u00A9': '\\x{00A9}',  # copyright sign
    }
    
    # Apply hex conversion
    hex_text = text
    for unicode_char, hex_repr in special_chars_to_convert.items():
        hex_text = hex_text.replace(unicode_char, hex_repr)
    
    return hex_text

def contains_date(text):
    """
    Comprehensive date detection function that checks if text contains any date format
    Returns True if the text contains a date in any common format
    Excludes section numbering patterns that are legitimate headings
    """
    if not text:
        return False
    
    # Clean the text for date checking
    text_clean = text.strip()
    
    # First, exclude section numbering patterns that should NOT be considered dates
    # These are legitimate heading patterns that contain numbers but aren't dates
    section_patterns = [
        r'^\d+(\.\d+)*\s+[A-Za-z]',  # e.g., "2.1 Introduction", "3.2.1 Overview"
        r'^[A-Za-z]+\s+\d+(\.\d+)*\s+[A-Za-z]',  # e.g., "Section 2.1 Introduction"
        r'^\d+(\.\d+)*\.\s*$',  # Just numbers with dots, e.g., "2.1."
    ]
    
    # If it matches section numbering patterns, it's NOT a date
    for pattern in section_patterns:
        if re.match(pattern, text_clean):
            return False
    
    # Define comprehensive date patterns (excluding version numbers that might be section numbers)
    date_patterns = [
        # Full month names with day and year
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
        
        # Abbreviated month names with day and year
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
        
        # Month/Day/Year formats (with various separators) - but only if it looks like a pure date
        r'^\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}$',
        
        # Year/Month/Day formats (ISO style) - but only if it looks like a pure date
        r'^\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}$',
        
        # Year-Month-Day (ISO 8601) - but only if it looks like a pure date
        r'^\d{4}-\d{2}-\d{2}$',
        
        # Month Day, Year (American style)
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b',
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},\s+\d{4}\b',
        
        # Day Month Year (British style)
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{4}\b',
        
        # Year only (4 digits) - but only if it's the entire text or clearly a year reference
        r'^\d{4}$',
        r'\byear\s+\d{4}\b',
        r'\bin\s+\d{4}\b',
        
        # Month/Year combinations - but be more specific
        r'^\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}$',
        r'^\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{4}$',
        
        # Quarters
        r'\bQ[1-4]\s+\d{4}\b',
        r'\b(First|Second|Third|Fourth)\s+Quarter\s+\d{4}\b',
        
        # Seasons with year
        r'\b(Spring|Summer|Fall|Autumn|Winter)\s+\d{4}\b',
        
        # Week formats
        r'\bWeek\s+\d{1,2},?\s+\d{4}\b',
        r'\bWeek\s+of\s+.*\d{4}\b',
        
        # Time stamps (hours:minutes)
        r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(AM|PM|am|pm)\b',
        
        # Relative dates
        r'^\b(Today|Yesterday|Tomorrow)$',
        r'^\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$',
        
        # Additional numeric date patterns
        r'\b\d{1,2}(?:st|nd|rd|th)\s+of\s+(January|February|March|April|May|June|July|August|September|October|November|December)\b',
        r'\b\d{1,2}(?:st|nd|rd|th)\s+of\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\b',
        
        # Date ranges - but only pure date ranges
        r'^\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\s*[-–—]\s*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}$',
        
        # European date format dd.mm.yyyy - but only if it's the entire text
        r'^\d{1,2}\.\d{1,2}\.\d{4}$',
        
        # Academic year format (e.g., "2023-24", "2023-2024") - but only if it's the entire text
        r'^\d{4}[-–—]\d{2,4}$',
        
        # Financial year quarters
        r'\bFY\s*\d{4}[-–—]?\d{0,4}\b',
        
        # Revision dates with explicit date context
        r'\bRev\.?\s*\d+(?:\.\d+)*\s+(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{4}\b',
        
        # Publication dates
        r'\bPublished:?\s+.*\d{4}\b',
        r'\bUpdated:?\s+.*\d{4}\b',
        r'\bModified:?\s+.*\d{4}\b',
        r'\bDate:?\s+.*\d{4}\b',
        
        # Copyright years
        r'\b©\s*\d{4}\b',
        r'\bCopyright\s+\d{4}\b',
    ]
    
    # Check if any date pattern matches the text
    for pattern in date_patterns:
        if re.search(pattern, text_clean, re.IGNORECASE):
            return True
    
    return False

def is_form_field_or_generic_term(text):
    """
    Check if the text is a common form field label or generic term that should not be considered a heading
    Returns True if the text should be excluded from headings
    """
    if not text:
        return False
    
    # Clean the text
    clean_text = text.strip().lower()
    
    # Single words that are typically form fields or generic terms
    form_fields_and_generic_terms = {
        # Common form fields
        'name', 'date', 'address', 'phone', 'email', 'signature', 'title', 'position',
        'department', 'company', 'organization', 'city', 'state', 'country', 'zip',
        'zipcode', 'postal', 'code', 'number', 'amount', 'total', 'subtotal',
        'quantity', 'price', 'cost', 'fee', 'tax', 'discount', 'balance',
        
        # Document metadata terms
        'page', 'pages', 'version', 'draft', 'final', 'copy',
        'original', 'duplicate', 'file', 'document', 'form', 'application',
        
        # Generic descriptive words
        'yes', 'no', 'true', 'false', 'male', 'female', 'other', 'none',
        'optional', 'required', 'mandatory', 'notes', 'comments', 'information', 'data',
        
        # Time-related single words
        'time', 'hour', 'minute', 'second', 'day', 'week', 'month', 'year',
        'today', 'yesterday', 'tomorrow', 'morning', 'afternoon', 'evening',
        'night', 'am', 'pm',
        
        # Status/action words
        'approved', 'rejected', 'pending', 'completed', 'incomplete', 'draft',
        'submitted', 'received', 'processed', 'cancelled', 'active', 'inactive',
        
        # Common single letter or number labels
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
        
        # Units and measurements
        'kg', 'lb', 'oz', 'cm', 'mm', 'inch', 'ft', 'meter', 'mile', 'km',
        'percent', '%', 'dollar', '$', 'euro', '€', 'pound', '£',
        
        # Checkbox/radio button labels
        'check', 'select', 'choose', 'pick', 'mark', 'tick', 'cross',
        
        # Common abbreviations
        'etc', 'inc', 'corp', 'ltd', 'llc', 'co', 'dept', 'div', 'mgr',
        'dir', 'vp', 'ceo', 'cfo', 'hr', 'it', 'pr', 'qa',
        
        # Educational/certification terms
        'grade', 'score', 'rank', 'level', 'class', 'course', 'subject',
        'test', 'exam', 'quiz', 'homework',
        
        # Medical/health form terms
        'age', 'weight', 'height', 'gender', 'race',
        
        # Financial terms
        'income', 'salary', 'wage', 'bonus', 'commission', 'deduction',
        'withholding', 'benefits', 'insurance', 'retirement', 'savings',
        
        # Legal terms
        'lawyer', 'judge', 'court',
        'case', 'claim', 'settlement', 'contract',
    }
    
    # Check if it's a single word and in our exclusion list
    if ' ' not in clean_text and clean_text in form_fields_and_generic_terms:
        return True
    
    # Also exclude very short single words (1-2 characters) that are likely labels
    if len(clean_text) <= 2 and ' ' not in clean_text:
        return True
    
    # Exclude words that are just numbers or simple patterns
    if re.match(r'^[0-9]+$', clean_text):  # Just numbers
        return True
    
    if re.match(r'^[a-z]$', clean_text):  # Single letters
        return True
    
    return False

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    text_elements = []

    # --- 1. Collect text with font sizes and position information ---
    for page_num, page in enumerate(doc, start=1):
        page_height = page.rect.height
        page_width = page.rect.width
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        # Apply Unicode normalization to the text
                        raw_text = s["text"].strip()
                        normalized_text = normalize_unicode_characters(raw_text)
                        # Calculate relative position on page (0.0 = top, 1.0 = bottom)
                        y_position = s["bbox"][1]  # Top Y coordinate of the text
                        relative_y = y_position / page_height
                        # Calculate horizontal position (0.0 = left, 1.0 = right)
                        x_position = s["bbox"][0]  # Left X coordinate of the text
                        relative_x = x_position / page_width
                        
                        text_elements.append({
                            "text": normalized_text,
                            "size": round(s["size"], 1),
                            "flags": s["flags"],
                            "page": page_num,
                            "y_position": y_position,
                            "relative_y": relative_y,
                            "x_position": x_position,
                            "relative_x": relative_x
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
    
    # Initial font-size based level assignment
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
        # 3. Has reasonable length (not too short or too long)
        if (t["size"] == title_size and 
            t["page"] <= 2 and 
            2 <= len(clean_text) <= 50 and  # Reasonable length bounds
            clean_text):
            title_components.append(clean_text)
    
    # Construct title from components
    if title_components:
        # Method to reconstruct title by merging overlapping text fragments
        def reconstruct_title_from_fragments(fragments):
            if not fragments:
                return ""
            
            # Start with the first fragment
            result = fragments[0]
            
            for fragment in fragments[1:]:
                merged = False
                
                # Try different overlap lengths (prioritize longer overlaps)
                min_len = min(len(result), len(fragment))
                for overlap_len in range(min(min_len, 15), 0, -1):  # Increased max overlap check
                    # Check if end of result matches beginning of fragment
                    if (overlap_len > 0 and 
                        result[-overlap_len:].lower().strip() == fragment[:overlap_len].lower().strip()):
                        # Found overlap, merge by removing the duplicate part
                        result = result + fragment[overlap_len:]
                        merged = True
                        break
                
                if not merged:
                    # Check if fragment is a substring of result (skip if so)
                    if fragment.lower().strip() in result.lower().strip():
                        continue
                    # Check if result is a substring of fragment (replace if so)
                    elif result.lower().strip() in fragment.lower().strip():
                        result = fragment
                        continue
                    # Check if they share common words that can be merged
                    else:
                        result_words = result.lower().split()
                        fragment_words = fragment.lower().split()
                        
                        # Look for word-level overlap
                        word_merged = False
                        for i in range(1, min(len(result_words), len(fragment_words)) + 1):
                            if result_words[-i:] == fragment_words[:i]:
                                # Found word overlap
                                result_part = ' '.join(result.split()[:-i]) if i < len(result_words) else ""
                                fragment_part = fragment
                                result = (result_part + " " + fragment_part).strip()
                                word_merged = True
                                break
                        
                        if not word_merged:
                            # No overlap found, concatenate with space
                            result = result + " " + fragment
            
            return result
        
        # Clean each component first and remove obvious duplicates, but be less aggressive
        seen_components = set()
        cleaned_components = []
        for comp in title_components:
            # Remove obvious artifacts and normalize
            cleaned = re.sub(r'([a-zA-Z])\1{2,}', r'\1', comp)  # Remove repeated letters
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Normalize whitespace
            
            # Skip if too short, but don't be too aggressive with substring filtering
            if len(cleaned) > 1 and cleaned.lower() not in seen_components:
                # Only skip if it's exactly the same (not just contained within)
                cleaned_components.append(cleaned)
                seen_components.add(cleaned.lower())
        
        title = reconstruct_title_from_fragments(cleaned_components)
        
        # Final cleanup
        title = re.sub(r'\s+', ' ', title).strip()  # Normalize whitespace
        title = re.sub(r'([a-zA-Z])\1{2,}', r'\1', title)  # Remove any remaining repeated letters
    
    # Find the position of the title to exclude headings above it
    title_y_position = None
    title_page = None
    
    # Find the earliest (topmost) title component position
    for t in text_elements:
        if t["size"] == title_size and t["page"] <= 2:
            clean_text = re.sub(r"^[0-9.\-\u2013\u2014\)\(©®™]+\s*", "", t["text"]).strip()
            if clean_text and any(comp.lower() in clean_text.lower() for comp in cleaned_components):
                if title_y_position is None or t["y_position"] < title_y_position:
                    title_y_position = t["y_position"]
                    title_page = t["page"]
    
    # Second pass: build outline excluding title components and consolidating split headings
    potential_headings = []
    
    # First, collect ALL text in the document and count frequency (including body text)
    all_text_frequency = Counter()
    
    for t in text_elements:
        text = t["text"]
        if not text or len(text) < 2:
            continue

        # Clean text by removing numbering/bullets AND copyright symbols (including Unicode dashes)
        clean_text = re.sub(r"^[0-9.\-\u2013\u2014\)\(©®™]+\s*", "", text).strip()
        
        # Count frequency of ALL text in the document (not just potential headings)
        if clean_text:
            all_text_frequency[clean_text] += 1
    
    # Now collect potential heading elements, excluding frequently repeated text
    for t in text_elements:
        text = t["text"]
        if not text or len(text) < 2:
            continue

        # Clean text by removing numbering/bullets AND copyright symbols (including Unicode dashes)
        clean_text = re.sub(r"^[0-9.\-\u2013\u2014\)\(©®™]+\s*", "", text).strip()
        
        # Check if the original text has numbering (before cleaning)
        has_numbering = bool(re.match(r"^[0-9]+(\.[0-9]+)*[\.\s]", text.strip()) or 
                            re.match(r"^[0-9]+(\s+[0-9]+)*\s", text.strip()))
        
        # Check if this text contains any date format (exclude dates from headings)
        # Use comprehensive date detection that covers all common date formats
        is_date = contains_date(text) or contains_date(clean_text)

        # Check if this is a form field or generic term (exclude from headings)
        is_form_field = is_form_field_or_generic_term(text) or is_form_field_or_generic_term(clean_text)

        # Check if this text appears above the title (exclude such text from being headings)
        above_title = False
        if title_y_position is not None and title_page is not None:
            if t["page"] == title_page and t["y_position"] < title_y_position:
                above_title = True
            elif t["page"] < title_page:
                above_title = True

        # Check if this text appears on the right side of the page (exclude from headings)
        # Headings typically appear on the left side or center, not on the right side
        # Text appearing on the right side is usually page numbers, headers, footers, or sidebar content
        # Using 70% as threshold: text starting beyond 70% of page width is considered right-side
        on_right_side = t["relative_x"] > 0.7  # Configurable threshold for right-side detection

        # Collect potential heading elements, but exclude:
        # 1. Text that appears too frequently (more than 5 times anywhere in the PDF)
        # 2. Any text containing dates in any format (comprehensive date detection)
        # 3. Form fields and generic single-word terms (name, date, address, etc.)
        # 4. Text that appears above the title
        # 5. Text that appears on the right side of the page
        if (t["size"] in heading_levels and 
            clean_text and 
            clean_text not in title_components and
            all_text_frequency[clean_text] <= 5 and  # Changed from 3 to 5 and using all_text_frequency
            not is_date and  # Exclude dates from headings
            not is_form_field and  # Exclude form fields and generic terms
            not above_title and  # Exclude headings above the title
            not on_right_side):  # Exclude headings on the right side of the page
            potential_headings.append({
                "level": heading_levels[t["size"]],
                "text": text.strip() if has_numbering else clean_text,  # Preserve original text for numbered headings
                "page": t["page"],
                "size": t["size"],
                "original_text": text.strip(),
                "has_numbering": has_numbering,
                "y_position": t["y_position"],  # Add position for checking text between headings
                "x_position": t["x_position"]   # Add x position for reference
            })
    
    # Reassign heading levels based on numbering hierarchy (overrides font-size levels)
    def get_numbering_level(text):
        """Determine heading level based on numbering pattern"""
        text = text.strip()
        
        # Match patterns like "1.", "2.", "3.", "4." (main sections with dot)
        if re.match(r"^[0-9]+\.\s", text):
            return "H1"
        
        # Match patterns like "1", "2", "3", "4" (main sections without dot)
        if re.match(r"^[0-9]+\s", text):
            return "H1"
        
        # Match patterns like "2.1", "2.2", "3.1", "4.2" (subsections)
        if re.match(r"^[0-9]+\.[0-9]+\s", text):
            return "H2"
        
        # Match patterns like "2 1", "2 2", "3 1", "4 2" (subsections without dots)
        if re.match(r"^[0-9]+\s+[0-9]+\s", text):
            return "H2"
        
        # Match patterns like "2.1.1", "3.2.1" (sub-subsections)
        if re.match(r"^[0-9]+\.[0-9]+\.[0-9]+\s", text):
            return "H3"
        
        # Match patterns like "2 1 1", "3 2 1" (sub-subsections without dots)
        if re.match(r"^[0-9]+\s+[0-9]+\s+[0-9]+\s", text):
            return "H3"
        
        return None
    
    # Apply numbering-based levels to numbered headings
    for heading in potential_headings:
        if heading["has_numbering"]:
            numbering_level = get_numbering_level(heading["text"])
            if numbering_level:
                heading["level"] = numbering_level
    
    # Helper function to check if there's text between two headings
    def has_text_between_headings(heading1, heading2, all_text_elements):
        """Check if there's body text between two headings"""
        if heading1["page"] != heading2["page"]:
            return True  # Different pages, assume there's content between
        
        # Get y-positions
        y1 = heading1["y_position"]
        y2 = heading2["y_position"]
        
        # Ensure y1 is the upper heading (smaller y value)
        if y1 > y2:
            y1, y2 = y2, y1
        
        # Check for text elements between these y positions on the same page
        for element in all_text_elements:
            if (element["page"] == heading1["page"] and 
                y1 < element["y_position"] < y2 and
                element["size"] not in heading_levels and  # Not a heading
                len(element["text"].strip()) > 3):  # Meaningful text
                return True
        
        return False
    
    # Consolidate consecutive headings of the same level on the same page
    # and combine split numbered sections (e.g., "1." + "Introduction to...")
    consolidated_headings = []
    i = 0
    
    while i < len(potential_headings):
        current = potential_headings[i]
        combined_text = current["text"]
        
        # Special handling for numbered sections that might be split
        # If current text is just a number (like "1.", "2.", "1", "2", etc.), look for the next heading on same page
        if re.match(r"^[0-9]+[\.\s]*$", current["text"].strip()):
            # Look for the next heading on the same page to combine
            j = i + 1
            while (j < len(potential_headings) and 
                   potential_headings[j]["page"] == current["page"]):
                next_heading = potential_headings[j]
                
                # Only combine if:
                # 1. The next text doesn't start with a number (likely the continuation)
                # 2. There's no text between the number and the heading text
                if (not re.match(r"^[0-9]+[\.\s]", next_heading["text"]) and
                    not has_text_between_headings(current, next_heading, text_elements)):
                    combined_text = current["text"] + " " + next_heading["text"]
                    # Use H1 for main numbered sections
                    current["level"] = "H1"
                    j += 1
                    break
                else:
                    break
        else:
            # Look ahead for consecutive headings of same level and page for normal consolidation
            j = i + 1
            while (j < len(potential_headings) and 
                   potential_headings[j]["level"] == current["level"] and
                   potential_headings[j]["page"] == current["page"]):
                
                next_heading = potential_headings[j]
                
                # NEW LOGIC: Don't merge if next heading starts with a number
                if re.match(r'^\d+\.', next_heading["text"]):
                    break  # Don't merge headings that start with numbers
                
                # NEW LOGIC: Don't merge if there's text between the headings
                if has_text_between_headings(current, next_heading, text_elements):
                    break  # Don't merge if there's content between headings
                
                # More intelligent combination logic:
                # 1. Always combine if next text is very short (< 20 chars)
                # 2. Combine if next text doesn't start with a number/bullet
                # 3. Combine if current text doesn't end with a complete sentence (no period at end)
                # 4. Combine if both texts seem like parts of the same title/heading
                should_combine = False
                
                if len(next_heading["text"]) < 20:
                    should_combine = True  # Short text is likely a continuation
                elif not re.match(r'^\d+\.', next_heading["text"]):
                    # Not starting with number, check if current text seems incomplete
                    if not current["text"].rstrip().endswith('.'):
                        should_combine = True  # Current doesn't end with period, likely incomplete
                    # Also check if they look like title parts (both start with capital or "the")
                    elif (current["text"][0].isupper() and 
                          (next_heading["text"][0].isupper() or next_heading["text"].startswith("the"))):
                        should_combine = True
                
                if should_combine:
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

    # Convert special characters to hex in the final output
    final_title = convert_special_chars_to_hex(title if title else "Untitled Document")
    
    final_outline = []
    for item in outline:
        final_outline.append({
            "level": item["level"],
            "text": convert_special_chars_to_hex(item["text"]),
            "page": item["page"]
        })

    return {
        "title": final_title,
        "outline": final_outline
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