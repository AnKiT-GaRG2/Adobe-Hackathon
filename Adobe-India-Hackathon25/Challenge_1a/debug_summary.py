import fitz
import re
from collections import Counter

# Debug specifically for "Summary" text in file03.pdf
pdf_path = 'sample_dataset/pdfs/file03.pdf'
doc = fitz.open(pdf_path)

print('=== SUMMARY DEBUG ANALYSIS FOR FILE03.PDF ===')

all_text_elements = []
summary_elements = []

# Extract all text elements
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
                            'size': span['size'],
                            'flags': span['flags'],
                            'font': span['font'],
                            'page': page_num + 1,
                            'bbox': span['bbox'],
                            'y_position': span['bbox'][1],
                            'x_position': span['bbox'][0]
                        }
                        all_text_elements.append(element)
                        
                        # Look for "Summary" specifically
                        if 'summary' in text.lower():
                            summary_elements.append(element)

print(f'\nFound {len(summary_elements)} elements containing "summary":')
for i, elem in enumerate(summary_elements):
    print(f'{i+1}. Page {elem["page"]}: "{elem["text"]}" (Size: {elem["size"]:.1f}, Bold: {bool(elem["flags"] & 16)})')

# Check frequency of exact "Summary" text
summary_frequency = Counter()
for elem in all_text_elements:
    clean_text = re.sub(r"^[0-9.\-\u2013\u2014\)\(©®™]+\s*", "", elem["text"]).strip()
    if clean_text.lower() == 'summary':
        summary_frequency[clean_text] += 1

print(f'\nFrequency analysis for exact "Summary" text:')
for text, count in summary_frequency.items():
    print(f'"{text}": appears {count} times')

# Look for body text sizes
sizes = [elem['size'] for elem in all_text_elements if len(elem['text']) > 3]
most_common = Counter(sizes).most_common()
body_text_size = most_common[0][0]
print(f'\nBody text size: {body_text_size}')

# Check if any "Summary" elements would qualify as headings
print(f'\nSummary elements analysis:')
for elem in summary_elements:
    clean_text = re.sub(r"^[0-9.\-\u2013\u2014\)\(©®™]+\s*", "", elem["text"]).strip()
    is_bold = elem['flags'] & 16
    is_larger_than_body = elem['size'] > body_text_size * 1.1
    
    print(f'  "{elem["text"]}" - Page {elem["page"]}')
    print(f'    Size: {elem["size"]:.1f} (Body: {body_text_size:.1f})')
    print(f'    Bold: {bool(is_bold)}')
    print(f'    Larger than body: {is_larger_than_body}')
    print(f'    Clean text: "{clean_text}"')
    print()
