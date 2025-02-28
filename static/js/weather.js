const apiKey = '438802557a5074e655e46b4140076665'; // Move this to Django backend for security

async function fetchWeather() {
    const locationType = document.querySelector('input[name="locationType"]:checked').value;
    const locationInput = document.getElementById('locationInput').value.trim();

    if (!locationInput) {
        showError('Please enter a location.');
        return;
    }

    let apiUrl = `https://api.openweathermap.org/data/2.5/forecast?appid=${apiKey}&units=metric`;

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

    const forecastData = data.list.filter(item => item.dt >= tomorrowStartTimestamp);
    let forecastHTML = '';

    for (let i = 0; i < 3; i++) {
        const dayStartTimestamp = tomorrowStartTimestamp + (86400 * i);
        const dayEndTimestamp = dayStartTimestamp + 86400;

        const dayData = forecastData.filter(item => item.dt >= dayStartTimestamp && item.dt < dayEndTimestamp);

        if (dayData.length > 0) {
            const date = new Date(dayData[0].dt * 1000);
            const maxTemp = Math.max(...dayData.map(i => i.main.temp));
            const avgClouds = dayData.reduce((acc, i) => acc + i.clouds.all, 0) / dayData.length;
            const maxPressure = Math.max(...dayData.map(i => i.main.pressure));
            const weatherIcon = dayData[0].weather[0].icon; // Get weather icon code

            forecastHTML += `
                <div class="forecast-day">
                    <h3>${date.toDateString()}</h3>
                    <img src="http://openweathermap.org/img/wn/${weatherIcon}@2x.png" alt="${dayData[0].weather[0].description}">
                    <p>Max Temp: ${maxTemp.toFixed(2)}°C</p>
                    <p>Avg Cloud Cover: ${avgClouds.toFixed(2)}%</p>
                    <p>Max Pressure: ${maxPressure} hPa</p>
                </div>
            `;
        }
    }

    document.getElementById('forecastResults').innerHTML = forecastHTML;
}

function showError(message) {
    document.getElementById('forecastResults').innerHTML = `<p style="color: red;">Error: ${message}</p>`;
}