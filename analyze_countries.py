
import json

try:
    with open('destination_details.json', 'r', encoding='utf-8') as f:
        dests = json.load(f)

    countries = set()
    for iata, info in dests.items():
        c = info.get('country')
        if c:
            countries.add(c)

    print(f"Total unique countries: {len(countries)}")
    print("Sample countries:")
    for c in sorted(list(countries))[:50]:
        print(c)
        
except Exception as e:
    print(e)
