let map;
let markers = [];

function initializeMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: { lat: 35.2271, lng: -80.8431 }, // Charlotte, NC
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

    const form = document.getElementById('addressForm');
    form?.addEventListener('submit', handleAddressSubmit);

    const autocompleteEl = document.querySelector('gmpx-place-autocomplete');
    if (autocompleteEl) {
        autocompleteEl.addEventListener('gmpx-placechange', (event) => {
            const place = event.detail;
            if (place && place.location) {
                const latLng = {
                    lat: place.location.lat,
                    lng: place.location.lng,
                };

                addMarker(latLng, place.displayName || "Selected Location");
                map.setCenter(latLng);
                map.setZoom(15);
            }
        });
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

function geocodeAddress(address) {
    const geocoder = new google.maps.Geocoder();

    geocoder.geocode({ address }, (results, status) => {
        showLoading(false);

        if (status === 'OK' && results[0]) {
            const location = results[0].geometry.location;
            const formatted = results[0].formatted_address;

            map.setCenter(location);
            map.setZoom(15);
            addMarker(location, formatted);
        } else {
            alert('Geocoder failed: ' + status);
            console.error('Geocoding error:', status);
        }
    });
}

function addMarker(latLng, title) {
    const marker = new google.maps.Marker({
        map,
        position: latLng,
        title,
    });
    markers.push(marker);

    const infowindow = new google.maps.InfoWindow({
        content: `<div><strong>${title}</strong></div>`,
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