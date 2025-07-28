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

def is_table_of_contents_entry(text, page_num, all_text_elements):
    """
    Check if the text is likely a table of contents entry that should not be considered a heading
    """
    if not text:
        return False
    
    clean_text = text.strip().lower()
    
    # Check if we're on a likely Table of Contents page
    # Look for TOC indicators on this page
    page_elements = [elem for elem in all_text_elements if elem["page"] == page_num]
    page_text = " ".join([elem["text"].lower() for elem in page_elements])
    
    is_toc_page = (
        "table of contents" in page_text or
        "contents" in page_text or
        # Look for multiple page number references (common in TOC)
        len(re.findall(r'\b\d+\b', page_text)) > 10
    )
    
    if not is_toc_page:
        return False
    
    # If on TOC page, check for TOC entry patterns
    toc_patterns = [
        # Concatenated headings (shouldn't exist as real headings)
        r'\b(revision|table|contents|introduction|overview|acknowledgement|reference)\s+(history|of|to|level|foundation)\s+(table|contents|extensions|agile|tester)\b',
        # Text that appears to be merged/concatenated unnaturally
        r'\b\w+\s+\w+\s+\w+\s+\w+\s+\w+\s+\w+\s+\w+',  # Very long phrases (7+ words) are often merged TOC entries
        # Page number references at the end
        r'.+\s+\d+\s*$',
    ]
    
    for pattern in toc_patterns:
        if re.search(pattern, clean_text):
            return True
    
    # Additional check: if text contains multiple distinct topics, it's likely merged
    topic_keywords = ['introduction', 'overview', 'extension', 'tester', 'agile', 'foundation', 'level', 'syllabus']
    keyword_count = sum(1 for keyword in topic_keywords if keyword in clean_text)
    if keyword_count >= 3:  # Too many topics in one heading suggests merging
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
        
        # Government/official terms
        'officer', 'official', 'servant', 'employee', 'staff',
        'government', 'ministry', 'department', 'bureau', 'agency',
    }
    
    # Multi-word form field patterns that should be excluded
    form_field_patterns = [
        r'signature\s+of\s+',  # "Signature of Government Servant"
        r'name\s+of\s+',       # "Name of applicant"
        r'address\s+of\s+',    # "Address of employee"
        r'date\s+of\s+',       # "Date of application"
        r'place\s+of\s+',      # "Place of birth"
        r'certified\s+that',   # "Certified that..."
        r'i\s+hereby\s+',      # "I hereby certify..."
        r'this\s+is\s+to\s+',  # "This is to certify..."
        r'seal\s+of\s+',       # "Seal of office"
        r'stamp\s+of\s+',      # "Stamp of authority"
        r'approval\s+of\s+',   # "Approval of competent authority"
        r'recommendation\s+of\s+',  # "Recommendation of..."
        r'verified\s+by\s+',   # "Verified by..."
        r'checked\s+by\s+',    # "Checked by..."
        r'forwarded\s+',       # "Forwarded with recommendation"
        r'countersigned\s+',   # "Countersigned"
    ]
    
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
    
    # Check for multi-word form field patterns
    for pattern in form_field_patterns:
        if re.search(pattern, clean_text, re.IGNORECASE):
            return True
    
    return False

