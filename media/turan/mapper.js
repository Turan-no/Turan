/**
 * Mapper class responsible for drawing trip map
 */
var Mapper = {
    map: null,
    projection: new OpenLayers.Projection("EPSG:4326"),

    resizeMapToLayerExtents: function (evt) {
        this.map.zoomToExtent(evt.object.getDataExtent());
    },

    init: function(gpx_file, geojson_url, start, end) {
        if (gpx_file) {
            var lgpx = new OpenLayers.Layer.GML("Route", gpx_file, {
                format: OpenLayers.Format.GPX,
                style: {strokeColor: "purple", strokeWidth: 5, strokeOpacity: 0.5, label: "Start"},
                projection: this.projection
            });
            lgpx.events.register("loadend", this, this.resizeMapToLayerExtents);
            this.lgpx = lgpx;
        }


        this.map = new OpenLayers.Map ({
            controls:[
                new OpenLayers.Control.Navigation(),
                new OpenLayers.Control.PanZoomBar(),
                //new OpenLayers.Control.MousePosition(),
                //new OpenLayers.Control.Permalink('permalink'),
                //new OpenLayers.Control.OverviewMap(),
                new OpenLayers.Control.LayerSwitcher(),
                new OpenLayers.Control.Attribution()],
            //maxExtent: lgpx.getDataExtent(),
            //maxResolution: 59.0399,
            maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
            maxResolution: 156543.0399,
            numZoomLevels: 20,
            units: 'm',
            projection: "EPSG:900913",
            //projection: this.projection,
            displayProjection: this.projection
        });
                

         var FKB = new OpenLayers.Layer.WMS(
            'Topo Norge (N50,FKB)',
            'http://opencache.statkart.no/gatekeeper/gk/gk.open',
            {layers: 'topo2', format: 'image/png'},
            {minZoomLevel: 5, maxZoomLevel: 19,
                transitionEffect: 'resize',
             attribution: 'Kartgrunnlag: ' +
              '<a href="http://www.statkart.no/">Statens kartverk</a>, ' +
              '<a href="http://www.statkart.no/nor/Land/Fagomrader/Geovekst/">Geovekst</a> og ' +
              '<a href="http://www.statkart.no/?module=Articles;action=Article.publicShow;ID=14194">kommuner</a>'});
         var FKBraster = new OpenLayers.Layer.WMS(
            'Topo Raster',
            'http://opencache.statkart.no/gatekeeper/gk/gk.open',
            {layers: 'toporaster2', format: 'image/png'},
            {minZoomLevel: 5, maxZoomLevel: 19,
             attribution: 'Kartgrunnlag: ' +
              '<a href="http://www.statkart.no/">Statens kartverk</a>, ' +
              '<a href="http://www.statkart.no/nor/Land/Fagomrader/Geovekst/">Geovekst</a> og ' +
              '<a href="http://www.statkart.no/?module=Articles;action=Article.publicShow;ID=14194">kommuner</a>'});
        var layerMapnik = new OpenLayers.Layer.OSM.Mapnik("Mapnik");
        var layerCycleMap = new OpenLayers.Layer.OSM.CycleMap("CycleMap");
        var layerTilesAtHome = new OpenLayers.Layer.OSM.Osmarender("Osmarender");
        var gphy = new OpenLayers.Layer.Google(
            "Google Physical",
            {type: google.maps.MapTypeId.TERRAIN}
        );
        var gmap = new OpenLayers.Layer.Google(
            "Google Streets", // the default
            {numZoomLevels: 20}
        );
        var ghyb = new OpenLayers.Layer.Google(
            "Google Hybrid",
            {type: google.maps.MapTypeId.HYBRID, numZoomLevels: 20}
        );
        var gsat = new OpenLayers.Layer.Google(
            "Google Satellite",
            {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22}
        );
        this.gsat = gsat;
        this.FKB = FKB;


        var defaultlayers = [layerMapnik, layerCycleMap, layerTilesAtHome, FKB, FKBraster, gphy, gmap, ghyb, gsat];
        if (start) {
            if (start[0] > 4 && start[1] > 57) { // Quickfix for checking for norwegian maps or not
                defaultlayers = [FKB, FKBraster, layerMapnik, layerCycleMap, layerTilesAtHome, gphy, gmap, ghyb, gsat];
            }
        }
        this.map.addLayers(defaultlayers);
        

        if (start) {

            var size = new OpenLayers.Size(16,16);
            var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
            var startlonlat = new OpenLayers.LonLat(start[0],start[1]).transform(this.projection, this.map.getProjectionObject());
            var endlonlat = new OpenLayers.LonLat(end[0],end[1]).transform(this.projection, this.map.getProjectionObject());

            var stop_icon = new OpenLayers.Icon('http://turan.no/site_media/pinax/images/silk/icons/flag_red.png',size,offset);
            var start_icon = new OpenLayers.Icon('http://turan.no/site_media/pinax/images/silk/icons/flag_green.png',size,offset);
            var pos_icon = new OpenLayers.Icon('http://turan.no/site_media/pinax/images/silk/icons/flag_yellow.png',size,offset);
            layerMarkers = new OpenLayers.Layer.Markers("Markers");
            this.layerMarkers = layerMarkers;
            this.map.addLayer(layerMarkers);
            this.start_icon = start_icon;
            this.stop_icon = stop_icon;
            this.pos_icon = pos_icon;



            this.startMarker = new OpenLayers.Marker(startlonlat, start_icon);
            this.stopMarker = new OpenLayers.Marker(endlonlat, stop_icon);
            this.posMarker = null;

            layerMarkers.addMarker(this.startMarker);
            layerMarkers.addMarker(this.stopMarker);
        } 
        this.geojson_url = geojson_url;
        if (geojson_url) {
            this.styles = new OpenLayers.StyleMap({
                "default": {
                    strokeWidth: 2
                },
                "select": {
                    strokeColor: "#0099cc",
                    strokeWidth: 4
                }
            });
        
            // add rules from the above lookup table
            this.styles.addUniqueValueRules("default", "ZONE", {
                0: {strokeColor: colorToHex(colors[0]), strokeWidth: 4},
                1: {strokeColor: colorToHex(colors[1]), strokeWidth: 4},
                2: {strokeColor: colorToHex(colors[2]), strokeWidth: 4},
                3: {strokeColor: colorToHex(colors[3]), strokeWidth: 4},
                4: {strokeColor: colorToHex(colors[4]), strokeWidth: 4},
                5: {strokeColor: colorToHex(colors[5]), strokeWidth: 4},
                6: {strokeColor: colorToHex(colors[6]), strokeWidth: 4},
                7: {strokeColor: colorToHex(colors[7]), strokeWidth: 4}
            });

            /*this.vectors = new OpenLayers.Layer.Vector("HR Line", {
                strategies: [new OpenLayers.Strategy.Fixed()],                
                protocol: new OpenLayers.Protocol.HTTP({
                    url: geojson_url,
                    format: new OpenLayers.Format.GeoJSON({
                                  'internalProjection': this.projection,
//                                  'externalProjection': new OpenLayers.Projection("EPSG:900913")
                                  }
                        )
                }),
                projection: this.projection,
                styleMap: this.styles,

            });
            this.map.addLayer(this.vectors);*/
        }
        
        this.map.render("map");
        if (gpx_file) {
            this.map.addLayer(lgpx);
            this.lgpx.setVisibility(true); // Dunno why this was needed after openlayers 2.8
        }
        return this.map;
    },
    deleteMarkers: function() {
        var i=0;
        var myMarkers = this.layerMarkers.markers;
        while (i<myMarkers.length) {
            var myMarker = myMarkers[i];
            if (myMarker != this.startMarker && myMarker != this.stopMarker) {
                this.layerMarkers.removeMarker(myMarker);
            } else {
                    i=i+1;
           }
        }
    },
    updatePosMarker: function(x, y) {
        if (x != undefined && y != undefined ) {
            this.deleteMarkers();
            lonlat = new OpenLayers.LonLat(x, y).transform(this.projection, this.map.getProjectionObject());
            this.posMarker = new OpenLayers.Marker(lonlat, this.pos_icon.clone());
            this.layerMarkers.addMarker(this.posMarker);
        }
    },
    zoomToPosMarker: function() {
        lonlat = this.posMarker.lonlat;
        this.map.setCenter(lonlat);
    }, 
    panTo: function(x1, y1) {
        lonlat =new OpenLayers.LonLat(x1,y1 ).transform(new OpenLayers.Projection("EPSG:4326"), this.map.getProjectionObject());;
        this.map.panTo(lonlat);
    }, 
    loadGeoJSON: function(minIndex, maxIndex) {
        if (this.map != null) {
        if (this.geojson_url) {
            oldlayer = this.map.getLayersByName('HR Line');
            if (oldlayer.length) {
                this.map.removeLayer(oldlayer[0]);
            }
            var selection_vectors = new OpenLayers.Layer.Vector("HR Line", {
                    strategies: [new OpenLayers.Strategy.Fixed()],                
                    rendererOptions: { zIndexing: true },
                    protocol: new OpenLayers.Protocol.HTTP({
                        url: this.geojson_url + '?start=' + minIndex + '&stop=' + maxIndex,
                        format: new OpenLayers.Format.GeoJSON({ 'internalProjection': this.projection })
                    }),
                    projection: this.projection,
                    styleMap: this.styles
                });
                this.map.addLayer(selection_vectors);
                selection_vectors.events.register("loadend", this, this.resizeMapToLayerExtents);
        }
        if (!this.map.center) {
            this.map.zoomToExtent(this.lgpx.getDataExtent());
        }
        
     } 
    },
    initLine: function(name) {
        lineLayer = new OpenLayers.Layer.Vector(name);
        map.addLayer(lineLayer);
        return lineLayer;
    },
    drawLine: function(layer, color, x1, y1, x2, y2) {

        points = new Array();
        style = { strokeColor: color, 
         strokeOpacity: 0.8,
         strokeWidth: 2
        };

        points[0] =new OpenLayers.LonLat(x1,y1 ).transform(new OpenLayers.Projection("EPSG:4326"), this.map.getProjectionObject());;
        points[0] = new OpenLayers.Geometry.Point(points[0].lon,points[0].lat);

        points[1] = new OpenLayers.LonLat(x2,y2 ).transform(new OpenLayers.Projection("EPSG:4326"), this.map.getProjectionObject());;
        points[1] = new OpenLayers.Geometry.Point(points[1].lon,points[1].lat);
        var linear_ring = new OpenLayers.Geometry.LinearRing(points);
        polygonFeature = new OpenLayers.Feature.Vector(
         new OpenLayers.Geometry.Polygon([linear_ring]), null, style);
         layer.addFeatures([polygonFeature]);
  },
  initMarker: function (icon_url, lon, lat) {
    var size = new OpenLayers.Size(32,32);
    var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
    var pos_icon = new OpenLayers.Icon(icon_url,size,offset);
    var lonlat = new OpenLayers.LonLat(lon, lat).transform(this.projection, this.map.getProjectionObject());
    var posMarker = new OpenLayers.Marker(lonlat, pos_icon);// Dummy pos, updated lateer
    layerMarkers.addMarker(posMarker);
    return posMarker;
  },
  moveMarker: function (marker, lon, lat) {
    var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), this.map.getProjectionObject());
    var newPx = map.getPixelFromLonLat(lonLat);
    marker.moveTo(newPx);
  },
  initFeature: function(athlete, icon_url) {
      var athleteStyleMap = new OpenLayers.StyleMap({
	  	externalGraphic: icon_url,
	  	graphicWidth: 32,
	  	graphicHeight: 32,
        graphicZIndex:745, // Over other layers TODO
	  	fillOpacity: 1,
	  	rotation: "${angle}",
	  });
	  athleteLayer=new OpenLayers.Layer.Vector(athlete,{styleMap:athleteStyleMap});
      this.map.addLayer(athleteLayer)
      return athleteLayer;

  },
  createFeature: function(layer, lon, lat, angle) {
    lonlat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), this.map.getProjectionObject());
    point = new OpenLayers.Geometry.Point(lonlat.lon,lonlat.lat);
    var feature = new OpenLayers.Feature.Vector(point, {
        angle: angle,
        rendererOptions: { zIndexing: true },
        poppedup: false
    });
    layer.addFeatures([feature]);
    return feature;

  },
  moveFeature: function(feature, lon, lat, angle) {
    lonlat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), this.map.getProjectionObject());
    point = new OpenLayers.Geometry.Point(lonlat.lon,lonlat.lat);
    if(angle) {
        feature.attributes.angle = angle;
        if(feature.attributes.angle>360){feature.attributes.angle -= 360;}
    }
    feature.move(lonlat);

  },
  calculateAngle: function(x1, y1, x2, y2) {
    var startPt=map.getPixelFromLonLat(new OpenLayers.LonLat(x1, y1).transform(new OpenLayers.Projection("EPSG:4326"), this.map.getProjectionObject()));
    var endPt=map.getPixelFromLonLat(new OpenLayers.LonLat(x2, y2).transform(new OpenLayers.Projection("EPSG:4326"), this.map.getProjectionObject()));
    //in the above line I think it would work too if we use Coordinates
    //instead of Pixels, but I used pixel cause its easy to do the math with
    var dy=endPt.y - startPt.y;
    var dx=endPt.x - startPt.x;
    var angle=Math.atan(dy/dx) / (Math.PI/180); //convert to degrees
    if(dx<0) // adjustment in angle for line moving to bottom
    angle-=180; // switch direction..if I dont do this.. the traigle will
                //point in other direction in certain cases
    return angle;   
  }

};
