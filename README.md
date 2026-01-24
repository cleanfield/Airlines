# Airline Reliability Tracker

A Python application that collects flight arrival and departure data from airport APIs, stores it in a MariaDB database, and provides real-time airline reliability rankings through a modern web interface.

## 🌟 Features

### ✈️ Multi-Airport Support

- Currently supports Schiphol Airport API (v4)
- Designed to easily add more airports
- Historical and future flight data collection

### 📊 Comprehensive Analysis

- On-time performance percentage
- Average delays calculation
- Reliability scores
- Delay distributions
- Trend analysis (comparison with previous periods)

### 🌐 Real-Time Web Interface

- **Live Rankings** - Real-time airline reliability rankings
- **Auto-Refresh** - Data updates every 5 minutes automatically
- **Interactive Filters** - Filter by flight type, date range, and minimum flights
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Premium UI** - Modern, professional interface with animations
- **Live Statistics** - Best airline, averages, and trends

### 💾 Database Storage

- MariaDB for persistent data storage
- SSH tunnel support for secure remote connections
- Efficient data retrieval (data collected only once)
- Comprehensive logging system

### 📈 Rich Visualizations

- Airline reliability rankings charts
- On-time performance scatter plots
- Delay distribution histograms
- Daily performance trends

### 🔄 Automated Data Collection

- Scheduled daily collection (configurable)
- Date range support
- Automatic processing and analysis
- Systemd service integration

## 🚀 Quick Start

### Local Development

#### 1. Installation

```bash
# Clone the repository
git clone https://github.com/cleanfield/Airlines.git
cd Airlines

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configuration

Copy `.env.example` to `.env` and configure:

```env
# Schiphol API
SCHIPHOL_APP_ID=your_app_id_here
SCHIPHOL_APP_KEY=your_app_key_here

# MariaDB Connection
MARIA_SERVER=your_server_ip
MARIA_SSH_USER=your_ssh_user
MARIA_SSH_PORT=22
MARIA_ID_ED25519=path/to/id_ed25519
MARIA_ID_ED25519_PUB=path/to/id_ed25519.pub
MARIA_ID_ED25519_PASSPHRASE=your_passphrase

# Database
MARIA_DB=flights
MARIA_DB_USER=your_db_user
MARIA_DB_PASSWORD=your_db_password
MARIA_DB_PORT=3306

# Web Server (optional)
WEB_PORT=5000
FLASK_DEBUG=True
```

#### 3. Run Analysis

```bash
# Collect and analyze today's flight data
python main.py analyze

# Analyze the past week
python main.py analyze --days-back 7
```

#### 4. Start Web Interface

```bash
# Start the web server
python web_api.py

# Or use the start script
.\start_web.ps1  # PowerShell
.\start_web.bat  # CMD
```

Access the web interface at: **<http://localhost:5000>**

## 🌐 Digital Ocean Deployment

Deploy your Airlines Reliability Tracker to Digital Ocean for 24/7 operation and public web access.

### Prerequisites

- Digital Ocean account
- Ubuntu 22.04 LTS droplet (minimum 1GB RAM, 1 vCPU)
- SSH access to your droplet
- Domain name (optional, for SSL/HTTPS)

### Quick Deployment

#### Option 1: Automated Deployment (Recommended)

From your local machine (Windows PowerShell):

```powershell
# Deploy to Digital Ocean
.\deploy_to_do.ps1 -DropletIP YOUR_DROPLET_IP
```

This will:

1. Package your application
2. Upload to your droplet
3. Run the deployment script automatically

#### Option 2: Manual Deployment

```bash
# 1. Connect to your droplet
ssh root@YOUR_DROPLET_IP

# 2. Upload files (from local machine)
scp -r c:\Projects\Airlines\* root@YOUR_DROPLET_IP:/opt/airlines/

# 3. On the droplet, run deployment
cd /opt/airlines
chmod +x deploy.sh
sudo ./deploy.sh
```

### Deploy Web Interface (Public Access)

Make your website publicly accessible:

```bash
# On your droplet
cd /opt/airlines
chmod +x deploy_web.sh
sudo ./deploy_web.sh
```

Or with a custom domain:

```bash
sudo ./deploy_web.sh your-domain.com
```

This installs:

- **Nginx** - Web server / reverse proxy
- **Gunicorn** - Production WSGI server (4 workers)
- **Systemd service** - Auto-start and monitoring
- **UFW Firewall** - Security configuration

### Access Your Website

**Without domain:**

```
http://YOUR_DROPLET_IP
```

**With domain:**

```
http://your-domain.com
```

### Add SSL/HTTPS (Free with Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

After SSL setup:

```
https://your-domain.com  ✅ Secure!
```

### Digital Ocean Configuration in .env

Add these variables to your `.env` file on the droplet:

```env
# Digital Ocean Droplet Info (for reference)
DROPLET_IP=your_droplet_ip
DROPLET_NAME=airlines-tracker
DOMAIN=your-domain.com  # Optional