def apply_numbering_logic(outline):
    """
    Apply numbering logic from bottom to top:
    - If there is any X.1 and X. is not present, add X. to the above heading
    - If X. is present, add (X-1). in front of the above heading
    - Stop at 1.
    """
    if not outline:
        return outline
    
    # Work from bottom to top
    for i in range(len(outline) - 1, -1, -1):
        current_text = outline[i]["text"]
        
        # Check if current heading has pattern like "X.1", "X.2", etc.
        match = re.match(r'^(\d+)\.(\d+)', current_text)
        if match:
            main_num = int(match.group(1))
            sub_num = int(match.group(2))
            
            # Only process if this is a .1 subsection (first subsection)
            if sub_num == 1:
                # Look for the parent heading (the one above)
                if i > 0:
                    parent_text = outline[i-1]["text"]
                    
                    # Check if parent already has the main number
                    parent_match = re.match(r'^(\d+)\.\s', parent_text)
                    if parent_match:
                        parent_num = int(parent_match.group(1))
                        # If parent has a number, add (parent_num - 1) to the heading above it
                        if i > 1 and parent_num > 1:
                            grandparent_text = outline[i-2]["text"]
                            # Only add numbering if it doesn't already have it
                            if not re.match(r'^\d+\.', grandparent_text):
                                outline[i-2]["text"] = f"{parent_num - 1}. {grandparent_text}"
                    else:
                        # Parent doesn't have the main number, add it
                        outline[i-1]["text"] = f"{main_num}. {parent_text}"
    
    # Second pass: handle cases where we have numbered sections (like "2.") 
    # and need to add numbers to headings above them
    for i in range(len(outline) - 1, -1, -1):
        current_text = outline[i]["text"]
        
        # Check if current heading has pattern like "X. Title" (main section)
        match = re.match(r'^(\d+)\.\s', current_text)
        if match:
            main_num = int(match.group(1))
            
            # If this is section 2 or higher, add numbering to the heading above it
            if main_num >= 2 and i > 0:
                parent_text = outline[i-1]["text"]
                # Only add numbering if it doesn't already have it and we haven't reached "1."
                if not re.match(r'^\d+\.', parent_text) and main_num > 1:
                    outline[i-1]["text"] = f"{main_num - 1}. {parent_text}"
    
    return outline

def detect_table_regions(text_elements):
    """
    Advanced table detection that identifies table regions using multiple heuristics:
    1. Regular column alignment patterns
    2. Repeating structural patterns
    3. High density of short text elements
    4. Consistent spacing patterns
    5. Tabular data characteristics (numbers, short phrases)
    """
    table_regions = []
    
    if not text_elements:
        return table_regions
    
    # Group text elements by page
    pages = {}
    for element in text_elements:
        page_num = element["page"]
        if page_num not in pages:
            pages[page_num] = []
        pages[page_num].append(element)
    
    for page_num, page_elements in pages.items():
        # Sort elements by Y position (top to bottom)
        page_elements.sort(key=lambda x: x["y_position"])
        
        # Detect table regions on this page
        page_table_regions = detect_tables_on_page(page_elements, page_num)
        table_regions.extend(page_table_regions)
    
    return table_regions

def detect_tables_on_page(elements, page_num):
    """
    Detect table regions on a single page using advanced heuristics
    """
    table_regions = []
    
    if len(elements) < 6:  # Too few elements to form a meaningful table
        return table_regions
    
    # Group elements into potential rows based on Y-coordinate proximity
    rows = group_elements_into_rows(elements)
    
    # Analyze each group of consecutive rows for table characteristics
    i = 0
    while i < len(rows):
        table_start = i
        table_end = i
        
        # Look for consecutive rows that show table characteristics
        consecutive_table_rows = 0
        max_consecutive = 0
        
        for j in range(i, min(i + 20, len(rows))):  # Look ahead up to 20 rows
            if is_table_row(rows[j], rows[max(0, j-2):j+3]):  # Consider context of ±2 rows
                consecutive_table_rows += 1
                max_consecutive = max(max_consecutive, consecutive_table_rows)
                table_end = j
            else:
                consecutive_table_rows = 0
        
        # If we found enough consecutive table-like rows, mark it as a table region
        if max_consecutive >= 4:  # Increased from 3 to 4 - require more evidence for table detection
            # Additional validation: ensure this looks like a real table
            table_rows = rows[table_start:table_end+1]
            if validate_table_region(table_rows):
                table_regions.append({
                    "page": page_num,
                    "start_row": table_start,
                    "end_row": table_end,
                    "y_start": rows[table_start][0]["y_position"] if rows[table_start] else 0,
                    "y_end": rows[table_end][-1]["y_position"] if rows[table_end] else 0,
                    "elements": [elem for row in rows[table_start:table_end+1] for elem in row]
                })
            i = table_end + 1
        else:
            i += 1
    
    return table_regions

