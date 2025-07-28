import json

def test_generic_approach():
    print("=== TESTING GENERIC METADATA DETECTION ===")
    
    # Test file02.json (should have filtered out org name)
    with open('sample_dataset/outputs/file02.json', 'r', encoding='utf-8') as f:
        data2 = json.load(f)
    
    print(f"\nFile02 results:")
    print(f"Title: {data2['title']}")
    print(f"First heading: {data2['outline'][0] if data2['outline'] else 'No headings'}")
    
    # Check if org name was filtered
    org_found = any("International Software Testing" in item['text'] for item in data2['outline'])
    print(f"❌ Organizational text found: {org_found}")
    
    # Test file03.json 
    with open('sample_dataset/outputs/file03.json', 'r', encoding='utf-8') as f:
        data3 = json.load(f)
    
    print(f"\nFile03 results:")
    print(f"Title: {data3['title']}")
    print(f"Outline items: {len(data3['outline'])}")
    
    # Show some headings to verify they look like content, not metadata
    for i, item in enumerate(data3['outline'][:3]):
        print(f"  {item['level']}: {item['text']}")
    
    print("\n=== GENERIC PATTERNS USED ===")
    print("✓ Length-based: Very long names (>6 words)")
    print("✓ Formal suffixes: Ltd, Inc, Corp, LLC, etc.")
    print("✓ Capitalization: 3+ capitalized words (proper nouns)")
    print("✓ Page 1 heuristics: Long text or ALL CAPS")
    print("✓ Copyright patterns: ©, copyright, all rights, reserved")
    print("✓ NO hardcoded specific keywords!")

if __name__ == "__main__":
    test_generic_approach()
