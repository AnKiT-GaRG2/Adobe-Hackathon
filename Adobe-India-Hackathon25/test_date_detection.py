#!/usr/bin/env python3
"""
Test script to verify the comprehensive date detection function
"""
import re

def contains_date(text):
    """
    Comprehensive date detection function that checks if text contains any date format
    Returns True if the text contains a date in any common format
    """
    if not text:
        return False
    
    # Clean the text for date checking
    text_clean = text.strip()
    
    # Define comprehensive date patterns
    date_patterns = [
        # Full month names with day and year
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
        
        # Abbreviated month names with day and year
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
        
        # Month/Day/Year formats (with various separators)
        r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b',
        
        # Day/Month/Year formats (European style)
        r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b',
        
        # Year/Month/Day formats (ISO style)
        r'\b\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}\b',
        
        # Year-Month-Day (ISO 8601)
        r'\b\d{4}-\d{2}-\d{2}\b',
        
        # Month Day, Year (American style)
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b',
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},\s+\d{4}\b',
        
        # Day Month Year (British style)
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{4}\b',
        
        # Year only (4 digits)
        r'\b(19|20)\d{2}\b',
        
        # Month/Year combinations
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{4}\b',
        r'\b\d{1,2}[\/\-\.]\d{4}\b',
        
        # Quarters
        r'\bQ[1-4]\s+\d{4}\b',
        r'\b(First|Second|Third|Fourth)\s+Quarter\s+\d{4}\b',
        
        # Seasons with year
        r'\b(Spring|Summer|Fall|Autumn|Winter)\s+\d{4}\b',
        
        # Week formats
        r'\bWeek\s+\d{1,2},?\s+\d{4}\b',
        r'\bWeek\s+of\s+.*\d{4}\b',
        
        # Time stamps (hours:minutes)
        r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(AM|PM|am|pm)?\b',
        
        # Relative dates
        r'\b(Today|Yesterday|Tomorrow)\b',
        r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
        
        # Additional numeric date patterns
        r'\b\d{1,2}(?:st|nd|rd|th)\s+of\s+(January|February|March|April|May|June|July|August|September|October|November|December)\b',
        r'\b\d{1,2}(?:st|nd|rd|th)\s+of\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\b',
        
        # Version numbers that might look like dates (e.g., "v2.3.1")
        r'\bv?\d+\.\d+(?:\.\d+)*\b',
        
        # Date ranges
        r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\s*[-–—]\s*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b',
        
        # European date format dd.mm.yyyy
        r'\b\d{1,2}\.\d{1,2}\.\d{4}\b',
        
        # Academic year format (e.g., "2023-24", "2023-2024")
        r'\b\d{4}[-–—]\d{2,4}\b',
        
        # Financial year quarters
        r'\bFY\s*\d{4}[-–—]?\d{0,4}\b',
        
        # Revision dates (e.g., "Rev. 1.2 March 2023")
        r'\bRev\.?\s*\d+(?:\.\d+)*\s+(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{4}\b',
        
        # Publication dates
        r'\bPublished:?\s+.*\d{4}\b',
        r'\bUpdated:?\s+.*\d{4}\b',
        r'\bModified:?\s+.*\d{4}\b',
        
        # Copyright years
        r'\b©\s*\d{4}\b',
        r'\bCopyright\s+\d{4}\b',
    ]
    
    # Check if any date pattern matches the text
    for pattern in date_patterns:
        if re.search(pattern, text_clean, re.IGNORECASE):
            return True
    
    return False

# Test cases
test_cases = [
    # Should be detected as dates
    ("January 15, 2023", True),
    ("Jan 15, 2023", True),
    ("15/01/2023", True),
    ("2023-01-15", True),
    ("March 2023", True),
    ("2023", True),
    ("Q1 2023", True),
    ("2.1 Intended Audience", True),  # Contains version number pattern
    ("Rev. 1.2 March 2023", True),
    ("© 2023", True),
    ("Monday", True),
    ("12:30 PM", True),
    
    # Should NOT be detected as dates
    ("Introduction", False),
    ("Table of Contents", False),
    ("Acknowledgements", False),
    ("Overview", False),
    ("References", False),
    ("Conclusion", False),
]

def test_date_detection():
    print("Testing comprehensive date detection function...")
    print("=" * 50)
    
    all_passed = True
    
    for text, expected in test_cases:
        result = contains_date(text)
        status = "✓" if result == expected else "✗"
        
        print(f"{status} '{text}' -> {result} (expected: {expected})")
        
        if result != expected:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("All tests passed! ✓")
    else:
        print("Some tests failed! ✗")

if __name__ == "__main__":
    test_date_detection()