# Web Server
WEB_PORT=5000
FLASK_DEBUG=False  # Set to False for production
```

### Service Management

```bash
# Data Collection Service
sudo systemctl status airlines-collector.timer
sudo systemctl start airlines-collector.service  # Manual run
sudo journalctl -u airlines-collector.service -f  # View logs

# Web Interface Service
sudo systemctl status airlines-web.service
sudo systemctl restart airlines-web.service
sudo journalctl -u airlines-web.service -f

# Nginx
sudo systemctl status nginx
sudo systemctl restart nginx
sudo tail -f /var/log/nginx/airlines-access.log
```

### Monitoring

```bash
# Check website health
curl http://localhost:5000/api/health

# View all services
systemctl list-units | grep airlines

# Check firewall
sudo ufw status
```

### Deployment Documentation

For detailed deployment instructions, see:

- **`DEPLOYMENT_STAPPENPLAN.md`** - Step-by-step deployment checklist
- **`WEB_DEPLOYMENT_GUIDE.md`** - Complete web deployment guide
- **`WEB_DEPLOYMENT_QUICK_REFERENCE.md`** - Quick command reference
- **`DEPLOYMENT.md`** - General deployment documentation

## 📁 Project Structure

```
Airlines/
├── main.py                     # Main application with CLI
├── web_api.py                  # Flask web API backend
├── schiphol_api.py            # Schiphol Airport API client
├── data_processor.py          # Data processing and calculations
├── visualizer.py              # Chart and graph generation
├── database.py                # Database connection and queries
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── .env                       # Credentials (not in git)
├── .env.example              # Template for credentials
│
├── web/                       # Web interface
│   ├── index.html            # Main web page
│   ├── styles.css            # Styling
│   └── app.js                # JavaScript application
│
├── deploy.sh                  # Main deployment script
├── deploy_web.sh             # Web deployment script
├── deploy_to_do.ps1          # Windows deployment helper
├── start_web.ps1             # Start web server (Windows)
│
├── data/                      # Data storage
│   ├── raw/                  # Raw JSON from APIs
│   ├── processed/            # Processed CSV files
│   └── reports/              # Reports and visualizations
│
└── docs/                      # Documentation
    ├── README.md             # This file
    ├── USAGE.md              # Detailed usage guide
    ├── WEB_README.md         # Web interface documentation
    ├── DEPLOYMENT_STAPPENPLAN.md  # Deployment checklist
    └── WEB_DEPLOYMENT_GUIDE.md    # Web deployment guide
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Schiphol API
SCHIPHOL_APP_ID=your_app_id
SCHIPHOL_APP_KEY=your_app_key

# MariaDB Connection
MARIA_SERVER=your_server_ip
MARIA_SSH_USER=your_ssh_user
MARIA_SSH_PORT=22
MARIA_ID_ED25519=/path/to/id_ed25519
MARIA_ID_ED25519_PUB=/path/to/id_ed25519.pub
MARIA_ID_ED25519_PASSPHRASE=your_passphrase

# Database
MARIA_DB=flights
MARIA_DB_USER=your_db_user
MARIA_DB_PASSWORD=your_db_password
MARIA_DB_PORT=3306

# Web Server
WEB_PORT=5000
FLASK_DEBUG=True  # False for production

# Digital Ocean (optional, for reference)
DROPLET_IP=your_droplet_ip
DOMAIN=your-domain.com
```

### Application Settings (config.py)

```python
# Reliability calculation settings
RELIABILITY_SETTINGS = {
    'on_time_threshold_minutes': 15,
    'minimum_flights_for_ranking': 10,
}

# Data collection settings
COLLECTION_SETTINGS = {
    'max_pages': 10,
    'delay_between_requests': 1,
}
```

## 📊 Usage Examples

### Data Collection

```bash
# Collect today's flights
python main.py collect

# Collect past 7 days
python main.py collect --days-back 7

# Collect next 3 days (scheduled flights)
python main.py collect --days-forward 3
```

### Data Processing

```bash
# Process departures
python main.py process departures 2024-01-22_to_2024-01-22

