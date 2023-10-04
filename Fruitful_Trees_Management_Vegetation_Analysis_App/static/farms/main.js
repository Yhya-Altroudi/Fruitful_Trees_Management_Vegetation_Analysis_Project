window.addEventListener("map:init", map_init, false);

// #region map section
var map,
  info = L.control({ position: "bottomleft" }),
  drawnItems = new L.FeatureGroup();
function map_init(e) {
  map = e.detail.map;
  // var options = e.detail.options;

  // FeatureGroup is to store editable layers
  // var drawnItems = new L.FeatureGroup();
  map.addLayer(drawnItems);

  info.onAdd = function (map) {
    this._div = L.DomUtil.create("div", "info"); // create a div with a class "info"
    this.update();
    return this._div;
  };

  // method that we will use to update the control based on feature properties passed
  info.update = function (props) {
    this._div.innerHTML = infoOnMap(props);
  };

  info.addTo(map);

  if (!is_authenticated) return;

  // map.addLayer(drawnFarms);
  // map.addLayer(drawnTrees);
  map.addLayer(newTrees);

  //configure draw control
  var drawControl = new L.Control.Draw({
    position: "topright",
    draw: {
      polyline: false,
      polygon: {
        allowIntersection: false, // Restricts shapes to simple polygons
        drawError: {
          color: "#e1e100", // Color the shape will turn when intersects
          message: "<strong>Oh snap!<strong> you can't draw that!", // Message that will show when intersect
        },
        shapeOptions: {
          color: "#bada55",
        },
        // showArea: true,
        zIndexOffset: 1,
      },
      marker: false,
      circle: {
        repeatMode: true,
        zIndexOffset: 2000,
      },
      rectangle: false,
      circlemarker: false,
      toolbar: {
        buttons: {
          polygon: "draw a farm",
        },
      },
    },
    edit: {
      featureGroup: drawnItems, //REQUIRED!!
      edit: true,
      remove: true,
    },
  });
  map.addControl(drawControl);

  // Map Events
  // draw farm/tree trigger
  map.on(L.Draw.Event.CREATED, async function (e) {
    var type = e.layerType,
      layer = e.layer;

    if (type == "polygon") {
      //
      if (newFarm != null) drawnItems.removeLayer(newFarm);
      // drawing farm state --> view farm and enter its info
      newFarm = layer;
      drawnItems.addLayer(newFarm);

      // enter farm information to create a new one
      window.document.getElementById("farm_create_ui").hidden = false;
      window.document.getElementById("detect_trees_ui").hidden = false;
    } else if (type == "circle") {
      // start state --> alert action
      if (validateTrees(newFarm, layer))
        // drawing tree state --> view tree
        newTrees.addLayer(layer);
    }
    console.log(drawnItems);
  });
  // edit
  map.on("draw:edited", (e) => {
    let polygonLayer;
    e.layers.eachLayer((layer) => {
      if (layer instanceof L.Polygon) {
        if (L.stamp(layer) == L.stamp(newFarm)) console.log("why to do that?!");
        polygonLayer = layer;
      } else if (layer instanceof L.Circle) {
        if (!validateTrees(newFarm, layer)) newTrees.removeLayer(layer);
      }
    });
    newTrees.eachLayer((layer) => {
      if (!validateTrees(newFarm, layer)) newTrees.removeLayer(layer);
    });
  });
  // delete
  map.on("draw:deleted", (e) => {
    e.layers.eachLayer((layer) => {
      if (layer instanceof L.Polygon) {
        // delete all trees
        newTrees.clearLayers();
        window.document.getElementById("farm_create_ui").hidden = true;
        window.document.getElementById("detect_trees_ui").hidden = true;
      } else if (layer instanceof L.Circle) {
        newTrees.removeLayer(layer);
      }
    });
  });
}
// map section
// viewed farms and trees layers on map as geojson layers received from server
var drawnFarms = null,
  drawnTrees = null;
// mapping from farm id to leaflet geojson layer id
var farms_mapping = {};
// new added trees to map
const newTrees = L.featureGroup.subGroup(drawnItems);
// new added farm to map
var newFarm = null;

