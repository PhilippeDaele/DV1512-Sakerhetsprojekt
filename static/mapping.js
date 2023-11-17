let currentHighlightedMarker = null;
let currentContextMenu = null;

async function initMap() {
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    const { LatLng } = await google.maps.importLibrary("core");
    const center = new LatLng(56.18221384356372, 15.594398836523856);
    const map = new Map(document.getElementById("map"), {
        zoom: 17,
        center,
        mapId: "4504f8b37365c3d0",
    });

    map.addListener("click", () => {
        if (currentHighlightedMarker) {
            toggleHighlight(currentHighlightedMarker, currentHighlightedMarker.property);
            currentHighlightedMarker = null;
        }
    });
    
    localStorage.clear();
    
    
    if (userData == 'admin') {
        // Right-click event listener for the map
        map.addListener("rightclick", (event) => {
            if (event && event.hasOwnProperty("latLng")) {
            if (currentContextMenu) {
                // Close the previous context menu if it exists
                currentContextMenu.remove();
            }
        
            const customContextMenu = createContextMenu(event);
        
            
        
            // Set position based on clientX and clientY relative to the map container
            customContextMenu.style.left = (event.pixel.x + 275) + "px";
            customContextMenu.style.top = (event.pixel.y) + "px";
            customContextMenu.style.display = "block";

            // Store the current context menu reference
            currentContextMenu = customContextMenu;
        
            // Function to close the custom context menu when clicking elsewhere
            map.addListener("click", () => {
                if (currentContextMenu === customContextMenu) {
                currentContextMenu.remove();
                currentContextMenu = null; // Reset currentContextMenu reference
                }
            });
            }
        });
    }
    
      

    for (const property of properties) {
        const markerElement = new google.maps.marker.AdvancedMarkerElement({
            map,
            content: buildContent(property),
            position: property.position,
            title: property.description,
        });

        property.markerElement = markerElement;
        if (userData == 'admin')
        {
            attachLightSwitchEventListener(markerElement, property);
            attachRefreshButtonEventListener(markerElement, property);
        }
        
        attachClosedButtonEventListener(markerElement, property);
        
        

        markerElement.addListener("click", () => {
            
            
            if (currentHighlightedMarker && currentHighlightedMarker !== markerElement) {
                return;
            }
        
            if (currentHighlightedMarker && currentHighlightedMarker === markerElement) {
                return;
            } else {

                let url = `http://localhost:${property.port}/get_status`;
                fetch(url)
                .then(response => {
                    // Get response as text
                    return response.text();
                })
                .then(data => {
                    
                    let statusElement = markerElement.content.querySelector('.details h3:nth-child(6)').nextElementSibling;
                    if (statusElement.innerHTML !== "Status: " + JSON.parse(data).Status){
                        property.status = JSON.parse(data).Status;
                        const checkbox = markerElement.content.querySelector(`#cb${property.id}`);
                        statusElement.innerHTML = "Status: " + property.status;
                        let imageElement = markerElement.content.querySelector('.videofeed img');
                        if (property.status === 'Inactive') {
                            imageElement.src = '/static/cameraoffline.jpg'; // Change the source to the offline image
                        } else {
                            imageElement.src = '/static/video-evidence-900.jpg'; // Change the source back to the active image
                        }
                        if (checkbox) {
                            checkbox.checked = property.status === 'Active';
                        }
                    }
                })
                toggleHighlight(markerElement, property);
                currentHighlightedMarker = markerElement;
            }
        });
    }
}

function createContextMenu(event) {
    // Create a div element for the context menu
    const customContextMenu = document.createElement("div");
    customContextMenu.className = "popup";
    //customContextMenu.textContent = "Add Camera";
    /*
    customContextMenu.style.position = "absolute";
    customContextMenu.style.background = "#fff";
    customContextMenu.style.border = "1px solid #ccc";
    customContextMenu.style.padding = "10px";
    */
    // Create a ul element for the menu items
    const ul = document.createElement("ul");
    ul.style.padding = "0";
    ul.style.margin = "0";
  
    // Create a li element for the "Add Camera" option
    const li = document.createElement("li");
    li.textContent = "Add Camera";
    li.style.cursor = "pointer";
    li.style.padding = "8px 15px";
    li.addEventListener("click", () => addCamera(event.latLng.lat(), event.latLng.lng())); 
    // Pass lat and lng to addCamera function
  
    // Append the li to the ul, and ul to the customContextMenu
    ul.appendChild(li);
    customContextMenu.appendChild(ul);

    const mapContainer = document.getElementById("map");
    mapContainer.appendChild(customContextMenu);
  
    // Append the customContextMenu to the body
    document.body.appendChild(customContextMenu);
  
    return customContextMenu;
    
}


  
  
