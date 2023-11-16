const latitude = localStorage.getItem('latitude');
const longitude = localStorage.getItem('longitude');

document.querySelector('input[name="latitude"]').value = latitude;
document.querySelector('input[name="longitude"]').value = longitude;
