import fitz
import json

# Extract detailed metadata for Summary and Background headings from file03.pdf
pdf_path = 'sample_dataset/pdfs/file03.pdf'
doc = fitz.open(pdf_path)

print('=== DETAILED METADATA FOR SUMMARY AND BACKGROUND HEADINGS ===')

summary_headings = []
background_headings = []

for page_num in range(len(doc)):
    page = doc[page_num]
    blocks = page.get_text('dict')['blocks']
    
    for block in blocks:
        if 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text'].strip()
                    text_lower = text.lower()
                    
                    if 'summary' in text_lower:
                        heading_info = {
                            'text': text,
                            'text_with_hex': repr(text),
                            'page': page_num + 1,
                            'font_size': span['size'],
                            'font_family': span['font'],
                            'is_bold': bool(span['flags'] & 16),
                            'is_italic': bool(span['flags'] & 2),
                            'character_count': len(text),
                            'word_count': len(text.split()),
                            'position_on_page': {
                                'x': span['bbox'][0],
                                'y': span['bbox'][1],
                                'width': span['bbox'][2] - span['bbox'][0],
                                'height': span['bbox'][3] - span['bbox'][1]
                            },
                            'bbox': span['bbox']
                        }
                        summary_headings.append(heading_info)
                        
                    if 'background' in text_lower:
                        heading_info = {
                            'text': text,
                            'text_with_hex': repr(text),
                            'page': page_num + 1,
                            'font_size': span['size'],
                            'font_family': span['font'],
                            'is_bold': bool(span['flags'] & 16),
                            'is_italic': bool(span['flags'] & 2),
                            'character_count': len(text),
                            'word_count': len(text.split()),
                            'position_on_page': {
                                'x': span['bbox'][0],
                                'y': span['bbox'][1],
                                'width': span['bbox'][2] - span['bbox'][0],
                                'height': span['bbox'][3] - span['bbox'][1]
                            },
                            'bbox': span['bbox']
                        }
                        background_headings.append(heading_info)

print('\n=== SUMMARY HEADINGS ===')
for i, heading in enumerate(summary_headings, 1):
    print(f"\n{i}. Summary Heading:")
    for key, value in heading.items():
        print(f"   {key}: {value}")

print('\n=== BACKGROUND HEADINGS ===')
for i, heading in enumerate(background_headings, 1):
    print(f"\n{i}. Background Heading:")
    for key, value in heading.items():
        print(f"   {key}: {value}")

doc.close()