// Function to create and display a custom popup
function displayPopup(content) {
    // Create a div element for the popup container
    const popupContainer = document.createElement("div");
    popupContainer.className = "popup";
    
    // Create a div for the popup content
    const popupContent = document.createElement("div");
    popupContent.className = "popup-content";
    popupContent.textContent = content;
    
    // Append the content to the popup container
    popupContainer.appendChild(popupContent);
    
    // Append the popup container to the body
    document.body.appendChild(popupContainer);
    return popupContainer; // Return the reference to the created popup container
}

// Function to simulate adding a camera and displaying latitude and longitude
function addCamera(clickedLat, clickedLng) {
    // Placeholder action - Display a custom popup when "Add Camera" is clicked
    const content = `Latitude: ${clickedLat}, Longitude: ${clickedLng}`;
    const popup = displayPopup(content);
    popup.textContent = "Check the Add camera tab";
    popup.style.display = 'block';
    
    localStorage.setItem('latitude', clickedLat);
    localStorage.setItem('longitude', clickedLng);
    
    if (currentContextMenu) {
        currentContextMenu.remove();
        currentContextMenu = null; // Reset currentContextMenu reference
    }

    setTimeout(function() {
        document.body.removeChild(popup); // Remove the popup from the DOM after 3 seconds
    }, 2000); // Adjust the time as needed
}

function showPopup(message, property) {
    const propertyId = property.id;
    const popupId = 'customPopup' + propertyId;
    // Accessing the element with the dynamically generated ID
    const popupElement = document.getElementById(popupId);
    const popupText = document.getElementById('popupText'+ propertyId);
    popupText.textContent = message;
    popupElement.style.display = 'block';
  
    // Close the popup after 2 seconds
    setTimeout(() => {
      closePopup(property);
    }, 2000);
}

function closePopup(property) {
    const propertyId = property.id;
    const popupId = 'customPopup' + propertyId;
    // Accessing the element with the dynamically generated ID
    const popup = document.getElementById(popupId);
    popup.style.display = 'none';
}

function attachRefreshButtonEventListener(markerElement, property) {
    const refreshButton = markerElement.content.querySelector(".refresh-button");
    let lightSwitch = markerElement.content.querySelector(".tgl");
    let url = `http://localhost:${property.port}/reset-rate-limit`;
    
    if (refreshButton) {
        refreshButton.addEventListener("click", (event) => {
            fetch(url);
            lightSwitch.removeAttribute('disabled');
            property.rebooted = true;
            showPopup(property.description + " have been rebooted, you can now turn on the camera again!", property);
            event.stopPropagation(); // Prevent the click event from propagating to the map
        });
    }
}

function attachClosedButtonEventListener(markerElement, property) {
    const closeButton = markerElement.content.querySelector(".close-button");
    if (closeButton) {
        closeButton.addEventListener("click", (event) => {
            toggleHighlight(markerElement, property);
            currentHighlightedMarker = null;
            event.stopPropagation(); // Prevent the click event from propagating to the map
        });
    }
}

function toggleHighlight(markerView, property) {
    const highlightZIndex = 1; // Set a value higher than other markers
    if (markerView.content.classList.contains("highlight")) {
        markerView.content.classList.remove("highlight");
        markerView.zIndex = null;
    } else {
        markerView.content.classList.add("highlight");
        markerView.zIndex = highlightZIndex;
    }
}

