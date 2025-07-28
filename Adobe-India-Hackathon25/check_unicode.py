import json

def check_unicode_characters(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=== UNICODE CHARACTER ANALYSIS ===")
    print(f"Title: {repr(data['title'])}")
    
    for item in data['outline']:
        text = item['text']
        # Check for specific Unicode characters
        if '\u2013' in text:  # en dash
            print(f"✓ EN DASH (U+2013) found in: {repr(text)}")
        if '\u2014' in text:  # em dash
            print(f"✓ EM DASH (U+2014) found in: {repr(text)}")
        if '\u201C' in text or '\u201D' in text:  # smart quotes
            print(f"✓ SMART QUOTES found in: {repr(text)}")
        if '\u2018' in text or '\u2019' in text:  # smart single quotes
            print(f"✓ SMART SINGLE QUOTES found in: {repr(text)}")
        if '\u2022' in text:  # bullet
            print(f"✓ BULLET (U+2022) found in: {repr(text)}")

if __name__ == "__main__":
    check_unicode_characters('sample_dataset/outputs/file02.json')