def validate_table_region(table_rows):
    """
    Additional validation to ensure a detected region is actually a table
    """
    if not table_rows or len(table_rows) < 3:
        return False
    
    # Check for consistent column structure
    column_counts = [len(row) for row in table_rows]
    avg_columns = sum(column_counts) / len(column_counts)
    
    # Tables should have relatively consistent column counts
    consistent_columns = sum(1 for count in column_counts if abs(count - avg_columns) <= 1)
    if consistent_columns / len(column_counts) < 0.7:
        return False
    
    # Check for data-like content (not just text)
    data_elements = 0
    total_elements = 0
    
    for row in table_rows:
        for elem in row:
            total_elements += 1
            text = elem["text"].strip()
            
            # Look for typical table content
            if (text.isdigit() or
                re.match(r'^\d+\.\d+$', text) or
                text in ['Yes', 'No', 'True', 'False', 'N/A', '-', ''] or
                len(text) <= 10):
                data_elements += 1
    
    # At least 40% of elements should look like table data
    if total_elements > 0 and data_elements / total_elements < 0.4:
        return False
    
    return True

def group_elements_into_rows(elements, y_threshold=3):
    """
    Group text elements into rows based on Y-coordinate proximity
    """
    if not elements:
        return []
    
    rows = []
    current_row = [elements[0]]
    current_y = elements[0]["y_position"]
    
    for element in elements[1:]:
        # If Y-position is close enough, add to current row
        if abs(element["y_position"] - current_y) <= y_threshold:
            current_row.append(element)
        else:
            # Start new row
            if current_row:
                # Sort row elements by X position (left to right)
                current_row.sort(key=lambda x: x["x_position"])
                rows.append(current_row)
            current_row = [element]
            current_y = element["y_position"]
    
    # Add the last row
    if current_row:
        current_row.sort(key=lambda x: x["x_position"])
        rows.append(current_row)
    
    return rows

def is_table_row(row, context_rows):
    """
    Determine if a row of text elements represents a table row
    using multiple sophisticated heuristics with improved accuracy
    """
    if not row or len(row) < 2:
        return False
    
    # Enhanced exclusion checks for obvious non-table content
    if is_obviously_not_table_row(row):
        return False
    
    # Heuristic 1: Column alignment detection
    column_alignment_score = calculate_column_alignment_score(row, context_rows)
    
    # Heuristic 2: Text characteristics (short, structured text)
    text_characteristics_score = calculate_text_characteristics_score(row)
    
    # Heuristic 3: Spacing regularity
    spacing_regularity_score = calculate_spacing_regularity_score(row)
    
    # Heuristic 4: Data pattern recognition (numbers, dates, structured data)
    data_pattern_score = calculate_data_pattern_score(row)
    
    # Heuristic 5: Font consistency (tables often use consistent fonts)
    font_consistency_score = calculate_font_consistency_score(row)
    
    # Combine scores with weights
    total_score = (
        column_alignment_score * 0.3 +
        text_characteristics_score * 0.25 +
        spacing_regularity_score * 0.2 +
        data_pattern_score * 0.15 +
        font_consistency_score * 0.1
    )
    
    # Higher threshold for considering a row as part of a table
    return total_score > 0.7

