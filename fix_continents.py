"""
Fix destinations_full.json - Move countries from 'Other' to correct continents
"""
import json
import os
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEST_FILE = os.path.join(SCRIPT_DIR, 'destinations_full.json')

COUNTRY_TO_CONTINENT = {
    'Antartica': 'Antarctica',
    'British Indian Ocean Territory (the)': 'Asia',
    'Dominican Republic': 'North America',
    'Equatorial Gui': 'Africa',
    'Fiji Islands': 'Oceania',
    'French Guyana': 'South America',
    'French Polynesia': 'Oceania',
    'Guernsey': 'Europe',
    'Guinea Bissau': 'Africa',
    'Jersey': 'Europe',
    'Jordania': 'Asia',
    'Kampuchea': 'Asia',
    'Kazakstan': 'Asia',
    'Korea (South)': 'Asia',
    'Kyrgystan': 'Asia',
    'Macao': 'Asia',
    'Marshall Islands': 'Oceania',
    'Northern Mariana Islands': 'Oceania',
    'Papua New Guinea': 'Oceania',
    'Russia (CIS)': 'Europe',
    'Saint Barthelemy': 'North America',
    'Saint Kitts &': 'North America',
    'Saint Martin (French part)': 'North America',
    'Saint Vincent': 'North America',
    'Saint Vincent and the Grenadines': 'North America',
    'Sao Tome & Principe': 'Africa',
    'Sao Tome and P': 'Africa',
    'Saudia Arabia': 'Asia',
    'Serbia ': 'Europe',
    'Sint Maarten (Dutch part)': 'North America',
    'Solomon Islands': 'Oceania',
    'St. Helena': 'Africa',
    'St. Pierre & M': 'North America',
    'Surinam': 'South America',
    'Svalbard and Jan Mayen': 'Europe',
    'The Netherlands': 'Europe',
    'Trinidad and Tobago': 'North America',
    'Tunesia': 'Africa',
    'Turks & Caicos': 'North America',
    'Türkiye': 'Europe',
    'United Arab Emirates (the)': 'Asia',
    'United Kingdom of Great Britain and Northern Ireland': 'Europe',
    'Vanuata': 'Oceania',
}

def main():
    # Backup
    backup_path = DEST_FILE + '.bak'
    shutil.copy2(DEST_FILE, backup_path)
    print(f"Backup created: {backup_path}")

    with open(DEST_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    fixed = 0
    for entry in data:
        if entry.get('continent') == 'Other' and entry.get('country') in COUNTRY_TO_CONTINENT:
            entry['continent'] = COUNTRY_TO_CONTINENT[entry['country']]
            fixed += 1

    remaining = [d for d in data if d.get('continent') == 'Other']

    with open(DEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Fixed {fixed} entries")
    print(f"Remaining 'Other': {len(remaining)}")
    
    # Verify UK
    uk = [d for d in data if d.get('country') and 'United Kingdom' in d['country']]
    print(f"UK airports now under: {set(d['continent'] for d in uk)}")

if __name__ == '__main__':
    main()
