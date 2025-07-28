#!/usr/bin/env python3
"""
Debug script to analyze why the "Background" heading in file04.pdf is not being detected.
This will trace through the entire heading detection pipeline to find where it gets eliminated.
"""

import fitz
import json
import re
from collections import Counter, defaultdict

def debug_background_heading_file04():
    pdf_path = 'sample_dataset/pdfs/file04.pdf'
    doc = fitz.open(pdf_path)
    
    print("=== DEBUGGING BACKGROUND HEADING DETECTION IN FILE04.PDF ===\n")
    
    # Step 1: Find all text elements containing "background" (broader search)
    background_elements = []
    all_text_elements = []
    similar_words = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text('dict')['blocks']
        
        for block in blocks:
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text'].strip()
                        if text:
                            element = {
                                'text': text,
                                'page': page_num + 1,
                                'size': span['size'],
                                'font': span['font'],
                                'flags': span['flags'],
                                'bbox': span['bbox'],
                                'x_position': span['bbox'][0],
                                'y_position': span['bbox'][1],
                                'relative_x': span['bbox'][0] / page.rect.width if page.rect.width > 0 else 0,
                                'is_bold': bool(span['flags'] & 16)
                            }
                            all_text_elements.append(element)
                            
                            # Broader search for background-related terms
                            text_lower = text.lower()
                            if any(term in text_lower for term in ['background', 'back ground', 'backgr']):
                                background_elements.append(element)
                            
                            # Look for similar words that might be headings
                            if any(term in text_lower for term in ['summary', 'intro', 'overview', 'context', 'history']):
                                similar_words.append(element)
    
    print(f"Found {len(background_elements)} text elements containing 'background' variants:")
    for i, elem in enumerate(background_elements):
        print(f"\n{i+1}. Text: '{elem['text']}'")
        print(f"   Page: {elem['page']}")
        print(f"   Font: {elem['font']}, Size: {elem['size']}")
        print(f"   Bold: {elem['is_bold']} (flags: {elem['flags']})")
        print(f"   Position: x={elem['x_position']:.1f}, y={elem['y_position']:.1f}")
        print(f"   Relative X: {elem['relative_x']:.3f}")
    
    if similar_words:
        print(f"\nFound {len(similar_words)} similar heading-like words:")
        for i, elem in enumerate(similar_words):
            print(f"  {i+1}. '{elem['text']}' (page {elem['page']}, size {elem['size']}, bold: {elem['is_bold']})")
    
    # Show first 50 text elements to understand document structure
    print(f"\n=== FIRST 50 TEXT ELEMENTS IN FILE04.PDF ===")
    for i, elem in enumerate(all_text_elements[:50]):
        text_preview = elem['text'][:50] + ('...' if len(elem['text']) > 50 else '')
        print(f"{i+1:2d}. Page {elem['page']}: '{text_preview}' (size: {elem['size']}, bold: {elem['is_bold']})")
    
    if len(all_text_elements) > 50:
        print(f"... and {len(all_text_elements) - 50} more elements")
    
    if not background_elements:
        print("\n❌ NO 'background' variants found in file04.pdf!")
        print("Let's check if there are any potential heading-like elements...")
        
        # Look for potential headings by size and formatting
        potential_headings = []
        font_sizes = [elem['size'] for elem in all_text_elements]
        size_counter = Counter(font_sizes)
        body_text_size = size_counter.most_common(1)[0][0] if size_counter else 12
        
        for elem in all_text_elements:
            if (elem['size'] > body_text_size or elem['is_bold']) and len(elem['text'].split()) <= 5:
                potential_headings.append(elem)
        
        print(f"\nPotential headings found (large size or bold, ≤5 words): {len(potential_headings)}")
        for i, elem in enumerate(potential_headings[:20]):  # Show first 20
            print(f"  {i+1}. '{elem['text']}' (page {elem['page']}, size {elem['size']}, bold: {elem['is_bold']})")
        
        if len(potential_headings) > 20:
            print(f"  ... and {len(potential_headings) - 20} more potential headings")
        
        doc.close()
        return
    
    # Step 2: Analyze document structure (body text size, heading levels, etc.)
    print("\n=== DOCUMENT STRUCTURE ANALYSIS ===")
    
    # Get body text size and heading levels (simplified logic from your code)
    font_sizes = [elem['size'] for elem in all_text_elements]
    size_counter = Counter(font_sizes)
    body_text_size = size_counter.most_common(1)[0][0]
    
    print(f"Font size distribution:")
    for size, count in sorted(size_counter.items(), key=lambda x: x[1], reverse=True):
        print(f"  Size {size}: {count} elements ({count/len(all_text_elements)*100:.1f}%)")
    
    print(f"\nBody text size (most common): {body_text_size}")
    
    # Get heading levels (sizes used less frequently, typically larger)
    size_frequency = {size: count for size, count in size_counter.items()}
    heading_levels = {}
    for size, count in size_frequency.items():
        if size > body_text_size and count <= len(all_text_elements) * 0.1:
            if size >= body_text_size * 1.4:
                heading_levels[size] = "H1"
            elif size >= body_text_size * 1.2:
                heading_levels[size] = "H2"
            else:
                heading_levels[size] = "H3"
    
    print(f"Detected heading levels: {heading_levels}")
    
    # Check frequency of all text
    all_text_frequency = Counter([elem['text'].strip() for elem in all_text_elements])
    
    # Analyze special font usage
    special_font_elements = 0
    for elem in all_text_elements:
        font_family = elem['font'].lower()
        if any(indicator in font_family for indicator in ['black', 'bold', 'heavy', 'semibold']):
            special_font_elements += 1
    
    print(f"Special font elements in document: {special_font_elements}")
    
    # Step 3: Test each background element against ALL filtering criteria
    for i, elem in enumerate(background_elements):
        print(f"\n{'='*60}")
        print(f"ANALYZING BACKGROUND ELEMENT {i+1}: '{elem['text']}'")
        print(f"{'='*60}")
        
        text = elem['text']
        clean_text = text.strip()
        elimination_reasons = []
        passes_criteria = []
        
        # ===== BASIC FORMATTING CRITERIA =====
        print(f"\n--- BASIC FORMATTING CRITERIA ---")
        
        # Test 1: Font size criteria
        is_heading_size = elem['size'] in heading_levels
        size_ratio = elem['size'] / body_text_size
        print(f"✓ Font size: {elem['size']} (ratio: {size_ratio:.2f})")
        print(f"  Is heading size: {is_heading_size} (in {list(heading_levels.keys())})")
        if is_heading_size:
            passes_criteria.append("heading_size")
        
        # Test 2: Bold formatting
        is_bold = elem['is_bold']
        print(f"✓ Bold formatting: {is_bold} (flags: {elem['flags']})")
        if is_bold:
            passes_criteria.append("bold")
        
        # Test 3: Special font family
        font_family = elem['font'].lower()
        is_special_font = any(indicator in font_family for indicator in ['black', 'bold', 'heavy', 'semibold'])
        print(f"✓ Special font: {is_special_font} (font: {elem['font']})")
        if is_special_font:
            passes_criteria.append("special_font")
        
        # Test 4: Size relative to body text
        is_size_adequate_standard = elem['size'] >= body_text_size * 1.0
        is_size_adequate_special = elem['size'] >= body_text_size * 0.95
        print(f"✓ Size adequacy: standard={is_size_adequate_standard} (≥{body_text_size*1.0:.1f}), special={is_size_adequate_special} (≥{body_text_size*0.95:.1f})")
        
        # ===== POTENTIAL HEADING BY FORMATTING =====
        print(f"\n--- FORMATTING-BASED HEADING DETECTION ---")
        
        # Standard bold criteria
        standard_criteria = (
            is_bold and
            elem['size'] >= body_text_size * 1.0 and
            len(clean_text.split()) >= 2 and
            len(clean_text.split()) <= 12 and
            not re.match(r'^[A-Z]\.?[A-Z]?\.?[A-Z]?o?\.?$', clean_text) and
            not clean_text.lower() in ['name', 'date', 'signature', 'remarks', 'amount', 'total'] and
            not re.match(r'^[\.\u2026]+$', clean_text) and
            not re.match(r'^[\.\u2026\s]+$', clean_text)
        )
        
        # Special font criteria (for documents with special fonts)
        special_font_criteria = (
            is_special_font and
            special_font_elements >= 3 and
            elem['size'] >= body_text_size * 0.95 and
            len(clean_text.split()) >= 1 and
            len(clean_text.split()) <= 8 and
            not re.match(r'^[A-Z]\.?[A-Z]?\.?[A-Z]?o?\.?$', clean_text) and
            not clean_text.lower() in ['name', 'date', 'signature', 'remarks', 'amount', 'total'] and
            not re.match(r'^[\.\u2026]+$', clean_text) and
            not re.match(r'^[\.\u2026\s]+$', clean_text)
        )
        
        is_potential_heading_by_formatting = standard_criteria or special_font_criteria
        
        print(f"Standard criteria: {standard_criteria}")
        print(f"  - Bold: {is_bold}")
        print(f"  - Size ≥ body: {elem['size'] >= body_text_size * 1.0}")
        print(f"  - Word count 2-12: {2 <= len(clean_text.split()) <= 12} ({len(clean_text.split())} words)")
        
        print(f"Special font criteria: {special_font_criteria}")
        print(f"  - Special font: {is_special_font}")
        print(f"  - Doc has ≥3 special fonts: {special_font_elements >= 3}")
        print(f"  - Size ≥ 95% body: {elem['size'] >= body_text_size * 0.95}")
        print(f"  - Word count 1-8: {1 <= len(clean_text.split()) <= 8} ({len(clean_text.split())} words)")
        
        print(f"RESULT: Is potential heading by formatting: {is_potential_heading_by_formatting}")
        if is_potential_heading_by_formatting:
            passes_criteria.append("formatting_based")
        else:
            elimination_reasons.append("Failed formatting criteria")
        
        # ===== EXCLUSION CRITERIA =====
        print(f"\n--- EXCLUSION CRITERIA ---")
        
        # Test: Word count
        word_count = len(clean_text.split())
        is_word_count_ok = 1 <= word_count <= 12
        print(f"✓ Word count: {word_count} words (1-12 allowed): {is_word_count_ok}")
        if not is_word_count_ok:
            elimination_reasons.append(f"Word count {word_count} outside 1-12 range")
        
        # Test: Frequency check
        frequency = all_text_frequency[clean_text]
        is_frequency_ok = frequency <= 5
        print(f"✓ Frequency: appears {frequency} times (≤5 allowed): {is_frequency_ok}")
        if not is_frequency_ok:
            elimination_reasons.append(f"Text appears {frequency} times (>5)")
        
        # Test: Form field detection
        form_field_patterns = [
            (r'^(name|date|signature|remarks|amount|total|address|phone|email)$', 'common form field'),
            (r'^[A-Z]\.?[A-Z]?\.?[A-Z]?o?\.?$', 'abbreviation pattern'),
            (r'^\d+[\.\)]\s*$', 'numbering pattern'),
            (r'^[\.\u2026]+$', 'dots/ellipsis')
        ]
        
        is_form_field = False
        form_field_reason = None
        for pattern, reason in form_field_patterns:
            if re.match(pattern, clean_text, re.IGNORECASE):
                is_form_field = True
                form_field_reason = reason
                break
        
        print(f"✓ Form field check: {is_form_field}" + (f" ({form_field_reason})" if form_field_reason else ""))
        if is_form_field:
            elimination_reasons.append(f"Matches form field pattern: {form_field_reason}")
        
        # Test: Date detection
        date_patterns = [
            (r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', 'date format'),
            (r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b', 'month name'),
            (r'\b\d{4}\b', 'year'),
            (r'\b©\s*\d{4}\b', 'copyright year'),
            (r'\bCopyright\s+\d{4}\b', 'copyright text')
        ]
        
        is_date = False
        date_reason = None
        for pattern, reason in date_patterns:
            if re.search(pattern, clean_text, re.IGNORECASE):
                is_date = True
                date_reason = reason
                break
        
        print(f"✓ Date detection: {is_date}" + (f" ({date_reason})" if date_reason else ""))
        if is_date:
            elimination_reasons.append(f"Contains date pattern: {date_reason}")
        
        # Test: Table-like content
        table_patterns = [
            (r'^[\.\u2026\s]+$', 'dots/ellipsis with spaces'),
            (r'^[A-Z]\.?[A-Z]?\.?[A-Z]?o?\.?$', 'abbreviation'),
            (lambda t: len(t.split()) == 1 and len(t) <= 3, 'very short single word')
        ]
        
        is_table_like = False
        table_reason = None
        for test, reason in table_patterns:
            if callable(test):
                if test(clean_text):
                    is_table_like = True
                    table_reason = reason
                    break
            else:
                if re.match(test, clean_text):
                    is_table_like = True
                    table_reason = reason
                    break
        
        print(f"✓ Table-like content: {is_table_like}" + (f" ({table_reason})" if table_reason else ""))
        if is_table_like:
            elimination_reasons.append(f"Table-like content: {table_reason}")
        
        # Test: Position (right side of page)
        on_right_side = elem['relative_x'] > 0.7
        print(f"✓ Position check: relative_x={elem['relative_x']:.3f}, on_right_side={on_right_side}")
        if on_right_side:
            elimination_reasons.append(f"Text on right side of page (x={elem['relative_x']:.3f} > 0.7)")
        
        # Test: Form region detection (simplified)
        form_field_indicators = [
            'designation', 'service', 'pay', 'grade', 'scale', 'name', 'address', 'phone',
            'email', 'date', 'signature', 'whether', 'concession', 'relationship',
            'home town', 'recorded in', 'service book', 'ltc', 'advance', 'grant',
            'application', 'form', 'availed', 'route', 'persons', 'respect'
        ]
        
        text_lower = clean_text.lower()
        contains_form_indicators = any(indicator in text_lower for indicator in form_field_indicators)
        
        in_form_region = False
        if contains_form_indicators:
            has_form_formatting = (
                clean_text.endswith(':') or
                clean_text.endswith('?') or
                any(word in text_lower for word in ['whether', 'if', 'name', 'date', 'address']) or
                re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+', clean_text) or
                'SI' in clean_text or 'NPA' in clean_text
            )
            is_left_aligned = elem['relative_x'] < 0.6
            
            if has_form_formatting and is_left_aligned:
                in_form_region = True
        
        print(f"✓ Form region check: {in_form_region}")
        if in_form_region:
            elimination_reasons.append("Text identified as form field content")
        
        # ===== FINAL DECISION =====
        print(f"\n--- FINAL DECISION ---")
        print(f"Passes criteria: {passes_criteria}")
        print(f"Elimination reasons: {elimination_reasons}")
        
        # Check if it would be accepted as a heading
        basic_heading_criteria = is_heading_size or is_potential_heading_by_formatting
        passes_all_exclusions = not any([
            is_form_field, is_date, is_table_like, on_right_side, in_form_region,
            not is_frequency_ok, not is_word_count_ok
        ])
        
        would_be_heading = basic_heading_criteria and passes_all_exclusions and clean_text
        
        print(f"\nBasic heading criteria met: {basic_heading_criteria}")
        print(f"Passes all exclusions: {passes_all_exclusions}")
        print(f"FINAL RESULT: Would be detected as heading: {would_be_heading}")
        
        if not would_be_heading:
            print(f"\n❌ ELIMINATED because:")
            for reason in elimination_reasons:
                print(f"   - {reason}")
            if not basic_heading_criteria:
                print(f"   - Failed basic heading criteria (size or formatting)")
    
    doc.close()
    
    # Step 4: Check current file04.json output
    print(f"\n{'='*60}")
    print("CURRENT FILE04.JSON OUTPUT")
    print(f"{'='*60}")
    
    try:
        with open('sample_dataset/outputs/file04.json', 'r') as f:
            current_output = json.load(f)
        
        print(f"Title: {current_output.get('title', 'N/A')}")
        print(f"Number of headings detected: {len(current_output.get('outline', []))}")
        
        if current_output.get('outline'):
            print("Detected headings:")
            for heading in current_output['outline']:
                print(f"  {heading['level']}: '{heading['text']}' (page {heading['page']})")
        else:
            print("No headings detected in current output")
            
    except FileNotFoundError:
        print("file04.json not found - file has not been processed yet")
    except Exception as e:
        print(f"Error reading file04.json: {e}")

if __name__ == "__main__":
    debug_background_heading_file04()
