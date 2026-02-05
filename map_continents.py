
import json

CONTINENT_MAPPING = {
    # Africa

    "Algeria": "Africa", "Angola": "Africa", "Benin": "Africa", "Botswana": "Africa",
    "Burkina Faso": "Africa", "Burundi": "Africa", "Cameroon": "Africa", "Cameroun": "Africa",
    "Cape Verde": "Africa", "Cape Verde Islands": "Africa", "Central Africa": "Africa",
    "Central African Republic": "Africa", "Chad": "Africa", "Comoros": "Africa", "Congo": "Africa",
    "Congo (the)": "Africa", "Congo (the Democratic Republic of the)": "Africa",
    "Côte d'Ivoire": "Africa", "Djibouti": "Africa", "Egypt": "Africa", "Equatorial Guinea": "Africa",
    "Eritrea": "Africa", "Ethiopia": "Africa", "Gabon": "Africa", "Gambia": "Africa",
    "Ghana": "Africa", "Guinea": "Africa", "Guinea-Benin": "Africa", "Guinea-Bissau": "Africa",
    "Ivory Coast": "Africa", "Kenya": "Africa", "Lesotho": "Africa", "Liberia": "Africa",
    "Libya": "Africa", "Madagascar": "Africa", "Malawi": "Africa", "Mali": "Africa",
    "Mauritania": "Africa", "Mauritius": "Africa", "Mayotte": "Africa", "Morocco": "Africa",
    "Mozambique": "Africa", "Namibia": "Africa", "Niger": "Africa", "Nigeria": "Africa",
    "Reunion": "Africa", "Rwanda": "Africa", "Saint Helena": "Africa", "Sao Tome & Pri": "Africa",
    "Sao Tome and Principe": "Africa", "Senegal": "Africa", "Seychelles": "Africa",
    "Sierra Leone": "Africa", "Somalia": "Africa", "South Africa": "Africa",
    "South Sudan": "Africa", "Sudan": "Africa", "Swaziland": "Africa", "Tanzania": "Africa",
    "Tanzania, United Republic of": "Africa", "Togo": "Africa", "Tunisia": "Africa",
    "Uganda": "Africa", "Western Sahara": "Africa", "Zambia": "Africa", "Zimbabwe": "Africa",

    

    # Asia
    "Afghanistan": "Asia", "Armenia": "Asia", "Azerbaijan": "Asia", "Azerbaijani": "Asia",
    "Bahrain": "Asia", "Bangladesh": "Asia", "Bhutan": "Asia", "Brunei": "Asia", "Cambodia": "Asia",
    "China": "Asia", "Cyprus": "Asia", "Georgia": "Asia", "Hong Kong": "Asia", "India": "Asia",
    "Indonesia": "Asia", "Iran": "Asia", "Iraq": "Asia", "Israel": "Asia", "Japan": "Asia",
    "Jordan": "Asia", "Kazakhstan": "Asia", "Korea (the Democratic People's Republic of)": "Asia",
    "Korea (the Republic of)": "Asia", "Kuwait": "Asia", "Kyrgyzstan": "Asia", "Laos": "Asia",
    "Lebanon": "Asia", "Macau": "Asia", "Malaysia": "Asia", "Maldives": "Asia", "Mongolia": "Asia",
    "Myanmar": "Asia", "Nepal": "Asia", "North Korea": "Asia", "Oman": "Asia", "Pakistan": "Asia",
    "Palestine": "Asia", "Palestinian Territory": "Asia", "Philippines": "Asia", "Qatar": "Asia",
    "Russia": "Asia", "Russian Feder": "Asia", "Russian Federation (the)": "Asia",
    "Saudi Arabia": "Asia", "Singapore": "Asia", "South Korea": "Asia", "Sri Lanka": "Asia",
    "Syria": "Asia", "Taiwan": "Asia", "Tajikistan": "Asia", "Thailand": "Asia", "Timor-Leste": "Asia",
    "Turkey": "Asia", "Turkmenistan": "Asia", "United Arab Emirates": "Asia", "Uzbekistan": "Asia",
    "Vietnam": "Asia", "Yemen": "Asia",

    # Europe
    "Aland Islands": "Europe", "Albania": "Europe", "Andorra": "Europe", "Austria": "Europe",
    "Belarus": "Europe", "Belgium": "Europe", "Bosnia Herzegovina": "Europe",
    "Bosnia-Hercego": "Europe", "Bulgaria": "Europe", "Croatia": "Europe", "Czech Republic": "Europe",
    "Denmark": "Europe", "Estonia": "Europe", "Faroe Islands": "Europe", "Finland": "Europe",
    "France": "Europe", "Germany": "Europe", "Gibraltar": "Europe", "Greece": "Europe",
    "Greenland": "Europe", "Holy See (Vatican City State)": "Europe", "Hungary": "Europe",
    "Iceland": "Europe", "Ireland": "Europe", "Italy": "Europe", "Kosovo": "Europe",
    "Latvia": "Europe", "Liechtenstein": "Europe", "Lithuania": "Europe", "Luxembourg": "Europe",
    "Macedonia": "Europe", "Malta": "Europe", "Moldova": "Europe", "Moldova (the Republic of)": "Europe",
    "Monaco": "Europe", "Montenegro": "Europe", "Netherlands": "Europe", "Norway": "Europe",
    "Poland": "Europe", "Portugal": "Europe", "Romania": "Europe", "San Marino": "Europe",
    "Serbia": "Europe", "Slovakia": "Europe", "Slovenia": "Europe", "Spain": "Europe",
    "Svalbard & Jan": "Europe", "Sweden": "Europe", "Switzerland": "Europe", "Ukraine": "Europe",
    "United Kingdom": "Europe", "Yugoslavia": "Europe",

    # North America
    "Anguilla": "North America", "Antigua & Barb": "North America", "Aruba": "North America",
    "Bahamas": "North America", "Barbados": "North America", "Belize": "North America",
    "Bermuda Islands": "North America", "Bonaire, Sint Eustatius and Saba": "North America",
    "British Virgin": "North America", "Canada": "North America", "Cayman Islands": "North America",
    "Costa Rica": "North America", "Cuba": "North America", "Curacao": "North America",
    "Dominica": "North America", "Dominican Repu": "North America", "El Salvador": "North America",
    "Grenada": "North America", "Guadeloupe": "North America", "Guatemala": "North America",
    "Haiti": "North America", "Honduras": "North America", "Jamaica": "North America",
    "Martinique": "North America", "Mexico": "North America", "Montserrat": "North America",
    "Netherlands Antilles": "North America", "Nicaragua": "North America", "Panama": "North America",
    "Puerto Rico": "North America", "Saint Barthele": "North America", "Saint Kitts": "North America",
    "Saint Lucia": "North America", "Saint Martin": "North America", "Saint Pierre": "North America",
    "St. Vincent": "North America", "Trinidad And T": "North America", "Turks And Caic": "North America",
    "United States": "North America", "United States of America (the)": "North America",
    "Virgin Islands": "North America", "Virgin Islands (British)": "North America",
    "Virgin Islands (U.S.)": "North America",

    # Oceania
    "American Samoa": "Oceania", "Australia": "Oceania", "Christmas Isla": "Oceania",
    "Cocos (Keeling": "Oceania", "Cook Islands": "Oceania", "Fiji": "Oceania",
    "French Polynes": "Oceania", "Guam": "Oceania", "Kiribati": "Oceania",
    "Marshall Islan": "Oceania", "Micronesia": "Oceania", "Nauru": "Oceania",
    "New Caledonia": "Oceania", "New Zealand": "Oceania", "Niue": "Oceania",
    "Norfolk Island": "Oceania", "Northern Maria": "Oceania", "Palau": "Oceania",
    "Papua New Guin": "Oceania", "Pitcairn": "Oceania", "Samoa": "Oceania",
    "Solomon Island": "Oceania", "Tokelau": "Oceania", "Tonga": "Oceania", "Tuvalu": "Oceania",
    "Vanuatu": "Oceania", "Wallis & Futun": "Oceania", "Wallis And Fut": "Oceania",

    # South America
    "Argentina": "South America", "Bolivia": "South America", "Brasil": "South America",
    "Brazil": "South America", "Chile": "South America", "Chili": "South America",
    "Colombia": "South America", "Ecuador": "South America",
    "Falkland Islan": "South America", "Falkland Islands (Malvinas)": "South America",
    "French Guiana": "South America", "Guyana": "South America", "Paraguay": "South America",
    "Peru": "South America", "Suriname": "South America", "Uruguay": "South America",
    "Venezuela": "South America", "Venezuelane": "South America",

}

def process():
    try:
        with open('destination_details.json', 'r', encoding='utf-8') as f:
            dests = json.load(f)
            
        final_list = []
        unknown_countries = set()
        
        for iata, info in dests.items():
            country = info.get('country')
            name = info.get('name')
            
            if not country:
                continent = "Unknown"
            else:
                continent = CONTINENT_MAPPING.get(country)
                if not continent:
                    # Try partial match or manual fixes
                    if country in ["USA"]: continent = "North America"
                    elif country in ["UK"]: continent = "Europe"
                    else:
                        continent = "Other"
                        unknown_countries.add(country)
            
            final_list.append({
                'code': iata,
                'name': name,
                'country': country,
                'continent': continent
            })
            
        print(f"Processed {len(final_list)} destinations.")
        print(f"Unknown countries ({len(unknown_countries)}):")
        for c in sorted(list(unknown_countries)):
            print(c)
            
        with open('destinations_full.json', 'w', encoding='utf-8') as f:
            json.dump(final_list, f, indent=2)
            
    except Exception as e:
        print(e)

if __name__ == "__main__":
    process()
