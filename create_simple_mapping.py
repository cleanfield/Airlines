
import json

try:
    with open('destinations_full.json', 'r', encoding='utf-8') as f:
        full_list = json.load(f)
        
    mapping = {}
    for item in full_list:
        code = item.get('code')
        name = item.get('name')
        if code and name:
            mapping[code] = name
            
    with open('destination_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
        
    print(f"Created simple mapping with {len(mapping)} entries")
    
except Exception as e:
    print(e)
