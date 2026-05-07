// Global chart instances
let tempChart = null;
let rainChart = null;
let aqiChart = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;
    
    if (path === '/' || path === '/index.html') {
        loadDashboard();
    } else if (path === '/analysis.html') {
        loadAnalysisPage();
    } else if (path === '/predict.html') {
        loadPredictionPage();
    }
});

// ================= DASHBOARD =================
async function loadDashboard() {
    showLoading();
    
    try {
        const summary = await (await fetch('/api/summary')).json();
        updateStats(summary);
        
        const seasonal = await (await fetch('/api/seasonal-trends')).json();
        createSeasonalChart(seasonal);
        
        const aqiData = await (await fetch('/api/aqi-distribution')).json();
        createAQIChart(aqiData);
        
        const topCities = await (await fetch('/api/top-cities?metric=Temperature_Avg (°C)&limit=5')).json();
        createTopCitiesChart(topCities);
        
    } catch (error) {
        console.error(error);
        showError('Failed to load dashboard data');
    }
    
    hideLoading();
}

function updateStats(summary) {
    document.getElementById('totalRecords').textContent = summary.total_records.toLocaleString();
    document.getElementById('avgTemp').textContent = `${summary.avg_temperature}°C`;
    document.getElementById('maxTemp').textContent = `${summary.max_temperature}°C`;
    document.getElementById('minTemp').textContent = `${summary.min_temperature}°C`;
    document.getElementById('avgHumidity').textContent = `${summary.avg_humidity}%`;
    document.getElementById('totalRainfall').textContent = `${summary.total_rainfall} mm`;
    document.getElementById('avgAQI').textContent = summary.avg_aqi;
    document.getElementById('citiesCount').textContent = summary.cities_count;
}

// ================= FIXED CHART =================
function createSeasonalChart(seasonal) {
    const ctx = document.getElementById('seasonalChart').getContext('2d');
    
    if (tempChart) tempChart.destroy();
    
    tempChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Object.keys(seasonal["Temperature_Avg (°C)"]),
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: Object.values(seasonal["Temperature_Avg (°C)"]),
                    borderColor: '#e53935',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Humidity (%)',
                    data: Object.values(seasonal["Humidity (%)"]),
                    borderColor: '#2196F3',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { title: { display: true, text: 'Temperature (°C)' }},
                y1: {
                    position: 'right',
                    title: { display: true, text: 'Humidity (%)' },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
}

// ================= FIXED FUNCTION NAME =================
function createTimeSeriesChart(data) {
    const dates = data.map(d => d.Date_str);
    const temps = data.map(d => d["Temperature_Avg (°C)"]);
    const humidity = data.map(d => d["Humidity (%)"]);
    const rainfall = data.map(d => d["Rainfall (mm)"]);

    const ctx = document.getElementById('timeSeriesChart').getContext('2d');

    if (window.timeSeriesChart) window.timeSeriesChart.destroy();

    window.timeSeriesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                { label: 'Temp', data: temps, borderColor: 'red' },
                { label: 'Humidity', data: humidity, borderColor: 'blue' },
                { label: 'Rainfall', data: rainfall, type: 'bar' }
            ]
        }
    });
}