import fitz
import json

# Debug file03.pdf
pdf_path = 'sample_dataset/pdfs/file03.pdf'
doc = fitz.open(pdf_path)
print('=== FILE03.PDF DEBUG ANALYSIS ===')

all_text_elements = []
for page_num in range(len(doc)):
    page = doc[page_num]
    print(f'\n--- PAGE {page_num + 1} ---')
    blocks = page.get_text('dict')['blocks']
    
    for block in blocks:
        if 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text'].strip()
                    if text and len(text) > 2:
                        element = {
                            'text': text,
                            'size': span['size'],
                            'flags': span['flags'],
                            'font': span['font'],
                            'page': page_num + 1,
                            'bbox': span['bbox']
                        }
                        all_text_elements.append(element)

# Calculate font statistics
font_sizes = [elem['size'] for elem in all_text_elements]
avg_font_size = sum(font_sizes) / len(font_sizes)
print(f'\nFONT STATISTICS:')
print(f'Average font size: {avg_font_size:.2f}')
print(f'Font size range: {min(font_sizes):.1f} - {max(font_sizes):.1f}')

# Look for potential headings
print(f'\nPOTENTIAL HEADINGS:')
heading_candidates = []

for elem in all_text_elements:
    text = elem['text']
    size = elem['size']
    flags = elem['flags']
    is_bold = flags & 16
    
    # Check specific texts we know should be headings
    expected_headings = [
        'Summary', 'Timeline', 'Background', 'Equitable access',
        'Shared decision-making', 'Local points', 'Access',
        'Guidance and Advice', 'Training', 'Provincial Purchasing',
        'What could the ODL', 'For each Ontario citizen',
        'Business Plan', 'Milestones', 'Approach', 'Evaluation',
        'Appendix A', 'Phase I', 'Phase II', 'Phase III',
        'Preamble', 'Terms of Reference', 'Membership'
    ]
    
    for expected in expected_headings:
        if expected.lower() in text.lower():
            heading_candidates.append({
                'text': text,
                'page': elem['page'],
                'size': size,
                'bold': is_bold,
                'font': elem['font']
            })
            break

print(f'Found {len(heading_candidates)} expected headings:')
for i, candidate in enumerate(heading_candidates):
    print(f'{i+1:2d}. Page {candidate["page"]}: "{candidate["text"]}" (Size: {candidate["size"]:.1f}, Bold: {candidate["bold"]})')

# Also show all unique font sizes
unique_sizes = sorted(set(font_sizes))
print(f'\nAll font sizes used: {unique_sizes}')
