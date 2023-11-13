let currentHighlightedMarker = null;

async function initMap() {
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    const { LatLng } = await google.maps.importLibrary("core");
    const center = new LatLng(56.18149984961032, 15.591348772323101);
    const map = new Map(document.getElementById("map"), {
        zoom: 16,
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

        attachLightSwitchEventListener(markerElement, property);

        markerElement.addListener("click", () => {
            if (currentHighlightedMarker && currentHighlightedMarker !== markerElement) {
                return;
            }
        
            if (currentHighlightedMarker && currentHighlightedMarker === markerElement) {
                toggleHighlight(markerElement, property);
                currentHighlightedMarker = null;
            } else {
                toggleHighlight(markerElement, property);
                currentHighlightedMarker = markerElement;
            }
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
    lightSwitch.addEventListener("click", (event) => {
        event.stopPropagation(); // Prevent the click event from propagating to the card
        console.log("Light switch clicked!");
    });
}

function buildContent(property) {
    const content = document.createElement("div");

    content.classList.add("property");
    content.innerHTML = `
    <div class="icon">
            <i aria-hidden="true" class="fa fa-icon fa-${property.type}" title="${property.type}"></i>
            <span class="fa-sr-only">${property.type}</span>
    </div>
    <div class="details">
            <div class="text-container">
                <h3>Name: ${property.description}</h3>
                <h3>IP Address: 192.168.0.1</h3>
                <h3>Port: 5000</h3>
                <h3>Status: ${property.status}</h3>
                <div class="middle-button">
                <input class="tgl tgl-flat" type="checkbox" id="cb${property.id}" ${property.status === 'Active' ? 'checked' : ''}>
                <label class="tgl-btn${property.status === 'Inactive' ? ' red' : ''}" for="cb${property.id}"></label>
            </div>
            </div>
            <div class="videofeed">
                <img class="fade-in" src="/static/video-evidence-900.jpg">
            </div>
    </div>
    `;
/* 
<div class="icon">
            <i aria-hidden="true" class="fa fa-icon fa-${property.type}" title="${property.type}"></i>
            <span class="fa-sr-only">${property.type}</span>
    </div>
    <div class="details">
            <div class="test">
                <h1>${property.description}</h1>
                <h1>${property.status}</h1>
                <button class="my-button">Click Me</button>
            </div>
    </div>
*/


/*
<div class="icon">
            <i aria-hidden="true" class="fa fa-icon fa-${property.type}" title="${property.type}"></i>
            <span class="fa-sr-only">${property.type}</span>
    </div>
        <div class="details">
            <div class="text-container">
                <h3>Name: CAM_01</h3>
                <h3>IP Address: 192.168.0.1</h3>
                <h3>Port: 5000</h3>
                <h3>Status: Active</h3>
            </div>
            <div class="videofeed">
                <img src="/static/screenshot-28.jpg">
            </div>
        </div> */


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
        status: data.status
    };

    properties.push(property);
}

initMap();
