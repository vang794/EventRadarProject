document.addEventListener('DOMContentLoaded', function() {
    initMap();
    initializePage();
    setupModalCloseListeners();
});

window.selectedMarker = null;

function getCategoryIcon(category) {
  const c = (category || '').toLowerCase();
  if (c.includes('activity park')) return 'fa-person-running';
  if (c.includes('aquarium')) return 'fa-fish';
  if (c.includes('arts centre')) return 'fa-palette';
  if (c.includes('artwork')) return 'fa-image';
  if (c.includes('fountain')) return 'fa-water';
  if (c.includes('gallery')) return 'fa-images';
  if (c.includes('historic building')) return 'fa-landmark';
  if (c.includes('memorial')) return 'fa-archway';
  if (c.includes('museum')) return 'fa-landmark-dome';
  if (c.includes('parking')) return 'fa-parking';
  if (c.includes('planetarium')) return 'fa-star';
  if (c.includes('theatre')) return 'fa-masks-theater';
  if (c.includes('theme park')) return 'fa-ticket-alt';
  if (c.includes('tourist building')) return 'fa-landmark-flag';
  if (c.includes('tower')) return 'fa-broadcast-tower';
  if (c.includes('viewpoint')) return 'fa-binoculars';
  return 'fa-map-marker-alt';
}

function makeDivIconForCategory(category) {
  const iconClass = getCategoryIcon(category);
  const html = `<i class="fas ${iconClass}" style="font-size:24px;color:#7a3bda;"></i>`;
  return L.divIcon({
    html: html,
    className: '',
    iconSize: [24, 24],
    iconAnchor: [12, 24]
  });
}

function makeEnlargedDivIconForCategory(category) {
  const iconClass = getCategoryIcon(category);
  const html = `<i class="fas ${iconClass}" style="font-size:32px;color:#7a3bda;"></i>`;
  return L.divIcon({
    html: html,
    className: '',
    iconSize: [32, 32],
    iconAnchor: [16, 32]
  });
}

function initMap() {
  const dataEl = document.getElementById('needsFetchData');
  const userLat = parseFloat(dataEl?.getAttribute('data-latitude')) || 43.0389;
  const userLng = parseFloat(dataEl?.getAttribute('data-longitude')) || -87.9065;
  const userRadius = parseFloat(dataEl?.getAttribute('data-radius')) || 5;

  window.map = L.map('map-container').setView([userLat, userLng], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
  }).addTo(window.map);

  if (!isNaN(userRadius)) {
    const radiusInMeters = userRadius * 1609.34;
    L.circle([userLat, userLng], {
      radius: radiusInMeters,
      color: '#3388ff',
      fillColor: '#3388ff',
      fillOpacity: 0.15
    }).addTo(window.map);
  }
  
  const markersCluster = L.markerClusterGroup();
  window.markersCluster = markersCluster;

  const eventCards = document.querySelectorAll('.event-card');
  eventCards.forEach((card) => {
    const lat = parseFloat(card.getAttribute('data-latitude'));
    const lng = parseFloat(card.getAttribute('data-longitude'));
    const titleText = card.getAttribute('data-title') || 'Event';
    const locText = card.getAttribute('data-location') || '';
    const descText = card.getAttribute('data-description') || '';
    const category = card.getAttribute('data-category') || 'Uncategorized';

    if (!isNaN(lat) && !isNaN(lng)) {
      const normalIcon = makeDivIconForCategory(category);
      const marker = L.marker([lat, lng], { icon: normalIcon });
      marker.normalIcon = normalIcon;
      marker.cardEl = card;

      const popupContent = `
        <strong>${titleText}</strong><br/>
        ${locText ? locText + '<br/>' : ''}
        ${descText}
      `;
      marker.bindPopup(popupContent);

      marker.on('click', function() {
        window.map.setView([lat, lng], 18);
        marker.openPopup();
        if (window.selectedMarker && window.selectedMarker !== marker) {
          if (window.selectedMarker.normalIcon) {
            window.selectedMarker.setIcon(window.selectedMarker.normalIcon);
          }
          if (window.selectedMarker.cardEl) {
            window.selectedMarker.cardEl.classList.remove('selected-event');
          }
        }
        window.selectedMarker = marker;
        marker.setIcon(makeEnlargedDivIconForCategory(category));
        if (marker.cardEl) {
          marker.cardEl.classList.add('selected-event');
        }
      });

      const headerEl = card.querySelector('.event-header');
      headerEl.addEventListener('click', () => {
        toggleEventDetails(card.getAttribute('data-event-id'));
        window.map.setView([lat, lng], 18);
        marker.openPopup();
        if (window.selectedMarker && window.selectedMarker !== marker) {
          if (window.selectedMarker.normalIcon) {
            window.selectedMarker.setIcon(window.selectedMarker.normalIcon);
          }
          if (window.selectedMarker.cardEl) {
            window.selectedMarker.cardEl.classList.remove('selected-event');
          }
        }
        window.selectedMarker = marker;
        marker.setIcon(makeEnlargedDivIconForCategory(category));
        card.classList.add('selected-event');
      });

      markersCluster.addLayer(marker);
    }
  });

  window.map.addLayer(markersCluster);
}

