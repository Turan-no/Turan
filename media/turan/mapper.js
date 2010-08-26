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
            projection: this.projection,
            
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

        this.map.addLayers([FKB, FKBraster, layerMapnik, layerCycleMap, layerTilesAtHome, lgpx]);

        if (start) {
            var size = new OpenLayers.Size(20,25);
            var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
            var startlonlat = new OpenLayers.LonLat(start[0],start[1]).transform(this.projection, this.map.getProjectionObject());
            var endlonlat = new OpenLayers.LonLat(end[0],end[1]).transform(this.projection, this.map.getProjectionObject());

            var icon = new OpenLayers.Icon('http://www.openstreetmap.org/openlayers/img/marker.png',size,offset);
            layerMarkers = new OpenLayers.Layer.Markers("Markers");
            this.map.addLayer(layerMarkers);

            layerMarkers.addMarker(new OpenLayers.Marker(startlonlat, icon));
            layerMarkers.addMarker(new OpenLayers.Marker(endlonlat, icon.clone()));
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
                0: {strokeColor: "#CCCCCC", strokeWidth: 4},
                1: {strokeColor: "#3366FF", strokeWidth: 4},
                2: {strokeColor: "#66CC00", strokeWidth: 4},
                3: {strokeColor: "#FF00FF", strokeWidth: 4},
                4: {strokeColor: "#FF9900", strokeWidth: 4},
                5: {strokeColor: "#FF99FF", strokeWidth: 4},
                6: {strokeColor: "#FF99FF", strokeWidth: 4},
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
                styleMap: this.styles
            });
            this.map.addLayer(this.vectors);
        }
        
        this.map.render("map");
        return this.map;
    },
    loadGeoJSON: function(minIndex, maxIndex) {
        if (this.map != null) {
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
    }}
};
