let map;
let markers = [];
let points = [];

// Parsed rows are delivered as JSON rather than pre-rendered HTML so that
// spreadsheet content can never be executed as script in a marker popup.
function loadPoints() {
    const node = document.getElementById('map-points');
    if (!node) return [];
    try {
        return JSON.parse(node.textContent) || [];
    } catch (error) {
        console.error('Could not parse map data:', error);
        return [];
    }
}

function initializeMap() {
    points = loadPoints();
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: { lat: 35.9653, lng: -83.9233 }, // Charlotte, NC
        styles: [
            {
                "featureType": "administrative",
                "elementType": "all",
                "stylers": [
                    { "visibility": "simplified" },
                    { "color": "#ffffff" }
                ]
            },
            {
                "featureType": "administrative",
                "elementType": "geometry.fill",
                "stylers": [
                    { "color": "#ff0000" }
                ]
            },
            {
                "featureType": "administrative",
                "elementType": "labels.text.fill",
                "stylers": [
                    { "color": "#444444" }
                ]
            },
            {
                "featureType": "administrative.province",
                "elementType": "all",
                "stylers": [
                    { "visibility": "off" }
                ]
            },
            {
                "featureType": "landscape",
                "elementType": "all",
                "stylers": [
                    { "color": "#ffffff" }
                ]
            },
            {
                "featureType": "poi",
                "elementType": "all",
                "stylers": [
                    { "visibility": "off" }
                ]
            },
            {
                "featureType": "road",
                "elementType": "all",
                "stylers": [
                    { "saturation": -100 },
                    { "lightness": 45 }
                ]
            },
            {
                "featureType": "road.highway",
                "elementType": "all",
                "stylers": [
                    { "visibility": "simplified" }
                ]
            },
            {
                "featureType": "road.arterial",
                "elementType": "labels.icon",
                "stylers": [
                    { "visibility": "off" }
                ]
            },
            {
                "featureType": "transit",
                "elementType": "all",
                "stylers": [
                    { "visibility": "off" }
                ]
            },
            {
                "featureType": "water",
                "elementType": "all",
                "stylers": [
                    { "color": "#7f5281" },
                    { "visibility": "on" }
                ]
            }
        ]       
    });

    // Add zoom control handlers
    document.getElementById('zoom-in').addEventListener('click', () => {
        map.setZoom(map.getZoom() + 1);
    });

    document.getElementById('zoom-out').addEventListener('click', () => {
        map.setZoom(map.getZoom() - 1);
    });

    points.forEach((point, index) => geocodeAddress(point.address, index));
}

function handleAddressSubmit(e) {
    e.preventDefault();
    const address = document.querySelector('gmpx-place-autocomplete')?.value;

    if (!address) {
        alert('Please enter an address');
        return;
    }

    showLoading(true);
    clearMarkers();
    geocodeAddress(address);
}

function geocodeAddress(address, idx) {
    const geocoder = new google.maps.Geocoder();

    geocoder.geocode({ address }, (results, status) => {
        showLoading(false);

        if (status === 'OK' && results[0]) {
            const location = results[0].geometry.location;
            const formatted = results[0].formatted_address;
            //location.lat += Math.random() * (0.007 - (-0.007)) + (-0.007);
            //location.lng += Math.random() * (0.007 - (-0.007)) + (-0.007);
            const oldLoc = results[0].geometry.location;
            const newLat = oldLoc.lat() + Math.random() * 0.15 - 0.075;
            const newLng = oldLoc.lng() + Math.random() * 0.15 - 0.075;
            const newLoc = new google.maps.LatLng(newLat, newLng);

            map.setCenter(newLoc);
            map.setZoom(15);
            addMarker(newLoc, formatted, idx);
        } else {
            // One unresolvable address should not block the rest of the map.
            console.warn(`Could not geocode "${address}": ${status}`);
        }
    });
}

function getMarkerColor(rent) {
    const minRent = 0;
    const maxRent = 1000000;

    // Clamp rent to be within min/max for color scaling
    const clampedRent = Math.max(minRent, Math.min(rent, maxRent));

    // Normalize rent to a 0-1 scale
    let normalizedRent = (clampedRent - minRent) / (maxRent - minRent);

    // Apply an exponential curve (e.g., square root (lesser number here the greater logarithmic difference)) to make lower values more distinct
    normalizedRent = Math.pow(normalizedRent, 0.25);

    // Interpolate hue from green (120) to red (0)
    const hue = 120 * (1 - normalizedRent);

    return `hsl(${hue}, 90%, 45%)`; // Using HSL for a color gradient
}

// Builds the popup with DOM APIs; every value goes through textContent.
function buildPopup(point) {
    const card = document.createElement('div');
    card.className = 'map-popup';

    (point.fields || []).forEach(([label, value]) => {
        const row = document.createElement('div');
        row.className = 'map-popup__row';

        const key = document.createElement('strong');
        key.textContent = `${label}:`;

        const cell = document.createElement('span');
        cell.textContent = value;

        row.append(key, cell);
        card.append(row);
    });

    return card;
}

function addMarker(latLng, title, idx) {
    const point = points[idx] || {};
    // Neutral grey for properties with no rent data to colour-scale against.
    const markerColor = point.rent === null || point.rent === undefined
        ? '#9E9E9E'
        : getMarkerColor(point.rent);

    const marker = new google.maps.Marker({
        map,
        position: latLng,
        title,
        icon: {
            path: 'M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z',
            fillColor: markerColor,
            fillOpacity: 1,
            scale: 1.5,
            strokeColor: '#ffffff',
            strokeWeight: 1,
            anchor: new google.maps.Point(12, 24)
        }
    });
    markers.push(marker);

    const infowindow = new google.maps.InfoWindow({
        content: buildPopup(point),
    });

    marker.addListener('click', () => {
        infowindow.open(map, marker);
    });
}

function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
}

function showLoading(isLoading) {
    const loader = document.getElementById('mapLoader');
    if (loader) loader.style.display = isLoading ? 'block' : 'none';
}
