/* Colors in use for lots of zone related stuffs */
var colors = [
    "rgb(240,240,240)", 
    "rgb(102,204,0)", 
    "rgb(000,200,255)",
    "rgb(51,102,255)", 
    "rgb(255,153,0)", 
    "rgb(255,0,0)", 
    "rgb(166,0,0)", 
    "rgb(119,0,119)"];

var playercolors = [
    { r: 255, g: 20, b: 20 },
    { r: 20, g: 20, b: 255 },
    { r: 20, g: 255, b: 255 },
    { r: 255, g: 20, b: 255 },
    { r: 255, g: 255, b: 20 },
    { r: 80, g: 80, b: 80 }
];

/* conver rgb colors to hex, openlayers uses those */
function colorToHex(c) {
    var m = /rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/.exec(c);
    return m ? '#' + (1 << 24 | m[1] << 16 | m[2] << 8 | m[3]).toString(16).substr(1) : c;
}

/* Used by flot axis */
var axisformatters = {
    speed: function(val, axis) {
        return (val).toFixed(axis.tickDecimals) + ' km/h';
    },
    altitude: function(val, axis) {
        return (val).toFixed(axis.tickDecimals) + ' m';
    },
    length: function(val, axis) {
        return (Math.round(val*100)/100) + ' km';
    },
    distance: function(val, axis) {
        return (Math.round(val*100)/100) + ' km';
    },
    power: function(val, axis) {
        return (val).toFixed(axis.tickDecimals) + ' W';
    },
    hr: function(val, axis) {
        return (val).toFixed(axis.tickDecimals) + ' BPM';
    },
    temp: function(val, axis) {
        return (val).toFixed(axis.tickDecimals) + ' ℃';
    },
    percent: function(val, axis) {
        return (val).toFixed(axis.tickDecimals) + ' %';
    },
    time: function(val, axis) {
        var hours = Math.floor(val / 60);
        var minutes = Math.floor(val - hours * 60);
	var seconds = Math.round(60 * (val - Math.floor(val)));

	var r = "";

        if (hours)
            r += hours + 'h ';

	if (minutes)
	    r += minutes + 'm ';

	if (seconds)
	    r += seconds + 's';
	return $.trim(r);
    },
    duration: function(val, axis) {
        var days    = parseInt((val / (60*60*24)));
        var hours   = parseInt((val % (60*60*24)) / (60*60));
        var minutes = parseInt((val % (60*60)) / (60));

        var result = [];

        if (days > 0) {
            result.push(days + "d");
        }
        if (hours > 0) {
            result.push(hours + "h");
        }
        if (minutes > 0) {
            result.push(minutes + "m");
        }
        if (result.length == 0) {
            return "0m" 
        }
        if (result.length == 1) {
            return result[0];
        }
        return result.slice(0, result.length-1).join(", ") + " " + result[result.length-1];
    }
};

function choose (set) {
    return set[Math.floor(Math.random() * set.length)];
}

jQuery.fn.autoscroll = function() {
    $('html,body').animate({scrollTop: this.offset().top}, 500);
}
$(function() {
    function popupfadein(evt) {
        var itemId = this.getAttribute("id").split("_")[1];
        
        var popupBox = $("#mouseover_" + itemId).show();
        var boxWidth = 300;
        var boxHeight = popupBox.height();
        popupBox.css({ 
            left: evt.clientX + 10 + (evt.clientX + boxWidth > window.innerWidth ? - boxWidth - 50 + window.innerWidth - evt.clientX : 0) + "px", 
            top: evt.clientY + 10 + (evt.clientY + boxHeight > window.innerHeight ? - boxHeight - 50 + window.innerHeight - evt.clientY : 0) + "px", 
            width: boxWidth + "px" 
        });
    }

    function popupfadeout(evt) {
        var itemId = this.getAttribute("id").split("_")[1];
        
        var popupBox = $("#mouseover_" + itemId).hide();
    }

    $(".hoverpoint").hoverIntent({timeout: 0, interval: 500, over: popupfadein, out: popupfadeout});

    function profilepopupfadein(evt) {
        var itemId = this.getAttribute("id").split("_")[1];
        
        var popupBox = $("#profile_" + itemId).show();
        var boxWidth = 300;
        popupBox.css({ left: evt.clientX + 10 + (evt.clientX + boxWidth > window.innerWidth ? - boxWidth - 50 + window.innerWidth - evt.clientX : 0) + "px", top: evt.clientY + 10 + "px", width: boxWidth + "px" });
    }

    function profilepopupfadeout(evt) {
        var itemId = this.getAttribute("id").split("_")[1];
        
        var popupBox = $("#profile_" + itemId).hide();
    }
    $(".profilehoverpoint").hoverIntent({timeout: 0, interval: 500, over: profilepopupfadein, out: profilepopupfadeout});

    var profile_avatar = $('#profile_avatar');
    if(profile_avatar) {
        profile_avatar.bind('mouseenter', function() {
            $('#avatar_replace').css('display', 'block');
        }).bind('mouseleave', function() {
            $('#avatar_replace').css('display', 'none');
        });
    }
    var ymap = document.getElementById('ymap');
    if(ymap) {
        var map = new YMap(ymap);
        // Add map type control  
        map.addTypeControl();  
        // Add map zoom (long) control  
        map.addZoomLong();  
        // Add the Pan Control  
        map.addPanControl();
        for(var i = 0; i < _geo.length; ++i) {
            var g = _geo[i];
            var yPoint = new YGeoPoint(g[0], g[1]);
            // Display the map centered on a geocoded location
            map.drawZoomAndCenter(yPoint, 12);
            // Create a new marker for an address
            var myMarker = new YMarker(yPoint);
            // Create some content to go inside the SmartWindow
            var myMarkerContent = g[2];
            // When the marker is clicked, show the SmartWindow
            YEvent.Capture(myMarker, EventsList.MouseClick, function() {
                myMarker.openSmartWindow(myMarkerContent); 
            });
            // Put the marker on the map
            map.addOverlay(myMarker);
            var pageLink = document.getElementById('loc_' + i);
            if(pageLink) {
                pageLink.onclick = function() {
                    var geoIndex = parseInt(this.id.replace('loc_', ''), 10);
                    var g = _geo[geoIndex];
                    var yPoint = new YGeoPoint(g[0], g[1]);
                    map.drawZoomAndCenter(yPoint, 12);
                };
            }
        }
    }
});
