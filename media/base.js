/* Colors in use for lots of zone related stuffs */
var colors = ["rgb(240,240,240)", "rgb(204,204,204)", "rgb(51,102,255)", "rgb(102,204,0)", 
        "rgb(255,153,0)", "rgb(255,0,0)", "rgb(166,0,0)", "rgb(119,0,119)"];


/* conver rgb colors to hex, openlayers uses those */
function colorToHex(color) {
    if (color.substr(0, 1) === '#') {
        return color;
    }
    var digits = /(.*?)rgb\((\d+), ?(\d+), ?(\d+)\)/.exec(color);
    
    var red = parseInt(digits[2]);
    var green = parseInt(digits[3]);
    var blue = parseInt(digits[4]);
    
    var rgb = blue | (green << 8) | (red << 16);
    return digits[1] + '#' + rgb.toString(16);
};

function durationFormatter(time, axis) {
    //var time = date_object.getTime();

    var days    = parseInt((time / (60*60*24)));
    var hours   = parseInt((time % (60*60*24)) / (60*60));
    var minutes = parseInt((time % (60*60)) / (60));

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
        return "0 m" 
    }
    if (result.length == 1) {
        return result[0];
    }
    return result.slice(0, result.length-1).join(", ") + " " + result[result.length-1];
}
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
        var boxWidth = 350;
        var boxHeight = parseInt(popupBox.css("height").replace("px","")) + 50;
        popupBox.css({ left: (evt.clientX > window.innerWidth - boxWidth ? window.innerWidth - boxWidth : evt.clientX) + "px", top: (evt.clientY > window.innerHeight - boxHeight ? window.innerHeight - boxHeight : evt.clientY) + "px", width: boxWidth-50 + "px" });
    }

    function popupfadeout(evt) {
        var itemId = this.getAttribute("id").split("_")[1];
        
        var popupBox = $("#mouseover_" + itemId).hide();
    }

    $(".hoverpoint").hoverIntent({timeout: 0, interval: 900, over: popupfadein, out: popupfadeout});

    function profilepopupfadein(evt) {
        var itemId = this.getAttribute("id").split("_")[1];
        
        var popupBox = $("#profile_" + itemId).show();
        var boxWidth = 300;
        popupBox.css({ left: evt.clientX + (evt.clientX < boxWidth ? boxWidth : 0) + "px", top: evt.clientY + "px", width: boxWidth + "px" });
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
