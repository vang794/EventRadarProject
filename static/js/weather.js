// weather.js
let useCelsius = false;

// Initialize unit toggle
document.addEventListener('DOMContentLoaded', () => {
    const unitToggle = document.getElementById('unitToggle');
    if (unitToggle) {
        unitToggle.addEventListener('change', handleUnitToggle);
    }
});

function handleUnitToggle() {
    useCelsius = this.checked;
    if (document.getElementById('forecastResults').innerHTML) {
        fetchWeather();
    }
}

// Overlay controls
function openWeatherOverlay() {
    document.getElementById('weatherOverlay').style.display = 'block';
}

function closeWeatherOverlay() {
    document.getElementById('weatherOverlay').style.display = 'none';
}

// API configuration
const apiKey = '438802557a5074e655e46b4140076665';

// Weather data functions
async function fetchWeather() {
    const locationType = document.querySelector('input[name="locationType"]:checked').value;
    const locationInput = document.getElementById('locationInputWeather').value.trim();
    const units = document.getElementById('unitToggle').checked ? 'metric' : 'imperial';
    const unitSymbol = units === 'metric' ? '°C' : '°F';

    if (!locationInput) {
        showError('Please enter a location.');
        return;
    }

    let apiUrl = `https://api.openweathermap.org/data/2.5/forecast?appid=${apiKey}&units=${units}`;

    try {
        if (locationType === 'city') {
            apiUrl += `&q=${locationInput}`;
        } else if (locationType === 'zip') {
            apiUrl += `&zip=${locationInput}`;
        } else if (locationType === 'coords') {
            const [lat, lon] = locationInput.split(',').map(coord => coord.trim());
            apiUrl += `&lat=${lat}&lon=${lon}`;
        }

        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error('Location not found or API error.');
        const data = await response.json();
        displayForecast(data, unitSymbol);
    } catch (error) {
        showError(error.message);
    }
}

function displayForecast(data, unitSymbol) {
    const forecastHTML = [];

    // Group forecasts by day
    const dailyForecasts = {};
    data.list.forEach(item => {
        const date = new Date(item.dt * 1000);
        const dateString = date.toLocaleDateString('en-US', {
            weekday: 'long',
            month: 'short',
            day: 'numeric'
        });

        if (!dailyForecasts[dateString]) {
            dailyForecasts[dateString] = [];
        }
        dailyForecasts[dateString].push(item);
    });

    // Get the next 3 days (excluding today if needed)
    const forecastDays = Object.keys(dailyForecasts).slice(0, 3);

    forecastDays.forEach(day => {
        const dayData = dailyForecasts[day];
        const temps = dayData.map(item => item.main.temp);
        const maxTemp = Math.max(...temps);
        const minTemp = Math.min(...temps);
        const weather = dayData[0].weather[0]; // Use first entry's weather as representative

        forecastHTML.push(`
            <div class="forecast-day">
                <h3>${day}</h3>
                <img src="http://openweathermap.org/img/wn/${weather.icon}@2x.png" alt="${weather.description}">
                <p><i class="fas fa-temperature-high"></i> High: ${maxTemp.toFixed(1)}${unitSymbol}</p>
                <p><i class="fas fa-temperature-low"></i> Low: ${minTemp.toFixed(1)}${unitSymbol}</p>
                <p><i class="fas fa-cloud"></i> ${weather.description}</p>
            </div>
        `);
    });

    document.getElementById('forecastResults').innerHTML = forecastHTML.join('');
}

function showError(message) {
    document.getElementById('forecastResults').innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-triangle"></i>
            ${message}
        </div>
    `;
}

// Event listener for form submission
document.getElementById('weatherForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    fetchWeather();
});