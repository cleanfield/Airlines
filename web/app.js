// Airlines Betrouwbaarheid - Main Application
// Handles data loading, filtering, and display

// Configuration
const CONFIG = {
    apiEndpoint: '/api/rankings',  // Flask API endpoint
    refreshInterval: 300000,  // 5 minutes (auto-refresh)
    mockData: false  // Use real data from API (set to true for demo mode)
};

// State
let currentData = null;
let filters = {
    flightType: 'all',
    dateRange: 30,
    minFlights: 10
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadData();
    updateLastUpdateTime();

    // Auto-refresh
    setInterval(() => {
        loadData();
        updateLastUpdateTime();
    }, CONFIG.refreshInterval);
});

// Event Listeners
function initializeEventListeners() {
    document.getElementById('flightType').addEventListener('change', (e) => {
        filters.flightType = e.target.value;
        loadData();
    });

    document.getElementById('dateRange').addEventListener('change', (e) => {
        filters.dateRange = parseInt(e.target.value);
        loadData();
    });

    document.getElementById('minFlights').addEventListener('change', (e) => {
        filters.minFlights = parseInt(e.target.value);
        loadData();
    });

    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadData();
    });

    // Sort headers
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            toggleSort(th.dataset.sort);
        });
        th.style.cursor = 'pointer';
    });
    // Destination filters
    document.getElementById('filterContinent').addEventListener('change', (e) => {
        updateCountrySelect(e.target.value);
    });

    document.getElementById('filterCountry').addEventListener('change', (e) => {
        updateAirportSelect(e.target.value);
    });

    document.getElementById('filterAirport').addEventListener('change', (e) => {
        filters.destination = e.target.value;
        loadData();
    });

    // Check initial visibility
    toggleDestinationFilters(filters.flightType);
}

function toggleDestinationFilters(type) {
    const group = document.getElementById('destinationFilterGroup');
    if (type === 'departures' || type === 'all') { // Allowing for 'all' too as it might be useful
        group.style.display = 'block';
        if (!destinationsData) {
            loadDestinations();
        }
    } else {
        group.style.display = 'none';
        filters.destination = null; // Clear filter
        document.getElementById('filterAirport').value = "";
    }
}


