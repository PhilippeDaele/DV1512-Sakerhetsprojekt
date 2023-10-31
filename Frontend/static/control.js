document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.tgl-flat');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const statusElement = checkbox.parentElement.previousElementSibling;
            const port = statusElement.id.split('-')[1];
            const newStatus = this.checked ? 'Active' : 'Inactive';
            const url = `http://localhost:${port}/set_status?new_status=${newStatus}`;
            fetch(url)
                .then(response => response.text())
            if (this.parentElement.parentElement.nextElementSibling.childNodes[0].textContent != "\n        ") {
                this.parentElement.parentElement.nextElementSibling.childNodes[0].textContent = newStatus;
            }
        });
    });
});