function addFarmsToMap(geoJSONFarms) {
  if (geoJSONFarms.features.length === 0) {
    alert("there are no farms");
    return;
  }
  if (drawnFarms) console.warn("the map is not clean to add new farms");
  // for (const [_, value] of Object.entries(L.geoJSON(geoJSONFarms)._layers))
  //   drawnFarms.addLayer(value);
  drawnFarms = L.geoJSON(geoJSONFarms, {
    style: drawnFarmsStyle,
    onEachFeature: onEachFarmFeature,
  }).addTo(map);

  // update farms mapping
  farms_mapping = Object.fromEntries(
    drawnFarms.getLayers().map((layer) => [layer.feature.id, L.stamp(layer)])
  );
}
function addTreesToMap(geoJSONTrees) {
  if (geoJSONTrees.features.length === 0) {
    alert("there are no trees");
    return;
  }
  if (drawnTrees) console.warn("the map is not clean to add new trees");
  drawnTrees = L.geoJSON(geoJSONTrees, {
    pointToLayer: (feature, latlng) =>
      new L.Circle(latlng, feature.properties.radius),
  }).addTo(map);
}
function setMapViewByFarms(farmsId = Object.keys(farms_mapping)) {
  var farmsLayers;
  if (farmsId.length == 0) return;
  // set view for all farms
  if (farmsId.length == Object.keys(farms_mapping).length) {
    farmsLayers = drawnFarms;
  } else if (farmsId.length == 1) {
    // set view for a specific farm
    farmsLayers = drawnFarms.getLayer(farms_mapping[farmsId[0]]);
  } else {
    // set view for subset of farms
    const farmsLeafletId = new Set(farmsId.map((id) => farms_mapping[id]));
    farmsLayers = new L.FeatureGroup(
      drawnFarms
        .getLayers()
        .filter((layer) => farmsLeafletId.has(L.stamp(layer)))
    );
  }
  // fit the farms
  const farmsLayersBounds = farmsLayers.getBounds();
  map.panTo(farmsLayersBounds.getCenter());
  map.fitBounds(farmsLayersBounds);
}
function getFarmsProperties(farmsId = Object.keys(farms_mapping)) {
  // properties for all farms
  if (farmsId.length == Object.keys(farms_mapping).length)
    return drawnFarms.getLayers().map((layer) => layer.feature.properties);

  // properties for farms filtered by farmsId parameter
  const farmsLeafletId = new Set(farmsId.map((id) => farms_mapping[id]));
  return drawnFarms
    .getLayers()
    .filter((layer) => farmsLeafletId.has(L.stamp(layer)))
    .map((layer) => layer.feature.properties);
}
function getNewFarmGeometry() {
  return newFarm.toGeoJSON().geometry;
}
function getNewTreesJSON(farmId) {
  return newTrees.getLayers().map((layer) => ({
    center: layer.toGeoJSON().geometry,
    radius: layer.getRadius(),
    farm: farmId,
  }));
}
function clearTreesFromMap() {
  if (drawnTrees != null) map.removeLayer(drawnTrees);
  drawnTrees = null;
}
function clearFarmsFromMap(farmsId = Object.keys(farms_mapping)) {
  if (drawnFarms == null) return;
  if (farmsId.length == Object.keys(farms_mapping).length) {
    map.removeLayer(drawnFarms);
    drawnFarms = null;
    farms_mapping = {};
  } else {
    // const { farmsId: farmsLeafletId, ...new_farms_mapping } = farms_mapping;
    // farms_mapping = new_farms_mapping;
    const farmsLeafletId = farmsId.map((id) => farms_mapping[id]);
    farmsId.forEach((id) => delete farms_mapping[id]);
    for (let layerid of farmsLeafletId) drawnFarms.removeLayer(layerid);
  }
}
function clearDrawnItemsMap() {
  if (newFarm != null) {
    drawnItems.removeLayer(newFarm);
    newFarm = null;
  }
  newTrees.clearLayers();
}
function validateTrees(farmLayer, treesLayer) {
  if (farmLayer == null) {
    // a new farm exists
    alert("there is no farm selected to add a new tree");
  } else if (!farmLayer.contains(treesLayer.getLatLng())) {
    // tree is inside the farm
    alert("tree is outside the farm");
  } else if (treesLayer.getRadius() > 4) {
    // maximum crown radius
    alert("tree crown is too big to accept");
  } else return true;
  return false;
}
// end map section
// #endregion

