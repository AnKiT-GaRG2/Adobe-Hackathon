import json

# Check PDF04 current state
with open('sample_dataset/outputs/file04.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Current PDF04 headings: {len(data['outline'])}")
print("\nAll headings:")
for i, h in enumerate(data['outline']):
    print(f"{i+1}. {h['level']}: {h['text']}")

print(f"\nTotal: {len(data['outline'])} headings")
print(f"Title: {data['title']}")
