from process_pdfs import extract_outline

files_to_test = ['file01.pdf', 'file02.pdf', 'file03.pdf', 'file04.pdf', 'file05.pdf']

for filename in files_to_test:
    print(f"\n=== Testing {filename} ===")
    try:
        result = extract_outline(f'sample_dataset/pdfs/{filename}')
        print(f'Title: {result["title"]}')
        print(f'Headings found: {len(result["outline"])}')
        for i, item in enumerate(result['outline'][:10], 1):  # Show first 10
            print(f"  {i}. {item['level']}: {item['text'][:60]}{'...' if len(item['text']) > 60 else ''}")
        if len(result['outline']) > 10:
            print(f"  ... and {len(result['outline']) - 10} more")
    except Exception as e:
        print(f"Error processing {filename}: {e}")
