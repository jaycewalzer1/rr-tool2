let map;
let markers = [];
const addressList = document.getElementById('address-list');
const addresses = Array.from(addressList.querySelectorAll('li')).map(li => li.textContent);
const popupList = document.getElementById('popup-list');
const popups = Array.from(popupList.querySelectorAll('li')).map(li => li.textContent);
const rentList = document.getElementById('rent-list');
const rents = Array.from(rentList.querySelectorAll('li')).map(li => li.textContent);

function initializeMap() {
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

    for (var i = 0; i < addresses.length; i++){
        if (addresses[i] && addresses[i] !== 'NaN') {
            console.log(addresses[i]);
            geocodeAddress(addresses[i], i);
        }
    }
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
            alert('Geocoder failed: ' + status);
            console.error('Geocoding error:', status);
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

function addMarker(latLng, title, idx) {
    const rentString = rents[idx];
    let markerColor = '#9E9E9E'; // A neutral grey for properties without rent data

    if (rentString) {
        // Sanitize and parse the rent value
        const rent = parseFloat(rentString.replace(/[^0-9.-]+/g, ""));
        if (!isNaN(rent)) {
            markerColor = getMarkerColor(rent);
        }
    }

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
        content: popups[idx],
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
