from process_pdfs import extract_outline

# Test the stack-based algorithm on file02.pdf
result = extract_outline('sample_dataset/pdfs/file02.pdf')

print('Title:', result['title'])
print(f'Found {len(result["outline"])} headings:')
print()

for i, h in enumerate(result['outline'][:15]):
    print(f'{i+1:2d}. {h["level"]} - {h["text"][:70]}... (Page {h["page"]})')

print()
print("Testing on file01.pdf (form document):")
result1 = extract_outline('sample_dataset/pdfs/file01.pdf')
print('Title:', result1['title'])
print(f'Found {len(result1["outline"])} headings (expected: 0 for a form)')
