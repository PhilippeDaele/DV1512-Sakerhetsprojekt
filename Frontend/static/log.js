document.addEventListener('DOMContentLoaded', function() {
    const logContentElement = document.getElementById('log-content');

    // Load and display the log file
    fetch('/log')
        .then(response => response.text())
        .then(data => {
            logContentElement.textContent = data;
        })
        .catch(error => {
            logContentElement.textContent = `Error loading log file: ${error}`;
        });
});