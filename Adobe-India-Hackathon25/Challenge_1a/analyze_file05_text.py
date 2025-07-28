import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import fitz

# Analyze file05 to understand the text structure better
pdf_path = "sample_dataset/pdfs/file05.pdf"

doc = fitz.open(pdf_path)
print("=== FILE05 DETAILED ANALYSIS ===")

all_elements = []

for page_num, page in enumerate(doc):
    print(f"\nPage {page_num}:")
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if "lines" in b:
            for l in b["lines"]:
                for s in l["spans"]:
                    text = s["text"].strip()
                    if text:
                        element = {
                            "text": text,
                            "size": s["size"],
                            "y_position": s["bbox"][1],
                            "x_position": s["bbox"][0],
                            "page": page_num
                        }
                        all_elements.append(element)
                        print(f"  '{text}' | Size: {s['size']:.1f} | Y: {s['bbox'][1]:.1f} | X: {s['bbox'][0]:.1f}")

doc.close()

# Analyze which elements could form "HOPE"
print("\n=== POTENTIAL 'HOPE' ELEMENTS ===")
hope_chars = ['H', 'O', 'P', 'E']
hope_elements = []

for elem in all_elements:
    if elem["text"] in hope_chars and elem["size"] > 20:  # Focus on larger text
        hope_elements.append(elem)
        print(f"Found '{elem['text']}' at Y:{elem['y_position']:.1f}, X:{elem['x_position']:.1f}, Size:{elem['size']:.1f}")

# Check if we can form "HOPE" from these elements
if len(hope_elements) >= 4:
    # Sort by position
    hope_elements.sort(key=lambda x: (x["y_position"], x["x_position"]))
    hope_word = "".join([elem["text"] for elem in hope_elements[:4]])
    print(f"\nReconstructed word: '{hope_word}'")

# Check what's currently detected as title size
print("\n=== TITLE SIZE ANALYSIS ===")
sizes = [elem["size"] for elem in all_elements if len(elem["text"]) > 3]
from collections import Counter
size_counts = Counter(sizes)
print("Size frequency:")
for size, count in size_counts.most_common():
    print(f"  Size {size:.1f}: {count} occurrences")

body_text_size = size_counts.most_common()[0][0] if size_counts else 12
unique_sizes = sorted(set([elem["size"] for elem in all_elements]), reverse=True)
title_size = unique_sizes[0] if unique_sizes else body_text_size

print(f"\nDetected title size: {title_size}")
print(f"Detected body text size: {body_text_size}")

print("\nElements with title size:")
for elem in all_elements:
    if elem["size"] == title_size and elem["page"] <= 2:
        print(f"  '{elem['text']}' at Y:{elem['y_position']:.1f}")
