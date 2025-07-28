import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from process_pdfs import group_text_by_lines, is_valid_heading_line

# Test the line-based grouping logic
def test_line_grouping():
    print("Testing line-based text grouping and validation:")
    print("=" * 60)
    
    # Mock text elements representing different scenarios
    test_elements = [
        # Scenario 1: Same line with all heading-sized text (should be valid)
        {"text": "Introduction", "size": 14, "page": 0, "y_position": 100, "x_position": 50},
        {"text": "to", "size": 14, "page": 0, "y_position": 102, "x_position": 150},  # Same line (close y)
        {"text": "Python", "size": 14, "page": 0, "y_position": 101, "x_position": 200},  # Same line
        
        # Scenario 2: Same line with mixed sizes (should be invalid)
        {"text": "Chapter", "size": 14, "page": 0, "y_position": 200, "x_position": 50},  # Heading size
        {"text": "Overview", "size": 12, "page": 0, "y_position": 201, "x_position": 150},  # Body text size
        
        # Scenario 3: Different lines (should be processed separately)
        {"text": "Section", "size": 14, "page": 0, "y_position": 300, "x_position": 50},
        {"text": "Details", "size": 14, "page": 0, "y_position": 320, "x_position": 50},  # Different line
    ]
    
    # Mock heading levels and frequency data
    heading_levels = {14: "H1", 13: "H2"}  # Note: 12 is NOT a heading level
    all_text_frequency = {"Introduction": 1, "to": 1, "Python": 1, "Chapter": 1, "Overview": 1, "Section": 1, "Details": 1}
    title_components = []
    
    # Group by lines
    line_groups = group_text_by_lines(test_elements)
    
    print(f"Found {len(line_groups)} line groups:")
    print()
    
    for i, line_group in enumerate(line_groups, 1):
        line_texts = [elem["text"] for elem in line_group]
        line_sizes = [elem["size"] for elem in line_group]
        
        print(f"Line {i}: {' '.join(line_texts)}")
        print(f"  Sizes: {line_sizes}")
        
        # Test validation
        is_valid = is_valid_heading_line(line_group, heading_levels, all_text_frequency, title_components)
        print(f"  Valid heading: {'✓ YES' if is_valid else '✗ NO'}")
        
        if not is_valid and any(size in heading_levels for size in line_sizes):
            # Explain why it's not valid
            reasons = []
            for elem in line_group:
                if elem["size"] not in heading_levels:
                    reasons.append(f"'{elem['text']}' has non-heading size ({elem['size']})")
            if reasons:
                print(f"  Reason: {'; '.join(reasons)}")
        print()

if __name__ == "__main__":
    test_line_grouping()