# Process arrivals
python main.py process arrivals 2024-01-22_to_2024-01-22
```

### Generate Visualizations

```bash
# Create charts for departures
python main.py visualize departures 2024-01-22_to_2024-01-22
```

### Full Analysis (Recommended)

```bash
# Complete workflow: collect, process, and visualize
python main.py analyze --days-back 7
```

### Web Interface

```bash
# Start web server
python web_api.py

# Access at http://localhost:5000
```

## 🌐 API Endpoints

### GET /api/rankings

Get airline reliability rankings.

**Parameters:**

- `days` - Number of days to look back (default: 30)
- `flight_type` - 'departures', 'arrivals', or 'all' (default: 'all')
- `min_flights` - Minimum number of flights (default: 10)

**Example:**

```
GET /api/rankings?days=30&flight_type=all&min_flights=10
```

### GET /api/stats

Get overall statistics.

### GET /api/health

Health check endpoint.

## 🎯 Reliability Scoring

**Formula:**

```
Reliability Score = On-time % - (Average Delay / 10)
```

**On-Time Definition:**

- Flight is on-time if within ±15 minutes of scheduled time
- Configurable in `config.py`

**Minimum Flights:**

- Airlines need at least 10 flights for ranking
- Prevents unreliable statistics from small samples

## 📈 Output Files

### Reports Directory (`data/reports/`)

- `reliability_report_*.txt` - Text reports with rankings
- `airline_rankings_*.png` - Bar chart of top 20 airlines
- `on_time_performance_*.png` - Scatter plot
- `delay_distribution_*.png` - Histogram
- `daily_performance_*.png` - Line chart

### Processed Data (`data/processed/`)

- `processed_departures_*.csv` - Individual flight records
- `airline_stats_*.csv` - Aggregated airline statistics

### Raw Data (`data/raw/`)

- `departures_*.json` - Raw departure data from API
- `arrivals_*.json` - Raw arrival data from API

## 🔒 Security

### Production Deployment

- Firewall (UFW) configured
- Only essential ports open (22, 80, 443)
- SSL/HTTPS with Let's Encrypt
- Non-root user for application
- Secure file permissions (`.env` = 600)
- Environment variables for sensitive data

### Best Practices

- Keep system updated: `sudo apt-get update && sudo apt-get upgrade`
- Use strong passwords
- Enable automatic security updates
- Monitor logs regularly
- Use SSH keys (not passwords)

## 🐛 Troubleshooting

### Local Development

**No Data Collected:**

- Check internet connection
- Verify API credentials in `.env`
- Check API rate limits

**Database Connection Error:**

- Verify database credentials
- Check SSH tunnel connection
- Ensure database service is running

### Digital Ocean Deployment

**Website Not Accessible:**

```bash
sudo systemctl status airlines-web.service
sudo systemctl status nginx
sudo ufw status
```

**502 Bad Gateway:**

```bash
sudo systemctl restart airlines-web.service
sudo journalctl -u airlines-web.service -f
```

**SSL Certificate Issues:**

```bash
sudo certbot renew
sudo systemctl restart nginx
```

## 📚 Documentation

- **README.md** - This file (overview and quick start)
- **USAGE.md** - Detailed usage instructions
- **WEB_README.md** - Web interface documentation
- **DEPLOYMENT_STAPPENPLAN.md** - Step-by-step deployment checklist
- **WEB_DEPLOYMENT_GUIDE.md** - Complete web deployment guide
- **WEB_DEPLOYMENT_QUICK_REFERENCE.md** - Quick command reference
- **DEPLOYMENT.md** - General deployment documentation
- **DEPLOYMENT_QUICK_REFERENCE.md** - Deployment commands

## 🚀 Future Enhancements

- [ ] Add more airport APIs (Heathrow, JFK, etc.)
- [ ] Email alerts for significant delays
- [ ] Historical trend analysis
- [ ] Machine learning predictions
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Advanced filtering options
- [ ] Export to PDF/Excel

## 📄 License

This project is for educational and research purposes. Please respect the terms of service of the airport APIs you use.

## 🙏 Acknowledgments

- Schiphol Airport for providing the Flight API
- Digital Ocean for cloud hosting
- Airport operators worldwide for making flight data accessible

---

**Live Demo:** http://YOUR_DROPLET_IP (after deployment)

**Repository:** <https://github.com/cleanfield/Airlines>

**Contact:** For Schiphol API support: <api-support@schiphol.nl>

---

Made with ✈️ by cleanfield
