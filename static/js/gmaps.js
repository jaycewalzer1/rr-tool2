let map;
let markers = [];

window.initMap = function () {
    // Initialize the map centered on the United States
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 4,
        center: { lat: 37.0902, lng: -95.7129 }, // Center of USA
    });

    // Add event listener for form submission
    const form = document.getElementById('addressForm');
    form.addEventListener('submit', handleAddressSubmit);

    // Add autocomplete to the address input
    const input = document.getElementById('addressInput');
    const autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.bindTo('bounds', map);
};

function handleAddressSubmit(e) {
    e.preventDefault();
    const address = document.getElementById('addressInput').value;

    if (!address) {
        alert('Please enter an address');
        return;
    }

    showLoading(true);

    // Clear previous markers
    markers.forEach(marker => marker.setMap(null));
    markers = [];

    // Geocode the address
    geocodeAddress(address);
}

function geocodeAddress(address) {
    const geocoder = new google.maps.Geocoder();

    geocoder.geocode({ address: address }, (results, status) => {
        showLoading(false);

        if (status === 'OK') {
            if (results[0]) {
                const location = results[0].geometry.location;
                const formatted = results[0].formatted_address;

                // Center map on the location
                map.setCenter(location);
                map.setZoom(15);

                // Add marker
                const marker = new google.maps.Marker({
                    map,
                    position: location,
                    title: formatted,
                });
                markers.push(marker);

                // Add info window
                const infowindow = new google.maps.InfoWindow({
                    content: `<div><strong>${formatted}</strong></div>`,
                });

                marker.addListener('click', () => {
                    infowindow.open(map, marker);
                });
            } else {
                alert('No results found');
            }
        } else {
            alert('Geocoder failed due to: ' + status);
            console.error('Geocoding error:', status);
        }
    });
}

function showLoading(isLoading) {
    const loader = document.getElementById('mapLoader');
    if (loader) {
        loader.style.display = isLoading ? 'block' : 'none';
    }
}