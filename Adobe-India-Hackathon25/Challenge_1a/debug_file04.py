import fitz
import json

def debug_file04():
    pdf_path = "sample_dataset/pdfs/file04.pdf"
    doc = fitz.open(pdf_path)
    
    print("=== FILE04.PDF CONTENT ANALYSIS ===")
    
    for page_num in range(min(2, len(doc))):  # First 2 pages
        page = doc[page_num]
        print(f"\n--- PAGE {page_num} ---")
        
        # Get all text with detailed formatting
        text_dict = page.get_text("dict")
        
        for block_num, block in enumerate(text_dict["blocks"]):
            if "lines" in block:  # Text block
                print(f"\nBlock {block_num}:")
                for line_num, line in enumerate(block["lines"]):
                    for span_num, span in enumerate(line["spans"]):
                        text = span["text"].strip()
                        if text:
                            font_size = span["size"]
                            font_flags = span["flags"]
                            font_name = span["font"]
                            is_bold = bool(font_flags & 16)
                            
                            print(f"  Line {line_num}, Span {span_num}:")
                            print(f"    Text: '{text}'")
                            print(f"    Size: {font_size}")
                            print(f"    Bold: {is_bold}")
                            print(f"    Font: {font_name}")
                            print(f"    Flags: {font_flags}")
    
    doc.close()

if __name__ == "__main__":
    debug_file04()