function attachLightSwitchEventListener(markerElement, property) {
    const lightSwitch = markerElement.content.querySelector(".tgl");
    lightSwitch.addEventListener("click", async (event) => {
        event.stopPropagation(); // Prevent the click event from propagating to the card

        const newStatus = toggleStatus(property.status);
        const url = `http://localhost:${property.port}/set_status?new_status=${newStatus}`;

        try {
            const response = await fetch(url);
            if (response.ok && property.rebooted === true) {
                // HTTP status code is in the range 200-299
                const responseText = await response.text();
                // Handle the response or update UI as needed
                // Update property status
                property.status = newStatus;
                // Update status element
                let statusElement = markerElement.content.querySelector('.details h3:nth-child(6)').nextElementSibling;
                let imageElement = markerElement.content.querySelector('.videofeed img');
                if (statusElement) {
                    if (property.status === 'Inactive') {
                        imageElement.src = '/static/cameraoffline.jpg'; // Change the source to the offline image
                    } else {
                        imageElement.src = '/static/video-evidence-900.jpg'; // Change the source back to the active image
                    }
                    statusElement.innerHTML = "Status: " + newStatus;
                }

                // Update checkbox checked attribute
                const checkbox = markerElement.content.querySelector(`#cb${property.id}`);
                if (checkbox) {
                    checkbox.checked = property.status === 'Active';
                }
            } else {
                property.rebooted = false;
                property.status = 'Inactive';
                let statusElement = markerElement.content.querySelector('.details h3:nth-child(6)').nextElementSibling;
                let imageElement = markerElement.content.querySelector('.videofeed img');
                imageElement.src = '/static/cameraoffline.jpg'; // Change the source to the offline image
                statusElement.innerHTML = "Status: " + property.status;
                const checkbox = markerElement.content.querySelector(`#cb${property.id}`);
                if (checkbox) {
                    checkbox.checked = property.status === 'Active';
                }
                lightSwitch.setAttribute('disabled', 'true');
            }
        } catch (error) {
            console.error(`Error during fetch: ${error.message}`);
            // Handle the error (e.g., show an error message to the user)
        }
    });
}



function toggleStatus(status) {
    return status === 'Active' ? 'Inactive' : 'Active';
}


function buildContent(property) {
    const content = document.createElement("div");

    content.classList.add("property");
    if (userData == 'admin') {
        content.innerHTML = `
        <div class="icon">
                <i aria-hidden="true" class="fa fa-icon fa-${property.type}" title="${property.type}"></i>
                <span class="fa-sr-only">${property.type}</span>
        </div>
        <div class="details">
                <div class="text-container">
                    <div class="button-fade-in">
                    <div class="popup" id="customPopup${property.id}">
                        <div class="popup-content">
                            <p id="popupText${property.id}"></p>
                        </div>
                    </div>
                        <button class="close-button">X</button>
                        <button class="refresh-button"> 
                            <img src="/static/reboot.png" alt="Image Alt Text">
                        </button>
                        <h3>Name: ${property.description}</h3>
                        <h3>Port: ${property.port}</h3>
                        <h3>Status: ${property.status}</h3>
                        <input class="tgl tgl-flat" type="checkbox" id="cb${property.id}" ${property.status === 'Active' ? 'checked' : ''}>
                        <label class="tgl-btn${property.status === 'Inactive' ? ' red' : ''}" for="cb${property.id}"></label>
                    </div>
                </div>
                <div class="videofeed">
                    <img class="fade-in" src="${property.status === 'Active' ? '/static/video-evidence-900.jpg' : '/static/cameraoffline.jpg'}">
                </div>
        </div>
        `;
    }
    else {
        content.innerHTML = `
        <div class="icon">
                <i aria-hidden="true" class="fa fa-icon fa-${property.type}" title="${property.type}"></i>
                <span class="fa-sr-only">${property.type}</span>
        </div>
        <div class="details">
                <div class="text-container">
                    <div class="button-fade-in">
                        <button class="close-button">X</button>
                        <h3>Name: ${property.description}</h3>
                        <h3>IP Address: 192.168.0.1</h3>
                        <h3>Port: ${property.port}</h3>
                        <h3>Status: ${property.status}</h3>
                    </div>
                </div>
                <div class="videofeed">
                    <img class="fade-in" src="${property.status === 'Active' ? '/static/video-evidence-900.jpg' : '/static/cameraoffline.jpg'}">
                </div>
        </div>
        `;
    }
    

    return content;
}



const properties = [];

// Assuming camerasData is available
for (const [index, data] of camerasData.entries()) {
    const property = {
        description: data.cname,
        id: index + 1,
        type: "video-camera",
        position: {
            lat: data.lat,
            lng: data.lng,
        },
        status: data.status,
        port: data.port,
        rebooted: true
    };

    properties.push(property);
}


initMap();
