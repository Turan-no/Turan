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
        var lgpx = new OpenLayers.Layer.GML("Route", gpx_file, {
            format: OpenLayers.Format.GPX,
            style: {strokeColor: "purple", strokeWidth: 5, strokeOpacity: 0.5, label: "Start"},
            projection: this.projection
        });
        lgpx.events.register("loadend", this, this.resizeMapToLayerExtents);


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

        var defaultlayers = [layerMapnik, layerCycleMap, layerTilesAtHome, FKB, FKBraster, lgpx];
        if (start) {
            if (start[0] > 4 && start[1] > 57) { // Quickfix for checking for norwegian maps or not
                defaultlayers = [FKB, FKBraster, layerMapnik, layerCycleMap, layerTilesAtHome, lgpx];
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

            this.vectors = new OpenLayers.Layer.Vector("HR Line", {
                strategies: [new OpenLayers.Strategy.Fixed()],                
                protocol: new OpenLayers.Protocol.HTTP({
                    url: geojson_url,
                    format: new OpenLayers.Format.GeoJSON({
                                  'internalProjection': new OpenLayers.Projection("EPSG:4326"),
//                                  'externalProjection': new OpenLayers.Projection("EPSG:900913")
                                  }
                        )
                }),
                projection: this.projection,
                styleMap: this.styles,

            });
            this.map.addLayer(this.vectors);
        }
        
        this.map.render("map");
        return this.map;
    /*pushPoints: function(poslist) {
        if (typeof(poslist) != "undefined") {
            for (var i = 0; i < poslist.length; i++) {
                var p = poslist[i];
                this.route_points.push(new OpenLayers.Geometry.Point(p[0], p[1]));
            
            }
    },
    */
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
            //if ( this.posMarker != null )
            //    this.posMarker.erase();
            this.deleteMarkers();
            //this.posMarker = this.startMarker.clone()
            //this.startMarker.erase();
            lonlat = new OpenLayers.LonLat(x, y).transform(this.projection, this.map.getProjectionObject());
            this.posMarker = new OpenLayers.Marker(lonlat, this.pos_icon.clone());
            this.layerMarkers.addMarker(this.posMarker);
            //        this.layerMarkers.redraw();
        }
    },
    loadGeoJSON: function(minIndex, maxIndex) {
        if (this.map != null) {
        if (this.geojson_url) {
            this.map.removeLayer(this.map.getLayersByName('HR Line')[0]);
            var selection_vectors = new OpenLayers.Layer.Vector("HR Line", {
                    strategies: [new OpenLayers.Strategy.Fixed()],                
                    protocol: new OpenLayers.Protocol.HTTP({
                        url: this.geojson_url + '?start=' + minIndex + '&stop=' + maxIndex,
                        format: new OpenLayers.Format.GeoJSON({ 'internalProjection': new OpenLayers.Projection("EPSG:4326"), })
                    }),
                    projection: this.projection,
                    styleMap: this.styles
                });
                this.map.addLayer(selection_vectors);
                selection_vectors.events.register("loadend", this, this.resizeMapToLayerExtents);
        }
        }
     } 
};
