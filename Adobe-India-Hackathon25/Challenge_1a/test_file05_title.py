import fitz
import json
import re
from collections import Counter

def contains_urls(text):
    """Check if text contains URLs, domain names, or web-related patterns."""
    text = text.lower()
    url_patterns = [
        r'https?://',
        r'www\.',
        r'\.com',
        r'\.org',
        r'\.net',
        r'\.edu',
        r'\.gov',
        r'\.mil',
        r'\.int',
        r'\.co\.',
        r'\.uk',
        r'\.de',
        r'\.fr',
        r'\.jp',
        r'\.au',
        r'\.ca',
        r'@.*\.',
        r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    ]
    
    for pattern in url_patterns:
        if re.search(pattern, text):
            return True
    
    return False

def contains_date(text):
    """Check if text contains date patterns."""
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\b',
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b',
        r'\b\d{1,2}(st|nd|rd|th)\b'
    ]
    
    for pattern in date_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False

# Test file05 title reconstruction
pdf_path = 'sample_dataset/pdfs/file05.pdf'
doc = fitz.open(pdf_path)

# Extract all text elements
text_elements = []
for page_num in range(min(2, len(doc))):  # First 2 pages
    page = doc[page_num]
    text_dict = page.get_text("dict")
    
    for block in text_dict["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        text_elements.append({
                            "text": text,
                            "size": round(span["size"], 1),
                            "page": page_num + 1,
                            "y_position": round(span["bbox"][1], 1),
                            "x_position": round(span["bbox"][0], 1)
                        })

print("FILE05 Title Reconstruction Test")
print("="*40)

# Find common font sizes
sizes = [t["size"] for t in text_elements if t["page"] == 1]
size_counter = Counter(sizes)
print("Font sizes (frequency):", size_counter.most_common(10))

body_text_size = size_counter.most_common(1)[0][0] if size_counter else 10
print(f"Body text size: {body_text_size}")

# Try decorative title reconstruction
decorative_title_elements = []

# Collect text elements that could be decorative title parts
all_sizes = [t["size"] for t in text_elements if len(t["text"]) > 0]
if all_sizes:
    max_size = max(all_sizes)
    print(f"Maximum font size: {max_size}")
    
    # Focus on text that's 70% or more of the max size, but exclude pure decorative symbols
    min_title_size = max_size * 0.7
    print(f"Minimum title size (70% of max): {min_title_size}")
    
    for t in text_elements:
        text = t["text"].strip()
        if (t["page"] <= 2 and  # First few pages
            t["size"] >= min_title_size and  # Reasonable size (70%+ of max)
            len(text) >= 1 and  # Accept single characters
            not contains_urls(text) and  # Exclude URLs from title
            not contains_date(text) and  # Exclude dates
            not re.match(r'^[-_=]+$', text)):  # Exclude pure decorative lines like "---"
            decorative_title_elements.append({
                "text": text,
                "size": t["size"],
                "page": t["page"],
                "y_position": t["y_position"],
                "x_position": t["x_position"]
            })

print(f"\nFound {len(decorative_title_elements)} potential title elements:")
for elem in decorative_title_elements[:20]:  # Show first 20
    print(f"  '{elem['text']}' (size: {elem['size']}, y: {elem['y_position']}, x: {elem['x_position']})")

if decorative_title_elements:
    # Sort by position (top to bottom, left to right within same line)
    decorative_title_elements.sort(key=lambda x: (x["page"], x["y_position"], x["x_position"]))
    
    # Group elements that are close together (same line)
    title_lines = []
    current_line = []
    current_y = None
    
    for elem in decorative_title_elements:
        elem_y = elem["y_position"]
        
        # If this element is on a different line (y position differs by more than 10 pixels)
        if current_y is not None and abs(elem_y - current_y) > 10:
            if current_line:
                title_lines.append(current_line)
                current_line = []
        
        current_line.append(elem)
        current_y = elem_y
    
    # Don't forget the last line
    if current_line:
        title_lines.append(current_line)
    
    print(f"\nGrouped into {len(title_lines)} lines:")
    for i, line in enumerate(title_lines):
        print(f"Line {i+1} (y: {line[0]['y_position']}):")
        for elem in line:
            print(f"  '{elem['text']}' (size: {elem['size']}, x: {elem['x_position']})")
    
    # Reconstruct title from the lines that look like title content
    title_parts = []
    for line in title_lines:
        # Sort elements in the line by x position (left to right)
        line.sort(key=lambda x: x["x_position"])
        
        # Combine text from this line, focusing on meaningful content
        line_text_parts = []
        
        # Handle fragmented words by looking for patterns like "Y ou" -> "You"
        i = 0
        while i < len(line):
            elem = line[i]
            text = elem["text"].strip()
            
            # Skip decorative symbols and pure punctuation
            if (text and 
                not re.match(r'^[-_=!@#$%^&*()]+$', text) and  # Skip pure symbols
                not contains_urls(text)):
                
                # Check if this is a single character that might be part of a fragmented word
                if (len(text) == 1 and text.isalpha() and 
                    i + 1 < len(line)):
                    # Look ahead to see if the next element completes a word
                    next_elem = line[i + 1]
                    next_text = next_elem["text"].strip()
                    
                    # If next element is also close and could complete the word
                    if (abs(next_elem["x_position"] - elem["x_position"]) < 30 and  # Close horizontally
                        len(next_text) >= 1 and next_text.isalpha()):
                        # Combine them into one word
                        combined_word = text + next_text
                        line_text_parts.append(combined_word)
                        i += 2  # Skip the next element since we processed it
                        continue
                
                line_text_parts.append(text)
            
            i += 1
        
        if line_text_parts:
            line_text = " ".join(line_text_parts)
            # Only include lines that look like meaningful title content
            if (len(line_text.strip()) >= 2 and 
                any(c.isalpha() for c in line_text)):  # Must contain letters
                title_parts.append(line_text)
    
    print("\nTitle parts:")
    for i, part in enumerate(title_parts):
        print(f"  {i+1}. '{part}'")
    
    if title_parts:
        # Take the first meaningful line as the title
        decorative_title = title_parts[0]
        
        # Clean up the decorative title
        decorative_title = re.sub(r'\s+', ' ', decorative_title).strip()
        
        print(f"\nFinal decorative title: '{decorative_title}'")
        
        # Check if the decorative title looks reasonable
        if (len(decorative_title) >= 3 and 
            not contains_urls(decorative_title) and 
            not contains_date(decorative_title) and
            any(c.isalpha() for c in decorative_title)):  # Must contain letters
            print(f"✓ Title accepted: '{decorative_title}'")
        else:
            print(f"✗ Title rejected")
    else:
        print("No valid title parts found")

doc.close()
