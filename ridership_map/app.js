function makeMap() {

	var skobblerUrl1 = 'http://tiles{s}-73ef414d6fe7d2b466d3d6cb0a1eb744.skobblermaps.com/TileService/tiles/2.0/11021111200/0/{z}/{x}/{y}.png24';
	var streets = L.tileLayer(skobblerUrl1, {
		attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
		detectRetina:true,
		maxZoom: 19,
		maxNativeZoom: 18,
		subdomains: '1234'
	});
	var buildings = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
		detectRetina:true,
		maxZoom: 20,
		maxNativeZoom: 19
	});
	var satellite = L.tileLayer('https://api.tiles.mapbox.com/v4/mapbox.streets-satellite/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoic3RldmV2YW5jZSIsImEiOiJqRVdYSnFjIn0.cmW3_zqwZpvcwPYc_C2SPQ', {
		attribution: '<a href="http://mapbox.com">Mapbox</a>',
		detectRetina:false,
		maxZoom: 20,
		maxNativeZoom: 19
	});

	// initialize the map on the "map" div with a given center and zoom
	map = L.map('map', {
	    center: [41.505, -87.4],
	    zoom: 15
	});
	
	// Make some empty layers that will be filled later
	layer = new L.featureGroup();
	
	var otherLayers = {};
	
	// add the base layer maps
	var baseMaps = {"Streets": streets, "Building Names": buildings, "Satellite": satellite};
	streets.addTo(map); // load streets by default
	
	// create a layer control that turns on/off layers
	//control = L.control.layers(baseMaps, otherLayers, {collapsed: false, autoZIndex: false}).addTo(map);

	infoBox = createInfoBox().addTo(map);
	
	layer.addTo(map);
	
	// Adjust the map size
	resizeMap();
	$(window).on("resize", resizeMap);
}


function createInfoBox() {
	var info = L.control();

	info.onAdd = function (map) {
	    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
	    this.update();
	    return this._div;
	};

	info.update = function (props) {
	    this._div.innerHTML = '<h4>Bus Ridership Density</h4>' +  (props ?
		    '<b>' + '</b><br />' + props.num_passengers + ' people / day'
			    : 'Hover over a street segment');
			    };
	return info;
}

function highlightFeature(e) {
	var layer = e.target;
	if (layer.feature) {
		layer.setStyle({
			weight: 15,
		});

		if (!L.Browser.ie && !L.Browser.opera) {
			layer.bringToFront();
		}
		infoBox.update(layer.feature.properties);
	}
}

function resetHighlight(e) {
	geojsonLayer.resetStyle(e.target);
	infoBox.update();
}

function addGeoJsonLayer(file) {
	
	/*
	* A generic function that simply adds our GeoJSON file to the map
	* and fits the map bounds (the viewport) to the extents of the GeoJSON features (zooms in or out
	* to show all the features)
	*/
	
	console.log("adding file '" + file + "'");
	$.getJSON(file, function() {
		console.log( "success" );
	})
	.done(function(data) {
		data = data;
		count = data.features.length;
		
		this.range = getNormalized(data);
		
		// Add the data to our GeoJSON layer
		geojsonLayer = L.geoJson(data, {
			style: style,
			onEachFeature: onEachFeature	
		});
		layer.addLayer(geojsonLayer);
		
		// Fit the map to that layer 
		map.fitBounds(layer.getBounds());
		
		// Add the layer to our layer switcher
		//control.addOverlay(layer, "Features (" + count + ")");
	})
	.fail(function() {
		alert("Couldn't load your GeoJSON file; is it where you said it is?")
	})
	.always(function() {

	});
	
}

function getNormalized(data) {
	
	/*
	* This function gets the min and max values for our bus ridership data
	*/
	
	values = [];
	range = [];
	$.each(data.features, function(i, v) {
		p = v.properties;
		values.push(p.num_passengers);
	});
	
	max = Math.max.apply(Math, values);
	min = Math.min.apply(Math, values);
	
	range['max'] = max;
	range['min'] = min;
	
	return range;
}

function getZScore(value) {
	
	/*
	* This function calculates a Z score, a number between 0 and 1 that normalizes 
	* the bus passengers data so that we can easily style the lines
	*/
	
	z = (value - this.range['min'])/(this.range['max'] - this.range['min']) * 200;
	console.log(z);
	
	return z;
}

function resizeMap() {
	
	/*
	* Resizes the map to fit the full height
	* It should be paired with a window.resize event so that it'll be resized
	* anytime the user resizes the window
	*/
	
	console.log("window has been resized");
	
	height = $("body").outerHeight();
	$("#map").height( height );
	map.invalidateSize();
	
	return height;
}

function getColor(value) {

	var val = value;
	var colorsArray = [
		'#9ecae1','#6baed6','#4292c6','#2171b5','#084594'];
	//Finding the percentile. Update the formula if changes nees to be done.
	var percentile = (val/this.range['max']) * 100; 
	// console.log("Accessed"+this.range['max']+"Value"+val);

	if(percentile>90){
		var index = 4;
	} else if(percentile>75){
		var index = 3;
	} else if(percentile>50){
		var index = 2;
	} else if(percentile>25){
		var index = 1;
	} else {
		var index = 0;
	};
	return colorsArray[index];
}

function style(feature) {
	if(feature.properties) {
		p = feature.properties;
		return {
			weight: 6,
			color: getColor(p.num_passengers),
			opacity: 1
		};
	} else { console.log('no properties'); return {}; }
}
function onEachFeature(feature, layer) {
	
	/*
	* This function will be called for each feature in your GeoJSON file
	* and this is where you should customize whether there should be a popup on features
	* and how features should be styled
	*/
	
 	layer.on({
		mouseover: highlightFeature,
		mouseout: resetHighlight,
	});
}
