document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.tgl-flat');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const statusElement = checkbox.parentElement.previousElementSibling;
            const port = statusElement.id.split('-')[1];
            const newStatus = this.checked ? 'Active' : 'Inactive';
            // This is used to change the status for the camera on provided port
            // For example to turn of Camera on port 5005 the url will look like this:
            // http://localhost:5005/set_status?new_status=Inactive`
            const url = `http://localhost:${port}/set_status?new_status=${newStatus}`;
            fetch(url)
                .then(response => response.text())
            if (this.parentElement.parentElement.nextElementSibling.childNodes[0].textContent != "\n        ") {
                this.parentElement.parentElement.nextElementSibling.childNodes[0].textContent = newStatus;
            }
        });
    });
});
