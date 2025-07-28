import json

# Check PDF02 current state
with open('sample_dataset/outputs/file02.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Current PDF02 headings: {len(data['outline'])}")
print("\nFirst 10 headings:")
for i, h in enumerate(data['outline'][:10]):
    print(f"{i+1}. {h['level']}: {h['text']}")

print(f"\nTotal: {len(data['outline'])} headings")