// #region SelectFarmElement
const select = window.document.getElementById("myUL");
// select trigger
select.addEventListener("change", async (e) => {
  let selectedOptions = [...e.target.selectedOptions].map(
    (option) => option.value
  );
  // remember to add select all code
  console.log(selectedOptions); // final selectedFarmsId or selectedOptionsValues

  if (selectedOptions.length === 0) {
    // no selection state
    clearTreesFromMap();
    window.document.getElementById("trees_types_pieChart").hidden = true;
    window.document.getElementById("population_scatter").hidden = true;
    window.document.getElementById("detail").innerHTML = "No Farm Selected";
  } else if (selectedOptions.length === 1) {
    // one selection state --> view farm action
    farmView(selectedOptions[0]);
    window.document.getElementById("trees_types_pieChart").hidden = true;
    window.document.getElementById("population_scatter").hidden = true;
  } else {
    // multi-selection state --> view farms info action
    farmsInfoView(selectedOptions);
    window.document.getElementById("trees_types_pieChart").hidden = false;
    window.document.getElementById("population_scatter").hidden = false;
  }

  // let options = e.target.children,
  //   selectedIndex = e.target.selectedIndex;

  // if (selectedIndex < 0) return;
  // const IsSelected = selectedOptions.includes(selectedIndex);

  // if (IsSelected) {
  //   if (selectedIndex == 0) selectedOptions = [];
  //   else {
  //     selectedOptions.splice(selectedOptions.indexOf(selectedIndex), 1);
  //     if (selectedOptions.length == options.length - 1)
  //       selectedOptions.splice(selectedOptions.indexOf(0), 1);
  //   }
  // } else {
  //   if (selectedIndex == 0)
  //     selectedOptions = Array.from({ length: options.length }, (_, i) => i);
  //   else {
  //     selectedOptions.push(selectedIndex);
  //     if (selectedOptions.length == options.length - 1)
  //       selectedOptions.push(0);
  //   }
  // }
  // for (let i = 0; i < options.length; i++) options[i].selected = false;
  // for (let i = 0; i < selectedOptions.length; i++)
  //   options[selectedOptions[i]].selected = true;

  // drawnTrees.clearLayers();

  // if (
  //   selectedOptions.length == 1 ||
  //   (selectedOptions.length == 2 && selectedIndex == 0)
  // ) {
  //   // fetch trees of the new farm from server as geojson data
  //   const response = await fetch(
  //     apiURLs.tree.replace(0, options[selectedOptions[0]].value)
  //   );
  //   const data = await response.json();
  //   console.log(data);
  //   farmView(data, options[selectedOptions[0]].value);
  // } else {
  //   farmsInfoView();
  // }
});
async function farmView(farmId) {
  // fetch trees of the new farm from server as geojson data
  const geoJSONTrees = await getFarmTrees(farmId);
  const properties = getFarmsProperties([farmId])[0];
  window.document.getElementById("detail").innerHTML =
    "Area: " +
    Math.round(properties.area) +
    " m<sup>2</sup></br>Density: " +
    (properties.density * 100).toFixed(3) +
    "%</br>Trees count: " +
    properties.trees_count +
    "</br>Population: " +
    (100 * properties.population).toFixed(3) +
    "%</br>date: " +
    properties.date.slice(0, -3) +
    "</br>Tree type: " +
    properties.trees_type;

  clearTreesFromMap();
  // adding trees layer to the map
  addTreesToMap(geoJSONTrees, farmId);

  setMapViewByFarms([farmId]);

  // ui
  // const farmProperties =
  //   drawnFarms._layers[farms_mapping[farmId]].feature.properties;
  // window.document
  //   .getElementById("detail")
  //   .appendChild(
  //     window.document.createTextNode(
  //       "\n" +
  //         farmProperties["name"] +
  //         "\ntree counts:" +
  //         geoJSONTrees.features.length +
  //         "\n"
  //     )
  //   );
}
let piechart = null;
let scatter = null;
function farmsInfoView(farmsId) {
  // clear the trees from the map
  clearTreesFromMap();

  setMapViewByFarms(farmsId);

  const farmsProperties = getFarmsProperties(farmsId);
  console.log(farmsProperties);
  let result = farmsProperties.reduce((a, b) => {
    return {
      area: a.area + b.area,
      density: a.density + b.density,
      population: a.population + b.population,
      trees_count: a.trees_count + b.trees_count,
    };
  });
  let r = {
    areaAv: result.area / farmsProperties.length,
    densityAv: result.density / farmsProperties.length,
    populationAv: result.population / farmsProperties.length,
    trees_countAv: result.trees_count / farmsProperties.length,
    trees_countDensity: result.trees_count / result.area,
  };
  console.log(r);
  window.document.getElementById("detail").innerHTML =
    "Area Average: " +
    r.areaAv.toFixed(0) +
    " m<sup>2</sup><br>Trees Count Average: " +
    r.trees_countAv.toFixed(2) +
    "<br>Population Average: " +
    (r.populationAv * 100).toFixed(2) +
    "%<br>Density Average: " +
    (r.densityAv * 100).toFixed(2) +
    "%<br>Trees Count Density: " +
    (r.trees_countDensity * 100).toFixed(2) +
    "%";
  // Trees Types Pie Chart
  let count = {};
  farmsProperties
    .map((x) => x.trees_type)
    .forEach((val) => (count[val] = (count[val] || 0) + 1));
  const barColors = ["#b91d47", "#00aba9", "#2b5797", "#e8c3b9", "#1e7145"];
  if (piechart == null)
    piechart = new Chart("trees_types_pieChart", {
      type: "pie",
      data: {
        labels: Object.keys(count),
        datasets: [
          {
            backgroundColor: barColors,
            data: Object.values(count),
          },
        ],
      },
      options: {
        // tooltips: {
        //   enabled: false,
        // },
        title: {
          display: true,
          text: "Trees Types",
        },
        plugins: {
          datalabels: {
            formatter: (value, ctx) => {
              let sum = 0;
              let dataArr = ctx.chart.data.datasets[0].data;
              dataArr.map((data) => {
                sum += data;
              });
              let percentage = ((value * 100) / sum).toFixed(2) + "%";
              return percentage;
            },
            color: "#fff",
          },
        },
      },
    });
  else {
    piechart.data.labels = Object.keys(count);
    piechart.data.datasets.forEach((dataset) => {
      dataset.data = Object.values(count);
    });
    piechart.update();
  }

  const xyValues = farmsProperties.map((p) => ({
    x: p.trees_count,
    y: p.area,
  }));
  if (scatter == null)
    scatter = new Chart("population_scatter", {
      type: "scatter",
      data: {
        datasets: [
          {
            label: "population",
            pointRadius: 4,
            pointBackgroundColor: "rgba(0,0,255,1)",
            data: xyValues,
          },
        ],
      },
      options: {
        scales: {
          x: {
            type: "linear",
            position: "bottom",
            scaleShowLabels: false, // set this to false to remove labels
          },
        },
        // tooltips: {
        //   enabled: false,
        // },
        scaleShowLabels: false,
        title: {
          display: true,
          text: "Population (x=trees count, y=area)",
        },
        plugins: { datalabels: { display: false } },
      },
    });
  else {
    scatter.data.datasets.forEach((dataset) => {
      dataset.data = xyValues;
    });
    scatter.update();
  }
}

