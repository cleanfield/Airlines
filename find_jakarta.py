import json

# Load destinations
with open('C:/Projects/Airlines/destinations_full.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find Jakarta
jakarta = [d for d in data if 'jakarta' in d.get('name', '').lower() or d.get('code') in ['CGK', 'JKT', 'HLP']]

print('Jakarta airports found:')
for d in jakarta:
    print(f"  {d['code']}: {d['name']} - {d.get('country', 'N/A')}")
