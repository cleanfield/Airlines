# Airlines Betrouwbaarheid - Web Interface

Een moderne, real-time webinterface voor het bekijken van airline betrouwbaarheidsrankings.

## ✨ Features

- **Real-time Rankings** - Live ranking van airlines op betrouwbaarheid
- **Automatische Updates** - Data wordt elke 5 minuten automatisch bijgewerkt
- **Interactieve Filters** - Filter op vluchttype, periode en minimum vluchten
- **Responsive Design** - Werkt perfect op desktop, tablet en mobiel
- **Premium UI** - Moderne, professionele interface met animaties
- **Live Statistieken** - Overzicht van beste airline, gemiddelden en trends

## 🚀 Quick Start

### 1. Installeer Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start de Web Server

```bash
python web_api.py
```

Of gebruik het start script:

**Windows (PowerShell):**

```powershell
.\start_web.ps1
```

**Windows (CMD):**

```cmd
start_web.bat
```

### 3. Open in Browser

Ga naar: **<http://localhost:5000>**

## 📊 API Endpoints

### GET /api/rankings

Haal airline rankings op.

**Query Parameters:**

- `days` - Aantal dagen terug (default: 30)
- `flight_type` - 'departures', 'arrivals', of 'all' (default: 'all')
- `min_flights` - Minimum aantal vluchten (default: 10)

**Voorbeeld:**

```
GET /api/rankings?days=30&flight_type=all&min_flights=10
```

**Response:**

```json
{
  "airlines": [
    {
      "code": "KL",
      "name": "KLM Royal Dutch Airlines",
      "totalFlights": 245,
      "onTimePercentage": 92.5,
      "avgDelay": -2.3,
      "reliabilityScore": 94.8,
      "trend": 2.5
    }
  ],
  "totalFlights": 5432,
  "lastUpdate": "2026-01-24T22:45:00",
  "dateRange": {
    "start": "2025-12-25T22:45:00",
    "end": "2026-01-24T22:45:00",
    "days": 30
  }
}
```

### GET /api/stats

Haal algemene statistieken op.

**Response:**

```json
{
  "totalFlights": 5432,
  "totalAirlines": 25,
  "onTimePercentage": 87.3,
  "avgDelay": 8.5
}
```

### GET /api/health

Health check endpoint.

## ⚙️ Configuratie

### Environment Variables

Voeg toe aan `.env`:

```env
# Web Server
WEB_PORT=5000
FLASK_DEBUG=True
```

### Auto-Refresh Interval

Pas aan in `web/app.js`:

```javascript
const CONFIG = {
    refreshInterval: 300000,  // 5 minuten in milliseconden
    mockData: false
};
```

## 🎨 Interface Features

### Rankings Tabel

- **Top 3 Badges** - Goud, zilver, brons voor top 3 airlines
- **Color Coding** - Visuele indicatie van prestaties
  - 🟢 Uitstekend (90%+)
  - 🟡 Goed (80-90%)
  - 🟠 Gemiddeld (70-80%)
  - 🔴 Matig (<70%)
- **Trend Indicators** - Pijlen tonen verbetering/verslechtering
- **Hover Effects** - Interactieve rijen met smooth animaties

### Filters

- **Vluchttype** - Vertrek, aankomst of beide
- **Periode** - 7, 14, 30 of 90 dagen
- **Min. vluchten** - Filter op minimum aantal vluchten
- **Refresh knop** - Handmatig data verversen

### Statistiek Cards

- **Beste Airline** - Hoogste betrouwbaarheidsscore
- **Gemiddeld op tijd** - Percentage van alle airlines
- **Gemiddelde vertraging** - Over alle vluchten
- **Totaal airlines** - Aantal geanalyseerde airlines

## 🔄 Automatische Updates

De webpagina werkt met automatische updates:

1. **Initiële load** - Data wordt geladen bij openen pagina
2. **Auto-refresh** - Elke 5 minuten automatisch nieuwe data
3. **Handmatig refresh** - Via de refresh knop
4. **Filter updates** - Direct bij wijzigen van filters

## 📱 Responsive Design

De interface past zich aan aan verschillende schermformaten:

- **Desktop** - Volledige tabel met alle kolommen
- **Tablet** - Geoptimaliseerde layout
- **Mobiel** - Compacte weergave met belangrijkste info

## 🎯 Betrouwbaarheidsscore

De score wordt berekend als:

```
Betrouwbaarheidsscore = Op tijd % - (Gemiddelde vertraging / 10)
```

**Voorbeeld:**

- Op tijd: 92%
- Gem. vertraging: -2 minuten
- Score: 92 - (-2/10) = 92.2

## 🚀 Deployment

### Lokaal Testen

```bash
python web_api.py
```

### Productie (met Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_api:app
```

### Digital Ocean Deployment

De web interface is geïntegreerd in de deployment scripts:

```bash
# Deploy inclusief web interface
.\deploy_to_do.ps1 -DropletIP YOUR_IP
```

De web server draait automatisch op poort 5000.

### Nginx Reverse Proxy

Voor productie, gebruik nginx als reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔧 Development

### Mock Data Mode

Voor development zonder database:

```javascript
// In web/app.js
const CONFIG = {
    mockData: true  // Gebruik mock data
};
```

### Live Reload

Flask heeft automatische reload in debug mode:

```bash
export FLASK_DEBUG=True  # Linux/Mac
set FLASK_DEBUG=True     # Windows CMD
$env:FLASK_DEBUG="True"  # Windows PowerShell

python web_api.py
```

## 📁 Bestandsstructuur

```
Airlines/
├── web/
│   ├── index.html      # Hoofdpagina
│   ├── styles.css      # Styling
│   └── app.js          # JavaScript applicatie
├── web_api.py          # Flask API backend
├── start_web.bat       # Windows start script
└── start_web.ps1       # PowerShell start script
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Database Connection Error

Controleer:

1. Database credentials in `.env`
2. SSH tunnel naar database server
3. Database service draait

### No Data Showing

1. Check API endpoint: <http://localhost:5000/api/health>
2. Controleer browser console voor errors
3. Verifieer dat er data in de database staat

### CORS Errors

Flask-CORS is geïnstalleerd, maar voor productie:

```python
# In web_api.py
CORS(app, resources={r"/api/*": {"origins": "https://your-domain.com"}})
```

## 📊 Performance

- **Auto-refresh**: Elke 5 minuten
- **API Response**: < 500ms (gemiddeld)
- **Page Load**: < 2 seconden
- **Database Queries**: Geoptimaliseerd met indexen

## 🔒 Security

Voor productie:

1. **Disable Debug Mode**

   ```python
   app.run(debug=False)
   ```

2. **Use HTTPS**
   - Configureer SSL certificaat
   - Gebruik Let's Encrypt

3. **Rate Limiting**

   ```bash
   pip install flask-limiter
   ```

4. **Authentication** (optioneel)
   - Voeg basic auth toe
   - Of gebruik OAuth

## 📝 License

Onderdeel van Airlines Reliability Tracker project.

---

**Geniet van de real-time airline rankings!** ✈️
