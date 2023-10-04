// define global variables
var layer;  // for last polygon created layer

var map; // the map

var form = document.getElementById("form"); // get form data from document

var drawnItems = new L.FeatureGroup(); // drawn items layer


// add initial map event
window.addEventListener("map:init", map_init, false);


//initial map function
function map_init(e) {

  //get map from event data
  map = e.detail.map;

  //get map options from event data
  //var options = e.detail.options;

  //add layer for drown polygons 
  map.addLayer(drawnItems);

  //declare map draw control
  var drawControl = new L.Control.Draw({
    
    // draw tools position
    position: "topright",

    // draw options
    draw: {

      polyline: false, // disable drawing line
      
      polygon: {
        allowIntersection: false, // Restricts shapes to simple polygons
        
        //error message options
        drawError: {
          color: "#e1e100", // Color the shape will turn when intersects
          message: "<strong>Oh snap!<strong> you can't draw that!", // Message that will show when intersect
        },
        
        //shape options
        shapeOptions: {
          color: "#bada55", //shape color
        },
        
        showArea: true, //show polygon area
        zIndexOffset: 1, //select z index offset
      },

      marker: false, //disable drawing marker
      circle: false, //disable drawing circle
      rectangle: false, //disable drawing rectangle
      circlemarker: false, //disable drawing circle marker
      
      //toolbar options
      toolbar: {
        buttons: {
          polygon: "draw a region",
        },
      },
    },
    
    //edit options
    edit: {
      featureGroup: drawnItems, //REQUIRED!!
      edit: false, //disable edit
      remove: true, //enable remove
    },
  
  });

  // Add control settings to the map
  map.addControl(drawControl);
  L.drawLocal.draw.toolbar.buttons.polygon = "Create a customized region";

  // Create polygon event
  map.on('draw:created', function (e) {

    
    // get polygon type and polygon layer from event data
    // var type = e.layerType;
    layer = e.layer;
    console.log(layer);

    // get submit button from document and click it
    var submitButton = document.getElementById("submit-button");
    submitButton.click();

  });
 
  // Delete polygon event
  map.on("draw:deleted", (e) => {
    
    console.log('this in on delete function');

    e.layers.eachLayer((layer) => {

      console.log('the tile layer:');
      console.log(layer.tileLayer);

      layer.tileLayer.remove(); //remove tilelayer
      drawnItems.removeLayer(layer); //remove polygon layer
    });

    });

}// end map init



// add submit event to the form
form.addEventListener('submit', async function (e) {

    // deactivate default behavior
    e.preventDefault();

    
    // get form data from document
    //var form = window.document.getElementById("form");
    
    // hide the form
    form.style.display = "none";

    // extract form data
    const formData = new FormData(form);
    
    // create object for form data
    const json = {};

    // add form data to the object
    Array.from(formData.entries()).forEach(([key, value]) => {
      json[key] = value;
    });

    // add polygon coordinates to the object
    json["study_region"] = JSON.stringify(
      layer.toGeoJSON().geometry.coordinates[0]
    );

    // extract csrf token from json object form and delete it from the object
    var csrf = json['csrfmiddlewaretoken']
    delete json.csrfmiddlewaretoken

    // print json object and csrf token in the console
    console.log('Request json:');
    console.log(json);
    console.log('The csrf Token : \n' + csrf);

    // make query using fetch api 
    const response = await fetch(form.action, {
      
      method: "POST", // using POST method
      
      // add headers
      headers: {
        
        "Content-Type": "application/json",  // content type
        "X-CSRFToken": csrf, // add csrf token
      
      },
      
      body: JSON.stringify(json), // convert json object into json format and add it to the body
    });

    // get response data
    const data = await response.json();
    
    // print response data
    console.log('The url respone: \n' +  data["url"]);
    
    // get url from response
    const tileLayer_url = await data["url"];

    //check if tilelayer not empty
    if(tileLayer_url)
    {
    
    // add polygon layer to drawn layer
    drawnItems.addLayer(layer);

    // add response tile layer
    const tileLayer = await L.tileLayer(tileLayer_url);
    tileLayer.addTo(map);
    layer.tileLayer = await tileLayer; // add response to polygon tile layer
    
    }
    else
    {
      var errors= ""
      data["errors"].forEach( (item, index) => {
        errors += "* "+item+"\n"
      });

      alert(errors)
    }

    // display form
    form.style.display = "block";

  }); // end on submit event
  
  
