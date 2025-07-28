import re

def has_long_numbers(text):
    """
    Check if text contains numbers with more than 4 characters
    Returns True if text has long numbers (except hex Unicode)
    """
    if not text:
        return False
    
    # Find all number sequences in the text
    number_pattern = r'\d{5,}'  # 5 or more consecutive digits
    numbers = re.findall(number_pattern, text)
    
    if not numbers:
        return False
    
    # Check if any long number is NOT a hex Unicode representation
    for number in numbers:
        # Check if it's part of a hex Unicode pattern like \x{1234} or \\x{1234}
        hex_unicode_pattern = r'\\x\{' + re.escape(number) + r'\}'
        if not re.search(hex_unicode_pattern, text):
            return True  # Found a long number that's not hex Unicode
    
    return False

# Test cases
test_cases = [
    ("Introduction to Python", False),  # Normal text
    ("Section 123", False),  # Short number
    ("Document 12345", True),  # Long number should be filtered
    ("Report 987654321", True),  # Very long number should be filtered
    ("Unicode \\x{12345}", False),  # Unicode hex should be allowed
    ("Text with \\x{123456} character", False),  # Unicode hex should be allowed
    ("Mixed 12345 and \\x{67890}", True),  # Long number not part of Unicode should be filtered
    ("Chapter 1234", False),  # 4 digit number is allowed
    ("Version 1.2.3", False),  # No long consecutive digits
    ("ID: 98765", True),  # Long number should be filtered
]

print("Testing number filtering function:")
print("=" * 50)
for text, expected in test_cases:
    result = has_long_numbers(text)
    status = "✓" if result == expected else "✗"
    print(f"{status} '{text}' -> {result} (expected: {expected})")

print("\n" + "=" * 50)
print("Filter test complete!")