function updateSelectFarmElement(data) {
  for (let i = 0; i < data.features.length; i++) {
    const feature = data.features[i];

    const option = select.firstElementChild.cloneNode(true);
    option.hidden = false;
    option.setAttribute("value", feature.id);
    option.innerHTML = feature.properties["name"];
    select.appendChild(option);
  }
}

function clearSelectFarmElement() {
  while (select.lastElementChild.value != "-1")
    select.removeChild(select.lastChild);
  const selectAllOption = select.firstElementChild;
  selectAllOption.selected = false;
}
// end SelectFarmElement
// #endregion

// #region FilterFarmsElement
const filterForm = window.document.getElementById("do-filter");
// get filtered farms data from server
filterForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const geoJSONFarms = await getFilteredFarms();

  // clear map as a start state
  clearFarmsFromMap();
  clearTreesFromMap();

  // check geoJSONFarms
  // update map with new farms
  addFarmsToMap(geoJSONFarms);

  setMapViewByFarms();

  // make select new as a start state
  clearSelectFarmElement();

  // update select ui with new elements
  updateSelectFarmElement(geoJSONFarms);
});
async function getFilteredFarms() {
  const formData = new FormData(filterForm);
  if (formData.get("date") != "")
    formData.set("date", formData.get("date") + "-1");
  if (formData.get("in_bbox") != null)
    formData.set("in_bbox", map.getBounds().toBBoxString());
  const response = await fetch(
    `${apiURLs.farm}?${new URLSearchParams(formData)}`
  );
  const geoJSONFilteredFarms = await response.json();
  return geoJSONFilteredFarms;
}
async function getFarmTrees(farmId) {
  const response = await fetch(apiURLs.tree.replace(0, farmId));
  const geoJSONTrees = await response.json();
  console.log(geoJSONTrees);
  return geoJSONTrees;
}
// end FilterFarmsElement
// #endregion

