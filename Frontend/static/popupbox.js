

// Get the modal and content elements
var modal = document.getElementById("myModal");
var modalContent = document.querySelector(".modal-body");
// Get the area elements
var areas = document.querySelectorAll('area');

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// Get the template
var template = document.getElementById('template');

// When the user clicks on an area, open the modal and set the content
areas.forEach(function(area) {
    area.addEventListener('click', function() {
        var dataKey = this.dataset.key;
        var contentPlaceholder = template.querySelector('.content-placeholder');
        // You can fetch content dynamically based on dataKey here
        // For demonstration purposes, I'll set static content
        modalContent.innerHTML = template.innerHTML; // Set the content based on the template
        modal.style.display = "block";
    });
});

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
} 