def is_obviously_not_table_row(row):
    """
    Check if this row is obviously not part of a table
    """
    if not row:
        return True
        
    # If row has only one element, it's likely not a table row
    if len(row) == 1:
        single_text = row[0]["text"].strip()
        
        # Check if it's a heading-like text
        if (len(single_text) > 30 or  # Long text is usually not table content
            re.match(r'^\d+(\.\d+)*\.?\s+[A-Z]', single_text) or  # Section numbering
            single_text.count(' ') > 5):  # Many words
            return True
    
    # Check if all elements in the row are very long text (likely paragraphs, not table)
    long_text_count = 0
    for elem in row:
        text = elem["text"].strip()
        if len(text) > 50 or text.count(' ') > 8:
            long_text_count += 1
    
    # If most elements are long text, it's likely not a table
    if long_text_count / len(row) > 0.6:
        return True
    
    # Check for obvious heading patterns
    for elem in row:
        text = elem["text"].strip()
        # Common heading patterns
        if (text.lower().startswith(('chapter', 'section', 'part', 'appendix', 'introduction', 'conclusion', 'summary', 'overview')) or
            re.match(r'^\d+\.\s+[A-Z][a-z]', text)):  # "1. Introduction" pattern
            return True
    
    return False

def calculate_column_alignment_score(row, context_rows):
    """
    Calculate how well this row aligns with columns in context rows
    """
    if not context_rows:
        return 0.0
    
    # Get X positions of elements in this row
    row_x_positions = [elem["x_position"] for elem in row]
    
    # Get X positions from context rows
    context_x_positions = []
    for context_row in context_rows:
        if context_row != row:  # Exclude the current row
            context_x_positions.extend([elem["x_position"] for elem in context_row])
    
    if not context_x_positions:
        return 0.0
    
    # Count how many elements align with context positions (within tolerance)
    alignment_tolerance = 5  # pixels
    aligned_count = 0
    
    for x_pos in row_x_positions:
        for context_x in context_x_positions:
            if abs(x_pos - context_x) <= alignment_tolerance:
                aligned_count += 1
                break
    
    return aligned_count / len(row_x_positions) if row_x_positions else 0.0

def calculate_text_characteristics_score(row):
    """
    Calculate score based on text characteristics typical of table cells
    """
    if not row:
        return 0.0
    
    score = 0.0
    total_elements = len(row)
    
    for elem in row:
        text = elem["text"].strip()
        
        # Short text segments are common in tables
        if 1 <= len(text) <= 20:
            score += 0.3
        
        # Single words or short phrases
        if len(text.split()) <= 3:
            score += 0.2
        
        # Numbers, dates, or structured data
        if re.search(r'\d', text):
            score += 0.3
        
        # Common table content patterns
        if re.match(r'^[A-Z]{1,5}$', text):  # Abbreviations
            score += 0.2
        
        # Currency, percentages, measurements
        if re.search(r'[\$€£%]|\b\d+\.\d+\b', text):
            score += 0.4
    
    return min(score / total_elements, 1.0)

def calculate_spacing_regularity_score(row):
    """
    Calculate score based on regular spacing between elements
    """
    if len(row) < 3:
        return 0.0
    
    # Calculate gaps between consecutive elements
    gaps = []
    for i in range(len(row) - 1):
        gap = row[i + 1]["x_position"] - (row[i]["x_position"] + 50)  # Approximate text width
        gaps.append(gap)
    
    if not gaps:
        return 0.0
    
    # Calculate coefficient of variation (std/mean) - lower is more regular
    import statistics
    try:
        mean_gap = statistics.mean(gaps)
        if mean_gap == 0:
            return 1.0 if all(g == 0 for g in gaps) else 0.0
        
        std_gap = statistics.stdev(gaps) if len(gaps) > 1 else 0
        cv = std_gap / abs(mean_gap)
        
        # Convert to score (lower CV = higher score)
        return max(0.0, 1.0 - cv)
    except:
        return 0.0

