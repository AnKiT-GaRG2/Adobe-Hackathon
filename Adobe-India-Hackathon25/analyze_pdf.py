import fitz
from collections import Counter

def analyze_pdf_structure(pdf_path):
    doc = fitz.open(pdf_path)
    print(f'Analyzing: {pdf_path}')
    print(f'Total pages: {len(doc)}')
    
    all_text_elements = []
    
    # Analyze first few pages
    for page_num in range(min(3, len(doc))):
        page = doc[page_num]
        blocks = page.get_text('dict')['blocks']
        
        print(f'\n=== PAGE {page_num + 1} ===')
        
        for b in blocks:
            if 'lines' in b:
                for l in b['lines']:
                    for s in l['spans']:
                        text = s['text'].strip()
                        if text and len(text) > 3:
                            all_text_elements.append({
                                'text': text,
                                'size': round(s['size'], 1),
                                'flags': s['flags'],
                                'page': page_num + 1
                            })
                            print(f"Size: {s['size']:.1f}, Flags: {s['flags']}, Text: '{text}'")
    
    # Font size analysis
    sizes = [elem['size'] for elem in all_text_elements]
    size_counts = Counter(sizes)
    
    print(f'\n=== FONT SIZE ANALYSIS ===')
    print('Font size distribution:')
    for size, count in sorted(size_counts.items(), reverse=True):
        print(f'Size {size}: {count} occurrences')
    
    most_common_size = size_counts.most_common(1)[0][0]
    print(f'Most common (body text) size: {most_common_size}')
    
    # Show largest sizes
    unique_sizes = sorted(set(sizes), reverse=True)
    print(f'Largest font sizes: {unique_sizes[:5]}')
    
    doc.close()

if __name__ == "__main__":
    analyze_pdf_structure('sample_dataset/pdfs/file02.pdf')
