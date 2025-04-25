document.addEventListener('DOMContentLoaded', function() {
  initMap();
  initializePage();
  setupModalCloseListeners();
  
  const style = document.createElement('style');
  style.textContent =
    `.category-tab {
      background-color: #f0e6ff;
      color: #7a3bda;
      border: none;
      border-radius: 8px;
      padding: 4px 8px;
      margin: 2px;
      font-weight: 500;
      font-size: 0.92em;
      transition: all 0.2s ease;
      min-width: 0;
    }

    .category-tab:hover {
      background-color: #e6d9ff;
      box-shadow: 0 2px 4px rgba(122, 59, 218, 0.2);
    }

    .category-tab.active {
      background-color: #7a3bda;
      color: white;
      box-shadow: 0 2px 6px rgba(122, 59, 218, 0.4);
    }

    .fa-map-marker-alt, .fas {
      color: #7a3bda;
    }
    .category-tabs {
      flex-wrap: wrap;
      gap: 0;
    }`;
  document.head.appendChild(style);
});

function slugify(text) {
return text.toString().toLowerCase().trim()
  .replace(/\s+/g, '-')           
  .replace(/[^\w\-]+/g, '')       
  .replace(/\-\-+/g, '-');       
}

window.selectedMarker = null;
let parkingMarkers = [];
let nonParkingMarkers = [];

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
return L.divIcon({ html, className: '', iconSize: [24, 24], iconAnchor: [12, 24] });
}

function makeEnlargedDivIconForCategory(category) {
const iconClass = getCategoryIcon(category);
const html = `<i class="fas ${iconClass}" style="font-size:32px;color:#7a3bda;"></i>`;
return L.divIcon({ html, className: '', iconSize: [32, 32], iconAnchor: [16, 32] });
}

function initMap() {
const dataEl = document.getElementById('needsFetchData');
const userLat = parseFloat(dataEl?.getAttribute('data-latitude')) || 43.0389;
const userLng = parseFloat(dataEl?.getAttribute('data-longitude')) || -87.9065;
const userRadius = parseFloat(dataEl?.getAttribute('data-radius')) || 5;

window.map = L.map('map-container').setView([userLat, userLng], 15);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '© OpenStreetMap'
}).addTo(window.map);

if (!isNaN(userRadius)) {
  L.circle([userLat, userLng], {
    radius: userRadius * 1609.34,
    color: '#3388ff', fillColor: '#3388ff', fillOpacity: 0.15
  }).addTo(window.map);
}

const markersCluster = L.markerClusterGroup();
window.markersCluster = markersCluster;
parkingMarkers = [];
nonParkingMarkers = [];

document.querySelectorAll('.event-card').forEach(card => {
  const lat = parseFloat(card.getAttribute('data-latitude'));
  const lng = parseFloat(card.getAttribute('data-longitude'));
  const category = card.getAttribute('data-category') || 'Uncategorized';
  if (isNaN(lat) || isNaN(lng)) return;

  const normalIcon = makeDivIconForCategory(category);
  const marker = L.marker([lat, lng], { icon: normalIcon });
  marker.normalIcon = normalIcon;
  marker.cardEl = card;

  const popupContent =
    `<strong>${card.getAttribute('data-title')}</strong><br/>` +
    (card.getAttribute('data-location') ? card.getAttribute('data-location') + '<br/>' : '') +
    card.getAttribute('data-description');
  marker.bindPopup(popupContent);

  marker.on('click', () => {
    const eventId = card.getAttribute('data-event-id');
    if (eventId.startsWith('user-')) {
      showSidebarTab('user-events');
      toggleEventDetails(eventId);
    } else {
      const slug = slugify(category);
      showSidebarTab('pois');
      showCategory(slug);
      toggleEventDetails(eventId);
    }
    const detailsEl = document.getElementById(`event-details-${eventId}`);
    if (detailsEl) detailsEl.scrollIntoView({ behavior: 'smooth', block: 'center' });

    window.map.setView([lat, lng], 18);
    marker.openPopup();
    if (window.selectedMarker && window.selectedMarker !== marker) {
      window.selectedMarker.setIcon(window.selectedMarker.normalIcon);
    }
    window.selectedMarker = marker;
    marker.setIcon(makeEnlargedDivIconForCategory(category));
  });

  const headerEl = card.querySelector('.event-header');
  if (headerEl) {
    headerEl.addEventListener('click', () => {
      const eventId = card.getAttribute('data-event-id');
      toggleEventDetails(eventId);
      window.map.setView([lat, lng], 18);
      marker.openPopup();
      if (window.selectedMarker && window.selectedMarker !== marker) {
        window.selectedMarker.setIcon(window.selectedMarker.normalIcon);
      }
      window.selectedMarker = marker;
      marker.setIcon(makeEnlargedDivIconForCategory(category));
    });
  }

  if (category.toLowerCase() === 'parking') {
    parkingMarkers.push(marker);
  } else {
    nonParkingMarkers.push(marker);
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
  const loadingOverlay = document.getElementById('loadingOverlay');
  if (loadingOverlay) {
    loadingOverlay.style.display = 'flex';
    loadingOverlay.style.position = 'fixed';
    loadingOverlay.style.top = '0';
    loadingOverlay.style.left = '0';
    loadingOverlay.style.width = '100%';
    loadingOverlay.style.height = '100%';
    loadingOverlay.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
    loadingOverlay.style.zIndex = '1000';
  }
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
  loadingOverlay.style.display = 'flex';
  if (loadingText) loadingText.textContent = 'Fetching POIs... Please hang tight!';
}
if (locationInput) locationInput.disabled = true;
if (radiusInput) radiusInput.disabled = true;
if (searchButton) searchButton.disabled = true;

const csrfToken = getCsrfToken();
if (!csrfToken) {
  alert('Security token missing. Please refresh and try again.');
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
    body: JSON.stringify({ latitude, longitude, radius, location_name: String(locationName || '') })
  });
  const result = await response.json();

  if (response.ok && result.status === 'success') {
    if (loadingText) loadingText.textContent = `Processed ${result.processed_count || 0} points of interest. Reloading...`;
    setTimeout(() => window.location.reload(), 1500);
  } else {
    alert('Failed to fetch events: ' + (result.message || 'Please try again.'));
    if (locationInput) locationInput.disabled = false;
    if (radiusInput) radiusInput.disabled = false;
    if (searchButton) searchButton.disabled = false;
    if (loadingOverlay) loadingOverlay.style.display = 'none';
  }
} catch (error) {
  console.error("Error fetching events:", error);
  alert('An error occurred while trying to fetch events.');
  if (locationInput) locationInput.disabled = false;
  if (radiusInput) radiusInput.disabled = false;
  if (searchButton) searchButton.disabled = false;
  if (loadingOverlay) loadingOverlay.style.display = 'none';
}
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
document.querySelectorAll('.event-details').forEach(el => el.style.display = 'none');
document.querySelectorAll('.event-card').forEach(el => el.classList.remove('selected-event'));