def calculate_data_pattern_score(row):
    """
    Calculate score based on structured data patterns common in tables
    """
    if not row:
        return 0.0
    
    score = 0.0
    total_elements = len(row)
    
    for elem in row:
        text = elem["text"].strip()
        
        # Numbers (including decimals)
        if re.match(r'^\d+(\.\d+)?$', text):
            score += 0.5
        
        # Dates
        if re.search(r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}', text):
            score += 0.4
        
        # Currency
        if re.search(r'[\$€£]\s*\d+', text):
            score += 0.4
        
        # Percentages
        if re.search(r'\d+%', text):
            score += 0.4
        
        # Yes/No, True/False type values
        if text.lower() in ['yes', 'no', 'true', 'false', 'y', 'n', 'x', '✓', '✗']:
            score += 0.3
        
        # Short codes or IDs
        if re.match(r'^[A-Z0-9\-_]{2,10}$', text):
            score += 0.2
    
    return min(score / total_elements, 1.0)

def calculate_font_consistency_score(row):
    """
    Calculate score based on font consistency within the row
    """
    if not row:
        return 0.0
    
    # Check if all elements have the same font size
    sizes = [elem["size"] for elem in row]
    if len(set(sizes)) == 1:
        return 1.0
    
    # Check if sizes are very close
    import statistics
    if len(sizes) > 1:
        try:
            mean_size = statistics.mean(sizes)
            if mean_size > 0:
                cv = statistics.stdev(sizes) / mean_size
                return max(0.0, 1.0 - cv * 2)  # Penalize size variation
        except:
            pass
    
    return 0.0

def is_text_in_table(element, table_regions):
    """
    Advanced check if a text element is within any detected table region.
    Uses multiple criteria to avoid false positives with headings.
    """
    for table in table_regions:
        if element["page"] != table["page"]:
            continue
            
        # Basic Y-coordinate check first
        if not (table["y_start"] <= element["y_position"] <= table["y_end"]):
            continue
            
        # Advanced checks to avoid classifying headings as table content:
        
        # 1. Check if this element looks like a heading based on text characteristics
        text = element.get("text", "").strip()
        if is_likely_heading_text(text):
            # Additional validation: check if element is truly embedded within table structure
            if not is_truly_embedded_in_table(element, table):
                continue
        
        # 2. Check X-position alignment with table columns
        # Headings often span multiple columns or are outside column boundaries
        if is_spanning_multiple_columns(element, table):
            continue
            
        # 3. Check font characteristics relative to table content
        if has_heading_font_characteristics(element, table):
            continue
            
        # 4. Check isolation - headings are often isolated from dense table content
        if is_isolated_from_table_content(element, table):
            continue
            
        # If all checks pass, the element is likely within a table
        return True
    
    return False

def is_likely_heading_text(text):
    """
    Check if text has characteristics typical of headings
    """
    if not text:
        return False
        
    # Remove leading/trailing whitespace and normalize
    clean_text = text.strip()
    
    # Headings often have:
    # 1. Proper capitalization patterns
    # 2. Meaningful length (not too short, not too long)
    # 3. Descriptive words rather than data
    # 4. Section numbering patterns
    
    # Check for section numbering
    if re.match(r'^\d+(\.\d+)*\.?\s', clean_text):
        return True
        
    # Check for title case or sentence case
    words = clean_text.split()
    if len(words) >= 2:
        # Check if it's title case (most words capitalized)
        capitalized_words = sum(1 for word in words if word[0].isupper() and len(word) > 2)
        if capitalized_words / len(words) > 0.5:
            return True
            
    # Check for common heading keywords
    heading_keywords = [
        'introduction', 'overview', 'summary', 'conclusion', 'background',
        'methodology', 'results', 'discussion', 'references', 'appendix',
        'chapter', 'section', 'part', 'acknowledgements', 'abstract',
        'contents', 'objectives', 'requirements', 'specifications',
        'implementation', 'analysis', 'evaluation', 'recommendations'
    ]
    
    for keyword in heading_keywords:
        if keyword in clean_text.lower():
            return True
            
    return False