// Data Loading
async function loadData() {
    showLoading();

    try {
        let data;

        if (CONFIG.mockData) {
            // Use mock data for demonstration
            data = await generateMockData();
        } else {
            // Fetch from API with filters
            const params = new URLSearchParams({
                days: filters.dateRange,
                flight_type: filters.flightType,
                min_flights: filters.minFlights
            });

            if (filters.destination) {
                params.append('destination', filters.destination);
            }


            const response = await fetch(`${CONFIG.apiEndpoint}?${params.toString()}`);
            if (!response.ok) throw new Error('Failed to fetch data');
            data = await response.json();
        }

        currentData = data;

        // Update First Update Metadata
        if (data.firstUpdate) {
            const firstDate = new Date(data.firstUpdate);
            document.getElementById('firstUpdate').textContent = firstDate.toLocaleString('nl-NL', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
        }

        applyFilters();
        hideLoading();

    } catch (error) {
        showError(error.message);
    }
}

// Apply Filters (Client-side sorting only)
function applyFilters() {
    if (!currentData) return;

    let filtered = [...currentData.airlines];

    // Note: Flight type and min flights filtering is now done on the backend

    // Sort by selected column
    filtered.sort((a, b) => {
        let valA = a[sortState.column];
        let valB = b[sortState.column];

        if (sortState.desc) {
            return valB - valA;
        } else {
            return valA - valB;
        }
    });

    displayRankings(filtered);
    displayStats(filtered);
    updateSortIcons();
}

// Sort State
let sortState = {
    column: 'reliabilityScore',
    desc: true
};

function toggleSort(column) {
    if (sortState.column === column) {
        sortState.desc = !sortState.desc;
    } else {
        sortState.column = column;
        sortState.desc = true; // Default to desc for new column
    }
    applyFilters();
}

function updateSortIcons() {
    // Reset all icons
    document.querySelectorAll('.sort-icon').forEach(icon => {
        icon.textContent = '⇅';
        icon.style.opacity = '0.3';
    });

    // Update active icon
    const activeHeader = document.querySelector(`th[data-sort="${sortState.column}"]`);
    if (activeHeader) {
        const icon = activeHeader.querySelector('.sort-icon');
        if (icon) {
            icon.textContent = sortState.desc ? '↓' : '↑';
            icon.style.opacity = '1';
        }
    }
}

// Display Rankings
function displayRankings(airlines) {
    const tbody = document.getElementById('rankingsTableBody');
    tbody.innerHTML = '';

    airlines.forEach((airline, index) => {
        const rank = index + 1;
        const row = createAirlineRow(airline, rank);
        tbody.appendChild(row);
    });

    document.getElementById('rankingsContainer').style.display = 'block';
}

// Modal Logic
const modal = document.getElementById('flightDetailsModal');
const closeBtn = document.getElementsByClassName('close')[0];

closeBtn.onclick = function () {
    modal.style.display = "none";
}

window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

async function showFlightDetails(airlineCode) {
    modal.style.display = "block";
    document.getElementById('modalLoading').style.display = 'block';
    document.getElementById('modalFlightTableContainer').style.display = 'none';
    document.getElementById('modalAirlineName').textContent = 'Loading...';

    try {
        const response = await fetch(`/api/airlines/${airlineCode}/flights?days=${filters.dateRange}&flight_type=${filters.flightType}`);
        if (!response.ok) throw new Error('Failed to fetch details');
        const data = await response.json();

        document.getElementById('modalAirlineName').textContent = data.airline.name;
        renderFlightTable(data.flights);

        document.getElementById('modalLoading').style.display = 'none';
        document.getElementById('modalFlightTableContainer').style.display = 'block';

    } catch (error) {
        document.getElementById('modalAirlineName').textContent = 'Error loading flights';
        document.getElementById('modalLoading').style.display = 'none';
        console.error(error);
    }
}

function renderFlightTable(flights) {
    const tbody = document.getElementById('modalFlightsBody');
    tbody.innerHTML = '';

    flights.forEach(flight => {
        const tr = document.createElement('tr');

        const statusClass = flight.onTime ? 'ontime' : 'delayed';
        const delayText = flight.delay > 0 ? `+${flight.delay.toFixed(0)}m` : 'Op tijd';

        // Parse flight number (e.g., "PC1254" -> "PC", "1254")
        const match = flight.flightNumber.match(/^([A-Z0-9]+)(\d+)$/);
        const carrier = match ? match[1] : flight.flightNumber.substring(0, 2);
        const number = match ? match[2] : flight.flightNumber.substring(2);

        // Parse date
        const [year, month, day] = flight.date.split('-');

        const trackerUrl = `https://www.flightstats.com/v2/flight-tracker/${carrier}/${number}?year=${year}&month=${month}&date=${day}`;

        tr.innerHTML = `
            <td><a href="${trackerUrl}" target="_blank" rel="noopener noreferrer" class="flight-link"><strong>${flight.flightNumber}</strong></a></td>
            <td>${flight.date}</td>
            <td>${(flight.schedTime && flight.schedTime.length >= 5) ? flight.schedTime.substring(0, 5) : (flight.schedTime || '-')}</td>
            <td>${flight.actualTime || '-'}</td>
            <td><span class="status-badge ${statusClass}">${delayText}</span></td>
            <td>${flight.destination || '-'}</td>
            <td>${flight.gate || '-'}</td>
            <td>${translateStatus(flight.status) || '-'}</td>
        `;
        tbody.appendChild(tr);
    });
}

function translateStatus(status) {
    if (!status) return '-';

    // Normalize status
    const upperStatus = status.toUpperCase();

    const translations = {
        'SCH': 'Gepland',
        'AIR': 'Onderweg',
        'EXP': 'Verwacht',
        'FIR': 'Onderweg',
        'LND': 'Geland',
        'FIB': 'Bagage band',
        'ARR': 'Aangekomen',
        'DIV': 'Uitgeweken',
        'CNX': 'Geannuleerd',
        'TOM': 'Morgen',
        'DEL': 'Vertraagd',
        'WIL': 'Wacht op land',
        'GTO': 'Gate open',
        'BRD': 'Boarding',
        'GCL': 'Gate dicht',
        'GTD': 'Gate gesloten',
        'DEP': 'Vertrokken'
    };

    return translations[upperStatus] || status;
}

// Create Airline Row
function createAirlineRow(airline, rank) {
    const tr = document.createElement('tr');
    tr.className = 'clickable-row';
    tr.onclick = () => showFlightDetails(airline.code);

    // Rank
    const rankClass = rank === 1 ? 'top-1' : rank === 2 ? 'top-2' : rank === 3 ? 'top-3' : 'other';

    // Score class
    const scoreClass = airline.onTimePercentage >= 90 ? 'excellent' :
        airline.onTimePercentage >= 80 ? 'good' :
            airline.onTimePercentage >= 70 ? 'average' : 'poor';

    // Trend
    const trend = airline.trend > 0 ? 'up' : airline.trend < 0 ? 'down' : 'stable';
    const trendIcon = airline.trend > 0 ? '↑' : airline.trend < 0 ? '↓' : '→';

    // Delay class
    const delayClass = airline.avgDelay <= 0 ? 'positive' : 'negative';

    tr.innerHTML = `
        <td style="text-align: center;">
            <div class="rank-badge ${rankClass}">${rank}</div>
        </td>
        <td>
            <div class="airline-info">
                <div class="airline-name">${airline.name}</div>
            </div>
        </td>
        <td style="text-align: center;">
            <span class="score-badge ${scoreClass}">${airline.reliabilityScore.toFixed(1)}</span>
        </td>
        <td style="text-align: center;">
            <span class="percentage">${airline.onTimePercentage.toFixed(1)}%</span>
        </td>
        <td style="text-align: center;">
            <span class="delay-value ${delayClass}">${airline.avgDelay > 0 ? '+' : ''}${airline.avgDelay.toFixed(0)} min</span>
        </td>
        <td style="text-align: center;">
            <span class="flights-count">${airline.totalFlights.toLocaleString()}</span>
        </td>
        <td style="text-align: center;">
            <span class="trend ${trend}">${trendIcon} ${Math.abs(airline.trend).toFixed(1)}%</span>
        </td>
    `;

    return tr;
}

// Display Statistics
function displayStats(airlines) {
    if (airlines.length === 0) return;

    // Best airline
    const best = airlines[0];
    document.getElementById('bestAirline').textContent = best.name;
    document.getElementById('bestAirlineScore').textContent = `Score: ${best.reliabilityScore.toFixed(1)}`;

    // Average on-time
    const avgOnTime = airlines.reduce((sum, a) => sum + a.onTimePercentage, 0) / airlines.length;
    document.getElementById('avgOnTime').textContent = `${avgOnTime.toFixed(1)}%`;

    // Average delay
    const avgDelay = airlines.reduce((sum, a) => sum + a.avgDelay, 0) / airlines.length;
    document.getElementById('avgDelay').textContent = `${avgDelay > 0 ? '+' : ''}${avgDelay.toFixed(0)} min`;

    // Total airlines
    document.getElementById('totalAirlines').textContent = airlines.length;

    // Total flights
    const totalFlights = airlines.reduce((sum, a) => sum + a.totalFlights, 0);
    document.getElementById('totalFlights').textContent = totalFlights.toLocaleString();

    document.getElementById('statsContainer').style.display = 'grid';
}

// UI State Management
function showLoading() {
    document.getElementById('loadingState').style.display = 'block';
    document.getElementById('errorState').style.display = 'none';
    document.getElementById('rankingsContainer').style.display = 'none';
    document.getElementById('statsContainer').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loadingState').style.display = 'none';
}

function showError(message) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('errorState').style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('nl-NL', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
    document.getElementById('lastUpdate').textContent = timeString;
}

// Mock Data Generator (for demonstration)
async function generateMockData() {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    const airlines = [
        { code: 'KL', name: 'KLM Royal Dutch Airlines', base: 92, variance: 5 },
        { code: 'BA', name: 'British Airways', base: 88, variance: 6 },
        { code: 'LH', name: 'Lufthansa', base: 90, variance: 4 },
        { code: 'AF', name: 'Air France', base: 85, variance: 7 },
        { code: 'DL', name: 'Delta Air Lines', base: 91, variance: 5 },
        { code: 'UA', name: 'United Airlines', base: 84, variance: 8 },
        { code: 'AA', name: 'American Airlines', base: 83, variance: 9 },
        { code: 'EK', name: 'Emirates', base: 94, variance: 3 },
        { code: 'QR', name: 'Qatar Airways', base: 93, variance: 4 },
        { code: 'SQ', name: 'Singapore Airlines', base: 95, variance: 2 },
        { code: 'TK', name: 'Turkish Airlines', base: 87, variance: 6 },
        { code: 'EY', name: 'Etihad Airways', base: 89, variance: 5 },
        { code: 'VS', name: 'Virgin Atlantic', base: 86, variance: 7 },
        { code: 'IB', name: 'Iberia', base: 82, variance: 8 },
        { code: 'AZ', name: 'ITA Airways', base: 81, variance: 9 },
        { code: 'TP', name: 'TAP Air Portugal', base: 80, variance: 10 },
        { code: 'SK', name: 'SAS Scandinavian', base: 88, variance: 6 },
        { code: 'AY', name: 'Finnair', base: 91, variance: 4 },
        { code: 'LX', name: 'Swiss International', base: 92, variance: 3 },
        { code: 'OS', name: 'Austrian Airlines', base: 89, variance: 5 },
        { code: 'SN', name: 'Brussels Airlines', base: 85, variance: 7 },
        { code: 'U2', name: 'easyJet', base: 78, variance: 12 },
        { code: 'FR', name: 'Ryanair', base: 76, variance: 14 },
        { code: 'VY', name: 'Vueling', base: 79, variance: 11 },
        { code: 'W6', name: 'Wizz Air', base: 75, variance: 15 }
    ];

    const generatedAirlines = airlines.map(airline => {
        const onTimePercentage = airline.base + (Math.random() - 0.5) * airline.variance;
        const avgDelay = (100 - onTimePercentage) * 2 - 10;
        const reliabilityScore = onTimePercentage - (avgDelay / 10);
        const totalFlights = Math.floor(Math.random() * 500) + 50;
        const trend = (Math.random() - 0.5) * 10;

        return {
            code: airline.code,
            name: airline.name,
            onTimePercentage: Math.max(0, Math.min(100, onTimePercentage)),
            avgDelay: avgDelay,
            reliabilityScore: reliabilityScore,
            totalFlights: totalFlights,
            trend: trend,
            flightType: Math.random() > 0.5 ? 'departures' : 'arrivals'
        };
    });

    return {
        airlines: generatedAirlines,
        lastUpdate: new Date().toISOString()
    };
}

// Export for use in other modules
window.AirlinesApp = {
    loadData,
    applyFilters,
    CONFIG
};

// Destination Drilldown Logic
async function loadDestinations() {
    try {
        const response = await fetch('/api/destinations');
        if (!response.ok) throw new Error('Failed to fetch destinations');
        destinationsData = await response.json();
        populateContinentSelect();
    } catch (error) {
        console.error('Error loading destinations:', error);
    }
}

function populateContinentSelect() {
    if (!destinationsData) return;

    // Get unique continents
    const continents = [...new Set(destinationsData.map(d => d.continent).filter(c => c))].sort();

    const select = document.getElementById('filterContinent');
    select.innerHTML = '<option value="">Continent...</option>';
    continents.forEach(c => {
        const option = document.createElement('option');
        option.value = c;
        option.textContent = c;
        select.appendChild(option);
    });

    select.disabled = false;
}

function updateCountrySelect(selectedContinent) {
    const countrySelect = document.getElementById('filterCountry');
    const airportSelect = document.getElementById('filterAirport');

    countrySelect.innerHTML = '<option value="">Land...</option>';
    airportSelect.innerHTML = '<option value="">Airport...</option>';
    airportSelect.disabled = true;
    filters.destination = null;

    if (!selectedContinent) {
        countrySelect.disabled = true;
        loadData(); // clear filter
        return;
    }

    // Filter countries by continent
    const countries = [...new Set(
        destinationsData
            .filter(d => d.continent === selectedContinent)
            .map(d => d.country)
            .filter(c => c)
    )].sort();

    countries.forEach(c => {
        const option = document.createElement('option');
        option.value = c;
        option.textContent = c;
        countrySelect.appendChild(option);
    });

    countrySelect.disabled = false;
}

function updateAirportSelect(selectedCountry) {
    const airportSelect = document.getElementById('filterAirport');
    airportSelect.innerHTML = '<option value="">Airport...</option>';
    filters.destination = null;

    if (!selectedCountry) {
        airportSelect.disabled = true;
        loadData();
        return;
    }

    // Filter airports by country
    const airports = destinationsData
        .filter(d => d.country === selectedCountry)
        .sort((a, b) => (a.name || "").localeCompare(b.name || ""));

    airports.forEach(a => {
        const option = document.createElement('option');
        option.value = a.code; // Use code for triggering filter
        option.textContent = `${a.name} (${a.code})`;
        airportSelect.appendChild(option);
    });

    airportSelect.disabled = false;
}

