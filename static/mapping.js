let currentHighlightedMarker = null;

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
        }
        
        attachClosedButtonEventListener(markerElement, property);
        

        markerElement.addListener("click", () => {
            

            if (currentHighlightedMarker && currentHighlightedMarker !== markerElement) {
                return;
            }
        
            if (currentHighlightedMarker && currentHighlightedMarker === markerElement) {
                return;
            } else {
                toggleHighlight(markerElement, property);
                currentHighlightedMarker = markerElement;
            }
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

            if (response.ok) {
                // HTTP status code is in the range 200-299
                const responseText = await response.text();
                // Handle the response or update UI as needed
                console.log(responseText);

                // Update property status
                property.status = newStatus;

                // Update status element
                let statusElement = markerElement.content.querySelector('.details h3:nth-child(4)').nextElementSibling;
                if (statusElement) {
                    statusElement.innerHTML = "Status: " + newStatus;
                }

                // Update checkbox checked attribute
                const checkbox = markerElement.content.querySelector(`#cb${property.id}`);
                if (checkbox) {
                    checkbox.checked = property.status === 'Active';
                }
            } else {
                let statusElement = markerElement.content.querySelector('.details h3:nth-child(4)').nextElementSibling;
                if (statusElement) {
                    statusElement.innerHTML = "Status: Inactive";
                }

                // Update checkbox checked attribute
                const checkbox = markerElement.content.querySelector(`#cb${property.id}`);
                if (checkbox) {
                    checkbox.checked = property.status === 'Inactive';
                }
                // Handle non-successful response (status outside the range 200-299)
                console.log(`Failed to fetch data. Status: ${response.status}`);
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
                        <button class="close-button">X</button>
                        <h3>Name: ${property.description}</h3>
                        <h3>IP Address: 192.168.0.1</h3>
                        <h3>Port: ${property.port}</h3>
                        <h3>Status: ${property.status}</h3>
                        <input class="tgl tgl-flat" type="checkbox" id="cb${property.id}" ${property.status === 'Active' ? 'checked' : ''}>
                        <label class="tgl-btn${property.status === 'Inactive' ? ' red' : ''}" for="cb${property.id}"></label>
                    </div>
                </div>
                <div class="videofeed">
                    <img class="fade-in" src="/static/video-evidence-900.jpg">
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
                    <img class="fade-in" src="/static/video-evidence-900.jpg">
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
        port: data.port
    };

    properties.push(property);
}


initMap();