function initializePage() {
  const firstTab = document.querySelector('.category-tab');
  const firstCategory = document.querySelector('.category-content');
  if (firstTab && firstCategory) {
    firstTab.classList.add('active');
    firstCategory.style.display = 'block';
  }

  const needsFetchElement = document.getElementById('needsFetchData');
  if (!needsFetchElement) {
    hideLoadingOverlay();
    return;
  }

  const needsFetch = needsFetchElement.dataset.needsFetch === 'true';
  const latStr = needsFetchElement.dataset.latitude;
  const lonStr = needsFetchElement.dataset.longitude;
  const radiusStr = needsFetchElement.dataset.radius;
  const locationName = needsFetchElement.dataset.location;

  const currentLat = (latStr !== 'null') ? parseFloat(latStr) : null;
  const currentLon = (lonStr !== 'null') ? parseFloat(lonStr) : null;
  const currentRadius = (radiusStr !== 'null') ? parseFloat(radiusStr) : null;

  if (needsFetch && currentLat !== null && currentLon !== null && currentRadius !== null) {
    triggerEventFetch(currentLat, currentLon, currentRadius, locationName);
  } else {
    hideLoadingOverlay();
  }
}

async function triggerEventFetch(latitude, longitude, radius, locationName) {
  const loadingOverlay = document.getElementById('loadingOverlay');
  const loadingText = document.getElementById('loadingText');
  const locationInput = document.getElementById('locationInput');
  const radiusInput = document.getElementById('radiusInput');
  const searchButton = document.getElementById('searchButton');

  if (loadingOverlay) {
    if (loadingText) loadingText.textContent = 'Fetching events... Please hang tight!';
    loadingOverlay.style.display = 'flex';
  }
  if (locationInput) locationInput.disabled = true;
  if (radiusInput) radiusInput.disabled = true;
  if (searchButton) searchButton.disabled = true;

  const csrfToken = getCsrfToken();
  if (!csrfToken) {
    alert('Security token missing. Please refresh and try again.');
    if (loadingOverlay) loadingOverlay.style.display = 'none';
    if (locationInput) locationInput.disabled = false;
    if (radiusInput) radiusInput.disabled = false;
    if (searchButton) searchButton.disabled = false;
    return;
  }

  try {
    const response = await fetch("/api/fetch_events/", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        latitude: latitude,
        longitude: longitude,
        radius: radius,
        location_name: locationName
      })
    });
    const result = await response.json();

    if (response.ok && result.status === 'success') {
      if (loadingText) {
        loadingText.textContent = `Processed ${result.processed_count || 0} potential events. Reloading...`;
      }
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } else {
      if (loadingText) loadingText.textContent = 'Fetching events... Please hang tight!';
      if (loadingOverlay) loadingOverlay.style.display = 'none';
      if (locationInput) locationInput.disabled = false;
      if (radiusInput) radiusInput.disabled = false;
      if (searchButton) searchButton.disabled = false;
      alert('Failed to fetch events: ' + (result.message || 'Please try again.'));
    }
  } catch (error) {
    if (loadingText) loadingText.textContent = 'Fetching events... Please hang tight!';
    if (loadingOverlay) loadingOverlay.style.display = 'none';
    if (locationInput) locationInput.disabled = false;
    if (radiusInput) radiusInput.disabled = false;
    if (searchButton) searchButton.disabled = false;
    alert('An error occurred while trying to fetch events.');
  }

  if (loadingOverlay) loadingOverlay.style.display = 'none';
  if (locationInput) locationInput.disabled = false;
  if (radiusInput) radiusInput.disabled = false;
  if (searchButton) searchButton.disabled = false;
}

function setupModalCloseListeners() {}

function getCsrfToken() {
  const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
  return tokenInput ? tokenInput.value : '';
}

function hideLoadingOverlay() {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) overlay.style.display = 'none';
}

function toggleEventDetails(eventId) {
  const detailsElement = document.getElementById(`event-details-${eventId}`);
  if (!detailsElement) return;
  const isVisible = (detailsElement.style.display === 'block');
  detailsElement.style.display = isVisible ? 'none' : 'block';
}

function showCategory(slug) {
  const allContents = document.querySelectorAll('.category-content');
  allContents.forEach(content => {
    content.style.display = 'none';
  });
  const target = document.getElementById('category-' + slug);
  if (target) target.style.display = 'block';

  const allTabs = document.querySelectorAll('.category-tab');
  allTabs.forEach(t => t.classList.remove('active'));
  const clickedTab = document.querySelector('.category-tab-' + slug);
  if (clickedTab) clickedTab.classList.add('active');
}

window.toggleEventDetails = toggleEventDetails;
window.showCategory = showCategory;
