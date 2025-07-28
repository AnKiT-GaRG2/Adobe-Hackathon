import fitz
import json

# Extract headings from file03.pdf with focus on Summary and Background
pdf_path = 'sample_dataset/pdfs/file03.pdf'
doc = fitz.open(pdf_path)

print('=== SEARCHING FOR SUMMARY AND BACKGROUND HEADINGS ===')

for page_num in range(len(doc)):
    page = doc[page_num]
    page_text = page.get_text().lower()
    
    if 'summary' in page_text or 'background' in page_text:
        print(f'\n--- PAGE {page_num + 1} CONTAINS SUMMARY/BACKGROUND ---')
        
        # Get detailed text blocks
        blocks = page.get_text('dict')['blocks']
        
        for block in blocks:
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text'].strip()
                        if text and ('summary' in text.lower() or 'background' in text.lower()):
                            print(f"Found: '{text}'")
                            print(f"  Font: {span['font']}")
                            print(f"  Size: {span['size']}")
                            print(f"  Position: {span['bbox']}")
                            print(f"  Flags: {span['flags']} (Bold: {bool(span['flags'] & 16)})")
                            print()

# Also show all text elements on pages 2-3 with larger font sizes
print('\n=== ALL LARGER TEXT ELEMENTS ON PAGES 2-3 ===')
for page_num in [1, 2]:  # Pages 2-3 (0-indexed)
    page = doc[page_num]
    print(f'\n--- PAGE {page_num + 1} ---')
    
    blocks = page.get_text('dict')['blocks']
    text_elements = []
    
    for block in blocks:
        if 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text'].strip()
                    if text and span['size'] > 12:  # Only show larger text
                        text_elements.append({
                            'text': text,
                            'size': span['size'],
                            'font': span['font'],
                            'bold': bool(span['flags'] & 16)
                        })
    
    # Sort by font size (largest first)
    text_elements.sort(key=lambda x: x['size'], reverse=True)
    
    for elem in text_elements:
        print(f"'{elem['text']}' - Size: {elem['size']}, Font: {elem['font']}, Bold: {elem['bold']}")

doc.close()