const detailsElement = document.getElementById(`event-details-${eventId}`);
const card = document.querySelector(`[data-event-id="${eventId}"]`);
if (!detailsElement || !card) return;
detailsElement.style.display = 'block';
card.classList.add('selected-event');
}

function showCategory(slug) {
document.querySelectorAll('.category-content').forEach(content => content.style.display = 'none');
const target = document.getElementById('category-' + slug);
if (target) target.style.display = 'block';
document.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
const clickedTab = document.querySelector('.category-tab-' + slug);
if (clickedTab) clickedTab.classList.add('active');
parkingMarkers.forEach(marker => { if (slug === 'parking') { window.markersCluster.addLayer(marker); } else { window.markersCluster.removeLayer(marker); } });
}

function showSidebarTab(tab) {
document.querySelectorAll('.sidebar-tab').forEach(btn => btn.classList.remove('active'));
document.querySelectorAll('.sidebar-tab-content').forEach(div => div.style.display = 'none');
if (tab === 'user-events') {
  document.querySelectorAll('.sidebar-tab')[0].classList.add('active');
  document.getElementById('sidebar-user-events').style.display = 'block';
} else {
  document.querySelectorAll('.sidebar-tab')[1].classList.add('active');
  document.getElementById('sidebar-pois').style.display = 'block';
}
}

function showAddToPlanModal(itemType, itemId) {
let modal = document.getElementById('addToPlanModal');
if (!modal) { modal = document.createElement('div'); modal.id = 'addToPlanModal'; modal.style.display = 'none'; document.body.appendChild(modal); }
fetch('/api/get_user_plans/')
  .then(res => res.json())
  .then(data => {
    if (!data.plans || data.plans.length === 0) { alert('You must create a plan before adding items.'); window.location.href = '/event_plan/'; return; }
    modal.innerHTML = `<div style="background:#fff;max-width:400px;margin:10vh auto;padding:24px;border-radius:8px;position:relative;box-shadow:0 2px 12px rgba(0,0,0,0.15)">` +
      `<h3 style="margin-top:0;">Select a Plan</h3>` +
      `<select id="planSelect" style="width:100%;padding:8px 6px;border-radius:6px;border:1px solid #ccc;">` +
      data.plans.map(plan => `<option value="${plan.id}">${plan.name} (${plan.start_date} - ${plan.end_date})</option>`).join('') +
      `</select>` +
      `<div style="margin-top:16px;text-align:right;">` +
      `<button id="confirmAddToPlan" class="btn btn-primary">Add</button>` +
      `<button id="cancelAddToPlan" class="btn btn-outline" style="margin-left:8px;">Cancel</button>` +
      `</div></div>`;
    modal.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.4);z-index:9999;';
    modal.style.display = 'block';
    modal.querySelector('#cancelAddToPlan').onclick = () => modal.style.display = 'none';
    modal.querySelector('#confirmAddToPlan').onclick = () => {
      const planId = modal.querySelector('#planSelect').value;
      addToPlan(planId, itemType, itemId, modal);
    };
    modal.onclick = e => { if (e.target === modal) modal.style.display = 'none'; };
  });
}

function addToPlan(planId, itemType, itemId, modal) {
const csrfToken = getCsrfToken();
fetch('/api/add_to_plan/', {
  method: 'POST',
  headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'application/x-www-form-urlencoded' },
  body: `plan_id=${encodeURIComponent(planId)}&item_type=${encodeURIComponent(itemType)}&item_id=${encodeURIComponent(itemId)}`
})
.then(res => res.json())
.then(data => {
  if (data.success) { alert('Added to plan!'); modal.style.display = 'none'; }
  else { alert('Failed to add to plan: ' + (data.error || 'Unknown error')); }
});
}
