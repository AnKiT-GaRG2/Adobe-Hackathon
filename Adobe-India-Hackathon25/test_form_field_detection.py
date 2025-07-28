#!/usr/bin/env python3
"""
Test script to verify the form field and generic term filtering function
"""
import re

def is_form_field_or_generic_term(text):
    """
    Check if the text is a common form field label or generic term that should not be considered a heading
    Returns True if the text should be excluded from headings
    """
    if not text:
        return False
    
    # Clean the text
    clean_text = text.strip().lower()
    
    # Single words that are typically form fields or generic terms
    form_fields_and_generic_terms = {
        # Common form fields
        'name', 'date', 'address', 'phone', 'email', 'signature', 'title', 'position',
        'department', 'company', 'organization', 'city', 'state', 'country', 'zip',
        'zipcode', 'postal', 'code', 'number', 'amount', 'total', 'subtotal',
        'quantity', 'price', 'cost', 'fee', 'tax', 'discount', 'balance',
        
        # Document metadata terms
        'page', 'pages', 'version', 'revision', 'draft', 'final', 'copy',
        'original', 'duplicate', 'file', 'document', 'form', 'application',
        
        # Generic descriptive words
        'yes', 'no', 'true', 'false', 'male', 'female', 'other', 'none',
        'optional', 'required', 'mandatory', 'notes', 'comments', 'remarks',
        'description', 'details', 'information', 'data',
        
        # Time-related single words
        'time', 'hour', 'minute', 'second', 'day', 'week', 'month', 'year',
        'today', 'yesterday', 'tomorrow', 'morning', 'afternoon', 'evening',
        'night', 'am', 'pm',
        
        # Status/action words
        'approved', 'rejected', 'pending', 'completed', 'incomplete', 'draft',
        'submitted', 'received', 'processed', 'cancelled', 'active', 'inactive',
        
        # Common single letter or number labels
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
        
        # Units and measurements
        'kg', 'lb', 'oz', 'cm', 'mm', 'inch', 'ft', 'meter', 'mile', 'km',
        'percent', '%', 'dollar', '$', 'euro', '€', 'pound', '£',
        
        # Checkbox/radio button labels
        'check', 'select', 'choose', 'pick', 'mark', 'tick', 'cross',
        
        # Common abbreviations
        'etc', 'inc', 'corp', 'ltd', 'llc', 'co', 'dept', 'div', 'mgr',
        'dir', 'vp', 'ceo', 'cfo', 'hr', 'it', 'pr', 'qa',
        
        # Educational/certification terms
        'grade', 'score', 'rank', 'level', 'class', 'course', 'subject',
        'test', 'exam', 'quiz', 'assignment', 'homework',
        
        # Medical/health form terms
        'age', 'weight', 'height', 'gender', 'race', 'ethnicity', 'blood',
        'allergies', 'medications', 'symptoms', 'diagnosis', 'treatment',
        
        # Financial terms
        'income', 'salary', 'wage', 'bonus', 'commission', 'deduction',
        'withholding', 'benefits', 'insurance', 'retirement', 'savings',
        
        # Legal terms
        'witness', 'notary', 'attorney', 'lawyer', 'judge', 'court',
        'case', 'claim', 'settlement', 'agreement', 'contract',
    }
    
    # Check if it's a single word and in our exclusion list
    if ' ' not in clean_text and clean_text in form_fields_and_generic_terms:
        return True
    
    # Also exclude very short single words (1-2 characters) that are likely labels
    if len(clean_text) <= 2 and ' ' not in clean_text:
        return True
    
    # Exclude words that are just numbers or simple patterns
    if re.match(r'^[0-9]+$', clean_text):  # Just numbers
        return True
    
    if re.match(r'^[a-z]$', clean_text):  # Single letters
        return True
    
    return False

# Test cases
test_cases = [
    # Should be filtered out (form fields/generic terms)
    ("Name", True),
    ("Date", True),
    ("Address", True),
    ("Phone", True),
    ("Email", True),
    ("Signature", True),
    ("Amount", True),
    ("Total", True),
    ("Page", True),
    ("Version", True),
    ("Yes", True),
    ("No", True),
    ("A", True),
    ("B", True),
    ("1", True),
    ("2", True),
    ("Age", True),
    ("Gender", True),
    ("ID", True),  # Short form
    
    # Should NOT be filtered out (legitimate headings)
    ("Introduction", False),
    ("Table of Contents", False),
    ("Acknowledgements", False),
    ("2.1 Intended Audience", False),
    ("Business Requirements", False),
    ("Technical Specifications", False),
    ("Project Overview", False),
    ("Implementation Plan", False),
    ("Risk Assessment", False),
    ("Budget Analysis", False),
]

def test_form_field_detection():
    print("Testing form field and generic term detection...")
    print("=" * 60)
    
    all_passed = True
    
    for text, expected in test_cases:
        result = is_form_field_or_generic_term(text)
        status = "✓" if result == expected else "✗"
        
        action = "FILTERED OUT" if result else "KEPT"
        
        print(f"{status} '{text}' -> {action} (expected: {'FILTERED' if expected else 'KEPT'})")
        
        if result != expected:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("All tests passed! ✓")
    else:
        print("Some tests failed! ✗")

if __name__ == "__main__":
    test_form_field_detection()
