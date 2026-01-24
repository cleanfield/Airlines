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
        applyFilters();
    });

    document.getElementById('dateRange').addEventListener('change', (e) => {
        filters.dateRange = parseInt(e.target.value);
        loadData();
    });

    document.getElementById('minFlights').addEventListener('change', (e) => {
        filters.minFlights = parseInt(e.target.value);
        applyFilters();
    });

    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadData();
    });
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
            // Fetch from API
            const response = await fetch(`${CONFIG.apiEndpoint}?days=${filters.dateRange}`);
            if (!response.ok) throw new Error('Failed to fetch data');
            data = await response.json();
        }

        currentData = data;
        applyFilters();
        hideLoading();

    } catch (error) {
        showError(error.message);
    }
}

// Apply Filters
function applyFilters() {
    if (!currentData) return;

    let filtered = [...currentData.airlines];

    // Filter by flight type
    if (filters.flightType !== 'all') {
        filtered = filtered.filter(airline =>
            airline.flightType === filters.flightType
        );
    }

    // Filter by minimum flights
    filtered = filtered.filter(airline =>
        airline.totalFlights >= filters.minFlights
    );

    // Sort by reliability score
    filtered.sort((a, b) => b.reliabilityScore - a.reliabilityScore);

    displayRankings(filtered);
    displayStats(filtered);
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

// Create Airline Row
function createAirlineRow(airline, rank) {
    const tr = document.createElement('tr');

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
                <div class="airline-code">${airline.code}</div>
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
        minute: '2-digit'
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
