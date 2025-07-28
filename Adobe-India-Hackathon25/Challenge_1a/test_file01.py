from process_pdfs import extract_outline

result = extract_outline('sample_dataset/pdfs/file01.pdf')
print('Title:', result['title'])
print('\nOutline:')
for i, item in enumerate(result['outline'], 1):
    print(f"  {i}. {item['level']}: {item['text'][:70]}{'...' if len(item['text']) > 70 else ''}")

print(f"\nTotal headings found: {len(result['outline'])}")
