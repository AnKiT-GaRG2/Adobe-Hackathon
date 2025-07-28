import sys
sys.path.append('.')

# Import the enhanced functions from process_pdfs
from process_pdfs import extract_outline

# Test all files
test_files = ['file01.pdf', 'file02.pdf', 'file04.pdf', 'file05.pdf']
for filename in test_files:
    print(f'\n{filename.upper()}:')
    print('='*40)
    result = extract_outline(f'sample_dataset/pdfs/{filename}')
    print('Title:', result.get('title', 'N/A'))
    print('Outlines:', len(result.get('outlines', [])))
    
    # Show first few outlines
    outlines = result.get('outlines', [])
    for i, outline in enumerate(outlines[:3]):
        print(f'  {i+1}. {outline}')
    if len(outlines) > 3:
        print(f'  ... and {len(outlines) - 3} more')