// #region CreateFarmElement
// create new farm
if (is_authenticated)
  window.document
    .getElementById("delete_trees")
    .addEventListener("click", (e) => {
      newTrees.clearLayers();
    });
if (is_authenticated)
  window.document
    .getElementById("detect_trees")
    .addEventListener("submit", async (e) => {
      e.preventDefault();

      if (newFarm == null) return;
      const formData = new FormData(e.target);
      const data = Object.fromEntries(formData.entries());
      data["polygon"] = getNewFarmGeometry().coordinates;
      data["circles"] = newTrees
        .getLayers()
        .map((layer) => [
          layer.toGeoJSON().geometry.coordinates,
          layer.getRadius(),
        ]);
      // let data = {
      //   polygon: getNewFarmGeometry().coordinates,
      //   circles: newTrees
      //     .getLayers()
      //     .map((layer) => [
      //       layer.toGeoJSON().geometry.coordinates,
      //       layer.getRadius(),
      //     ]),
      // };
      // post new trees json and get them
      console.log(data);
      console.log(JSON.stringify(data));

      let response = await fetch(apiURLs.tree_detect, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        mode: "same-origin",
        body: JSON.stringify(data),
      });
      newTrees.clearLayers();
      const geoJSONTrees = await response.json();
      console.log(geoJSONTrees);
      if (geoJSONTrees.features.length != 0)
        L.geoJSON(geoJSONTrees, {
          pointToLayer: (f, latlng) =>
            new L.Circle(latlng, f.properties.radius),
        }).eachLayer((layer) => {
          if (newFarm.contains(layer.getLatLng())) newTrees.addLayer(layer);
        });
    });

const createForm = window.document.getElementById("farm_create");
if (is_authenticated)
  createForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    // new farm as json
    const newFarmJSON = {};
    // adding form data to new farm json
    const formData = new FormData(e.target);
    for (const [key, value] of formData.entries()) {
      console.log(key + ", " + value);
      newFarmJSON[key] = value;
    }
    newFarmJSON["polygon"] = getNewFarmGeometry();
    newFarmJSON["date"] += "-1";

    if (updateFarmId != null) {
      deleteFarm(farms_mapping[updateFarmId], updateFarmId);
      updateFarmId = null;
    }
    // post new farm geojson and get the data
    console.log(JSON.stringify(newFarmJSON));
    let response = await fetch(apiURLs.farm, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      mode: "same-origin",
      body: JSON.stringify(newFarmJSON),
    });
    const newFarmJSONResponse = await response.json();
    const farmId = newFarmJSONResponse.id;

    // trees
    if (newTrees.getLayers().length !== 0) {
      // new trees as json
      let newTreesJSON = getNewTreesJSON(farmId);

      // post new trees json and get them
      console.log(JSON.stringify(newTreesJSON));
      response = await fetch(apiURLs.tree.replace(0, farmId), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        mode: "same-origin",
        body: JSON.stringify(newTreesJSON),
      });
      newTreesJSON = await response.json();
    }

    // remove last-added drawn new farm layer
    clearDrawnItemsMap();
    window.document.getElementById("farm_create_ui").hidden = true;
    window.document.getElementById("detect_trees_ui").hidden = true;
  });
// end CreateFarmElement
// #endregion