def is_truly_embedded_in_table(element, table):
    """
    Check if element is truly embedded within table structure
    """
    # Get surrounding elements in the table
    table_elements = table.get("elements", [])
    
    # Check if there are table-like elements (numbers, short text) very close to this element
    close_elements = []
    element_y = element["y_position"]
    element_x = element["x_position"]
    
    for table_elem in table_elements:
        if (abs(table_elem["y_position"] - element_y) <= 5 and  # Same row
            abs(table_elem["x_position"] - element_x) > 20):    # Different column
            close_elements.append(table_elem)
    
    # If there are many close elements with table-like characteristics, it's embedded
    if len(close_elements) >= 2:
        table_like_count = 0
        for elem in close_elements:
            elem_text = elem.get("text", "").strip()
            # Check for typical table content (numbers, short text, etc.)
            if (elem_text.isdigit() or 
                len(elem_text) <= 15 or 
                re.match(r'^\d+(\.\d+)?$', elem_text) or
                elem_text.lower() in ['yes', 'no', 'true', 'false', 'n/a', '-']):
                table_like_count += 1
        
        return table_like_count >= len(close_elements) * 0.6
    
    return False

def is_spanning_multiple_columns(element, table):
    """
    Check if element spans multiple columns (typical for headings)
    """
    table_elements = table.get("elements", [])
    
    # Find typical column positions in the table
    x_positions = [elem["x_position"] for elem in table_elements]
    if len(x_positions) < 4:  # Need enough elements to determine columns
        return False
    
    # Find common X positions (columns)
    x_positions.sort()
    columns = []
    current_col = x_positions[0]
    columns.append(current_col)
    
    for x in x_positions[1:]:
        if x - current_col > 30:  # Significant gap indicates new column
            columns.append(x)
            current_col = x
    
    if len(columns) < 2:  # Not enough columns to determine spanning
        return False
    
    # Check if element's text width would span multiple columns
    element_text = element.get("text", "")
    estimated_width = len(element_text) * 6  # Rough estimate of text width
    
    # Check if element starts before first column and extends beyond second column
    element_x = element["x_position"]
    if (element_x <= columns[0] + 10 and  # Starts near or before first column
        element_x + estimated_width >= columns[1] - 10):  # Extends to second column
        return True
    
    return False

def has_heading_font_characteristics(element, table):
    """
    Check if element has font characteristics typical of headings vs table content
    """
    table_elements = table.get("elements", [])
    
    # Get font sizes in the table
    table_font_sizes = [elem.get("size", 12) for elem in table_elements if "size" in elem]
    
    if not table_font_sizes:
        return False
    
    avg_table_font_size = sum(table_font_sizes) / len(table_font_sizes)
    element_font_size = element.get("size", 12)
    
    # If element font is significantly larger than average table font, it's likely a heading
    if element_font_size > avg_table_font_size * 1.2:
        return True
    
    return False

