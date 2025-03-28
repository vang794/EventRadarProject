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
    const locationInput = document.getElementById('locationInput').value.trim();
    const units = useCelsius ? 'metric' : 'imperial';

    if (!locationInput) {
        showError('Please enter a location.');
        return;
    }

    let apiUrl = `https://api.openweathermap.org/data/2.5/forecast?appid=${apiKey}&units=${units}`;

    try {
        if (locationType === 'city') {
            apiUrl += `&q=${locationInput}`;
        } else if (locationType === 'zip') {
            if (!/^\d{5}(-\d{4})?$/.test(locationInput)) {
                throw new Error('Invalid zip code format.');
            }
            apiUrl += `&zip=${locationInput}`;
        } else if (locationType === 'coords') {
            const [lat, lon] = locationInput.split(',').map(coord => coord.trim());
            if (isNaN(lat) || isNaN(lon)) {
                throw new Error('Invalid coordinates format.');
            }
            apiUrl += `&lat=${lat}&lon=${lon}`;
        }

        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error('Location not found or API error.');
        const data = await response.json();
        displayForecast(data);
    } catch (error) {
        showError(error.message);
    }
}

function displayForecast(data) {
    const now = new Date();
    const todayStartTimestamp = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime() / 1000;
    const tomorrowStartTimestamp = todayStartTimestamp + 86400;
    const unitSymbol = useCelsius ? '°C' : '°F';

    const forecastData = data.list.filter(item => item.dt >= tomorrowStartTimestamp);
    let forecastHTML = '';

    for (let i = 0; i < 3; i++) {
        const dayStartTimestamp = tomorrowStartTimestamp + (86400 * i);
        const dayEndTimestamp = dayStartTimestamp + 86400;
        const dayData = forecastData.filter(item => item.dt >= dayStartTimestamp && item.dt < dayEndTimestamp);

        if (dayData.length > 0) {
            const date = new Date(dayData[0].dt * 1000);
            const maxTemp = Math.max(...dayData.map(i => i.main.temp_max));
            const minTemp = Math.min(...dayData.map(i => i.main.temp_min));
            const weatherIcon = dayData[0].weather[0].icon;
            const weatherDesc = dayData[0].weather[0].description;

            forecastHTML += `
                <div class="forecast-day">
                    <h3>${date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}</h3>
                    <img src="http://openweathermap.org/img/wn/${weatherIcon}@2x.png" alt="${weatherDesc}">
                    <p><i class="fas fa-temperature-high"></i> High: ${maxTemp.toFixed(1)}${unitSymbol}</p>
                    <p><i class="fas fa-temperature-low"></i> Low: ${minTemp.toFixed(1)}${unitSymbol}</p>
                    <p><i class="fas fa-cloud"></i> ${weatherDesc}</p>
                </div>
            `;
        }
    }

    document.getElementById('forecastResults').innerHTML = forecastHTML;
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