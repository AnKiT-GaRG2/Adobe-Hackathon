import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from process_pdfs import is_decorative_text, find_nearby_heading_words

def test_decorative_detection():
    print("Testing Decorative Text Detection")
    print("=" * 50)
    
    # Test decorative text patterns
    test_cases = [
        ("Normal heading text", False),
        ("★★★ DECORATIVE ★★★", True),
        ("=== TITLE ===", True),
        ("--- Chapter ---", True),
        ("T O P  J U M P", True),  # Spaced out letters
        ("♦♦♦ PARTY ♦♦♦", True),
        ("Introduction to Python", False),
        ("●●● INVITATION ●●●", True),
        ("AAAAAAAA", True),  # Repeated characters
        ("!!!! WARNING !!!!", True),
        ("Chapter 1", False),
        ("◆◇◆◇ EVENT ◇◆◇◆", True),
    ]
    
    print("Decorative Text Detection Results:")
    print("-" * 40)
    for text, expected in test_cases:
        result = is_decorative_text(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> {result} (expected: {expected})")
    
    print("\n" + "=" * 50)
    print("Nearby Words Detection Test:")
    print("-" * 40)
    
    # Test nearby words detection
    decorative_element = {
        "text": "★★★",
        "size": 16,
        "page": 1,
        "x_position": 100,
        "y_position": 200
    }
    
    all_text_elements = [
        decorative_element,
        {"text": "PARTY", "size": 14, "page": 1, "x_position": 120, "y_position": 200},  # Same line
        {"text": "INVITATION", "size": 14, "page": 1, "x_position": 180, "y_position": 200},  # Same line
        {"text": "2024", "size": 12, "page": 1, "x_position": 100, "y_position": 220},  # Below
        {"text": "Some body text here", "size": 10, "page": 1, "x_position": 50, "y_position": 300},  # Far away
        {"text": "Another", "size": 14, "page": 1, "x_position": 250, "y_position": 200},  # Same line but far
    ]
    
    nearby_words = find_nearby_heading_words(decorative_element, all_text_elements)
    
    print(f"Decorative element: '{decorative_element['text']}' at ({decorative_element['x_position']}, {decorative_element['y_position']})")
    print("Nearby words found:")
    for i, word in enumerate(nearby_words):
        distance_x = abs(word['x_position'] - decorative_element['x_position'])
        distance_y = abs(word['y_position'] - decorative_element['y_position'])
        print(f"  {i+1}. '{word['text']}' at ({word['x_position']}, {word['y_position']}) - Distance: ({distance_x}, {distance_y})")
    
    print(f"\nWould combine into heading: '★★★ PARTY INVITATION' (decorative + nearby words)")

if __name__ == "__main__":
    test_decorative_detection()