// #region FarmOperations
export async function copyFarm(farmLeafletId, farmId) {
  clearDrawnItemsMap();

  const farmLayer = drawnFarms.getLayer(farmLeafletId);
  newFarm = L.polygon(farmLayer.getLatLngs(), drawnItems.options).addTo(
    drawnItems
  );
  // fetch trees of the new farm from server as geojson data
  const geoJSONTrees = await getFarmTrees(farmId);
  if (geoJSONTrees.features.length != 0)
    L.geoJSON(geoJSONTrees, {
      pointToLayer: (f, latlng) => new L.Circle(latlng, f.properties.radius),
    }).eachLayer((layer) => newTrees.addLayer(layer));

  clearTreesFromMap();
  window.document.getElementById("farm_create_ui").hidden = false;
  window.document.getElementById("detect_trees_ui").hidden = false;
}
export async function deleteFarm(farmLeafletId, farmId) {
  await fetch(apiURLs.farm_detail.replace(0, farmId), {
    method: "DELETE",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
    mode: "same-origin",
  });
  clearTreesFromMap();
  clearFarmsFromMap([farmId]);
}
let updateFarmId = null;
export async function updateFarm(farmLeafletId, farmId) {
  clearDrawnItemsMap();

  const farmLayer = drawnFarms.getLayer(farmLeafletId);
  newFarm = L.polygon(farmLayer.getLatLngs(), drawnItems.options).addTo(
    drawnItems
  );
  // fetch trees of the new farm from server as geojson data
  const geoJSONTrees = await getFarmTrees(farmId);
  if (geoJSONTrees.features.length != 0)
    L.geoJSON(geoJSONTrees, {
      pointToLayer: (f, latlng) => new L.Circle(latlng, f.properties.radius),
    }).eachLayer((layer) => newTrees.addLayer(layer));

  clearTreesFromMap();
  updateFarmId = farmId;
  window.document.getElementById("farm_create_ui").hidden = false;
  window.document.getElementById("detect_trees_ui").hidden = false;
}
// #endregion

// #region map style
const pointToCircleLayer = (feature, latlng) =>
  new L.Circle(latlng, feature.properties.radius);
function onEachFarmFeature(feature, layer) {
  const properties = feature.properties;
  layer.on({
    mouseover: (e) => {
      e.target.setStyle({
        weight: 5,
        color: "#666",
        dashArray: "",
        fillOpacity: 0.7,
      });
      info.update(e.target.feature.properties);
    }, // highlightFeature
    mouseout: (e) => {
      drawnFarms.resetStyle(e.target);
      info.update();
    }, // resetHighlight
    click: (e) => farmView(e.target.feature.id), // map.fitBounds(e.target.getBounds()), // zoomToFeature
  });
  let farmPopupButton = (name, btnName) =>
    '<button id="' +
    name +
    L.stamp(layer) +
    '" onclick="' +
    name +
    "(" +
    L.stamp(layer) +
    "," +
    feature.id +
    ')">' +
    btnName +
    "</button>";
  let popupContent =
    "<b>area: " +
    Math.round(properties.area) +
    " m<sup>2</sup></br>density: " +
    (properties.density * 100).toFixed(3) +
    "%</br>trees count: " +
    properties.trees_count +
    "</br>tree population: " +
    (100 * properties.population).toFixed(3) +
    "%</br>date: " +
    properties.date.slice(0, -3) +
    "</br>tree type: " +
    properties.trees_type +
    "</b>" +
    "</br>" +
    (is_authenticated
      ? farmPopupButton("copyFarm", "add new") +
        farmPopupButton("deleteFarm", "delete") +
        farmPopupButton("updateFarm", "update")
      : "");
  layer.bindPopup(popupContent);
  // let hexColor =
  //   "#" +
  //   Math.floor(properties.density * 255)
  //     .toString(16)
  //     .toUpperCase() +
  //   (properties.density < 0.062745098 ? "0" : "") +
  //   "00" +
  //   Math.floor((1 - properties.density) * 255)
  //     .toString(16)
  //     .toUpperCase() +
  //   (properties.density > 0.937254902 ? "0" : "");
  // layer.setStyle({ color: hexColor });
  // console.log(hexColor);
}
let farmColors = [
  "#ffffcc",
  "#ffeda0",
  "#fed976",
  "#feb24c",
  "#fd8d3c",
  "#fc4e2a",
  "#e31a1c",
  "#bd0026",
  "#800026",
];
let getColor = (v, min, max) =>
  farmColors[
    Math.max(
      0,
      Math.min(
        farmColors.length - 1,
        Math.floor(((farmColors.length - 1) * (v - min)) / (max - min))
      )
    )
  ];
let drawnFarmsStyle = (feature) => ({
  fillColor: getColor(feature.properties.density, 0, 1),
  weight: 2,
  opacity: 1,
  color: "white",
  dashArray: "2",
  fillOpacity: 0.1,
});
let infoOnMap = (props) =>
  "<h4>Trees Density</h4>" +
  (props
    ? "<b>" +
      props.name +
      "</b><br />" +
      ((100 * props.trees_count) / props.area).toFixed(3) +
      " trees / mi<sup>2</sup>"
    : "Hover over a farm");
// #endregion

// #region HelperFunctions

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
// #endregion
