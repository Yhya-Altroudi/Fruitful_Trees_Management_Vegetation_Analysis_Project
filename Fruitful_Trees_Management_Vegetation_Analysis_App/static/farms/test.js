// const map = L.map('map').setView([34.988515, 37.980672], 6);

// const tiles = L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
//     maxZoom: 20,
//     subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
// }).addTo(map);

//   const marker = L.marker([51.5, -0.09]).addTo(map)
//   	.bindPopup('<b>Hello world!</b><br />I am a popup.').openPopup();

// const circle = L.circle([51.508, -0.11], {
// 	color: 'red',
// 	fillColor: '#f03',
// 	fillOpacity: 0.5,
// 	radius: 500
// }).addTo(map).bindPopup('I am a circle.');

// const polygon = L.polygon([
// 	[51.509, -0.08],
// 	[51.503, -0.06],
// 	[51.51, -0.047]
// ]).addTo(map).bindPopup('I am a polygon.');

// const popup = L.popup()
// 	.setLatLng([51.513, -0.09])
// 	.setContent('I am a standalone popup.')
// 	.openOn(map);

// function onMapClick(e) {
// 	popup
// 		.setLatLng(e.latlng)
// 		.setContent(`You clicked the map at ${e.latlng.toString()}`)
// 		.openOn(map);
// }

// map.on('click', onMapClick);

// GeoJson
// var geojsonFeature = {
// 	"type": "Feature",
// 	"properties": {
// 		"name": "Coors Field",
// 		"amenity": "Baseball Stadium",
// 		"popupContent": "This is where the Rockies play!"
// 	},
// 	"geometry": {
// 		"type": "Point",
// 		"coordinates": [51.505, -0.09]
// 	}
// };

// L.geoJSON(geojsonFeature)
// 	.addTo(map)
// 	// .bindPopup('I am a point.')
// 	.openPopup()
// 	;
// L.drawLocal.draw.toolbar.buttons.polygon = "Create a customized geofence";