def is_isolated_from_table_content(element, table):
    """
    Check if element is isolated from dense table content
    """
    table_elements = table.get("elements", [])
    element_y = element["y_position"]
    
    # Count elements very close to this element (same row area)
    close_elements = 0
    for table_elem in table_elements:
        if abs(table_elem["y_position"] - element_y) <= 3:
            close_elements += 1
    
    # If there are very few elements on the same row, it might be an isolated heading
    return close_elements <= 2

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

    # --- DETECT TABLE REGIONS ---
    # Perform advanced table detection before processing headings
    table_regions = detect_table_regions(text_elements)
    
    # Optional: Log table detection results for debugging
    if table_regions:
        print(f"  Detected {len(table_regions)} table regions in {pdf_path}")
        for i, table in enumerate(table_regions):
            print(f"    Table {i+1}: Page {table['page']}, Y-range: {table['y_start']:.1f}-{table['y_end']:.1f}, Elements: {len(table['elements'])}")
    
    # --- 2. Determine title & heading levels ---
    sizes = [t["size"] for t in text_elements if len(t["text"]) > 3]
    most_common = Counter(sizes).most_common()
    body_text_size = most_common[0][0]  # most frequent = normal text size

    # Sort unique sizes (largest first)
    unique_sizes = sorted(set(sizes), reverse=True)
    heading_levels = {}
    level_names = ["H1", "H2", "H3", "H4"]

    # More sophisticated heading detection that considers both font size AND formatting
    title_size = unique_sizes[0] if unique_sizes else body_text_size
    
    # Instead of just using the largest sizes, consider:
    # 1. Sizes significantly larger than body text
    # 2. Sizes that appear with bold formatting frequently
    
    # Analyze which font sizes are used with bold formatting
    bold_font_usage = {}
    for t in text_elements:
        size = t["size"]
        is_bold = t.get("flags", 0) & 16  # Bold flag
        if size not in bold_font_usage:
            bold_font_usage[size] = {"total": 0, "bold": 0}
        bold_font_usage[size]["total"] += 1
        if is_bold:
            bold_font_usage[size]["bold"] += 1
    
    # Find sizes that are frequently used with bold (likely heading sizes)
    heading_candidate_sizes = []
    
    # Add sizes significantly larger than body text
    for sz in unique_sizes:
        if sz > body_text_size * 1.2:  # 20% larger than body text
            heading_candidate_sizes.append(sz)
    
    # Add sizes that are frequently bold (even if not much larger)
    for size, usage in bold_font_usage.items():
        if usage["total"] >= 3 and usage["bold"] / usage["total"] > 0.5:  # More than 50% bold usage
            if size >= body_text_size * 0.9 and size not in heading_candidate_sizes:  # At least 90% of body text size
                heading_candidate_sizes.append(size)
    
    # Sort by size (largest first) and assign levels
    heading_candidate_sizes = sorted(set(heading_candidate_sizes), reverse=True)
    
    # Skip the absolute largest size (likely title) but include others
    for i, sz in enumerate(heading_candidate_sizes):
        if sz == title_size:
            continue  # Skip title size
        if len(heading_levels) < len(level_names):
            heading_levels[sz] = level_names[len(heading_levels)]

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
        
        # Check if this is a table of contents entry (exclude from headings)
        is_toc_entry = is_table_of_contents_entry(text, t["page"], text_elements) or is_table_of_contents_entry(clean_text, t["page"], text_elements)
        
        # Additional check for table-like content
        is_table_like_content = (
            re.match(r'^[\.\u2026\s]+$', clean_text) or  # Just dots/ellipsis (using Unicode)
            re.match(r'^[A-Z]\.?[A-Z]?\.?[A-Z]?o?\.?$', clean_text) or  # Abbreviations like "S.No"
            clean_text.lower() in ['s.no', 'sl.no', 'sr.no', 'no.', 'sn', 'amount', 'total', 'subtotal'] or
            len(clean_text) == 1 or  # Single characters
            (len(clean_text.split()) == 1 and len(clean_text) <= 4)  # Very short single words
        )

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

        # Check if this text is within a detected table region
        in_table = is_text_in_table(t, table_regions)

        # Enhanced heading detection: consider both font size AND bold formatting, but with strict filtering
        is_bold = t.get("flags", 0) & 16  # Bold flag
        is_heading_size = t["size"] in heading_levels
        
        # More restrictive criteria for bold-based heading detection
        is_potential_heading_by_formatting = (
            is_bold and 
            t["size"] >= body_text_size * 1.0 and  # At least body text size
            len(clean_text.split()) >= 2 and  # At least 2 words (exclude "S.No", single words)
            len(clean_text.split()) <= 12 and  # Reasonable heading length
            not re.match(r'^[A-Z]\.?[A-Z]?\.?[A-Z]?o?\.?$', clean_text) and  # Exclude abbreviations like "S.No"
            not clean_text.lower() in ['name', 'date', 'signature', 'remarks', 'amount', 'total'] and  # Exclude form fields
            not re.match(r'^[\.\u2026]+$', clean_text) and  # Exclude dots/ellipsis
            not re.match(r'^[\.\u2026\s]+$', clean_text)  # Exclude dots/ellipsis with spaces
        )

        # Collect potential heading elements, but exclude:
        # 1. Text that appears too frequently (more than 5 times anywhere in the PDF)
        # 2. Any text containing dates in any format (comprehensive date detection)
        # 3. Form fields and generic single-word terms (name, date, address, etc.)
        # 4. Text that appears above the title
        # 5. Text that appears within detected table regions
        # 6. Table-like content (dots, abbreviations, single words)
        # 7. Table of contents entries
        if ((is_heading_size or is_potential_heading_by_formatting) and 
            clean_text and 
            clean_text not in title_components and
            all_text_frequency[clean_text] <= 5 and  # Changed from 3 to 5 and using all_text_frequency
            not is_date and  # Exclude dates from headings
            not is_form_field and  # Exclude form fields and generic terms
            not is_toc_entry and  # Exclude table of contents entries
            not is_table_like_content and  # Exclude table-like content
            not above_title and  # Exclude headings above the title
            not in_table):  # Exclude text within table regions
            
            # Determine heading level
            if is_heading_size:
                level = heading_levels[t["size"]]
            else:
                # For bold formatting headings, assign level based on context
                if t["size"] > body_text_size * 1.1:
                    level = "H2"
                elif text.strip().endswith(':') or len(text.strip().split()) <= 5:
                    level = "H3"
                else:
                    level = "H4"
            
            potential_headings.append({
                "level": level,
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
                
                # IMPROVED LOGIC: Be much more conservative about merging
                
                # 1. Never merge if next heading starts with a number
                if re.match(r'^\d+\.', next_heading["text"]):
                    break  # Don't merge headings that start with numbers
                
                # 2. Never merge if there's text between the headings
                if has_text_between_headings(current, next_heading, text_elements):
                    break  # Don't merge if there's content between headings
                
                # 3. Never merge if either heading contains multiple distinct topics
                current_topics = sum(1 for keyword in ['introduction', 'overview', 'extension', 'tester', 'agile', 'foundation', 'level', 'syllabus', 'history', 'contents'] 
                                   if keyword in current["text"].lower())
                next_topics = sum(1 for keyword in ['introduction', 'overview', 'extension', 'tester', 'agile', 'foundation', 'level', 'syllabus', 'history', 'contents'] 
                                if keyword in next_heading["text"].lower())
                
                if current_topics >= 2 or next_topics >= 2:
                    break  # Don't merge if either has multiple topics (likely already merged incorrectly)
                
                # 4. Never merge if combined length would be excessive
                if len(combined_text + " " + next_heading["text"]) > 100:
                    break  # Don't create overly long headings
                
                # 5. Only merge in very specific cases
                should_combine = False
                
                # Case 1: Next text is very short (< 15 chars) and current doesn't end properly
                if (len(next_heading["text"]) < 15 and 
                    not current["text"].rstrip().endswith(('.', ':', '!', '?'))):
                    should_combine = True
                
                # Case 2: Current text ends with a conjunction or preposition (incomplete)
                elif re.search(r'\b(and|or|of|to|for|with|in|on|at|by|from)\s*$', current["text"].lower()):
                    should_combine = True
                
                # Case 3: Very specific patterns that are clearly split words
                elif (len(current["text"].split()) == 1 and len(next_heading["text"].split()) == 1 and
                      len(current["text"]) < 10 and len(next_heading["text"]) < 10):
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

    # Remove duplicate headings (same text, keep the first occurrence)
    deduplicated_outline = []
    seen_texts = set()
    for item in outline:
        if item["text"] not in seen_texts:
            deduplicated_outline.append(item)
            seen_texts.add(item["text"])
    
    outline = deduplicated_outline

    # Apply numbering logic from bottom to top
    outline = apply_numbering_logic(outline)

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