/**
 * Script for displaying overlay notifying the user that he/she is running an old version of IE.
 * When the overlay gets closed, it won't show for another day, or when the cookie is deleted.
 * The time to live for the cookie can be changed by changing the "ttl" var.
 *
 * Author: Mads Erik Forberg <mads@hardware.no>
 *
 */

var ttl = 1; // Counted in days.
var oldIE = (/MSIE [3-6]/.test(navigator.appVersion));

var displayPopup = function() {
    var root = document.body || document.documentElement;
    var container = document.createElement("div");
    var frag = document.createDocumentFragment();
    container.setAttribute("id", "ieOld");
    container.className = "ieOldStopper";

    var overlay = document.createElement("div");
    overlay.className = "overlay";

    var html = "<h2 class=\"header\">Du kj&oslash;rer utdatert Internet Explorer</h2>"
         + "<p>Dette er ikke en oppdatert nettleser, og kan negativt p&aring;virke din datamaskins sikkerhet og din surfing!</p>"
         + "<p>Vennligst oppgrader til Internet Explorer 7, eller bytt til en annen nettleser:</p>"
         + "<ul><li style=\"background: url(http://images.gfx.no/573/573312/40px-InternetExplorer7Logo-16x16.png) no-repeat; padding-left: 20px;\"><a href=\"http://url.hw.no/?py\">Oppgrader til IE7</a></li>"
         + "<li style=\"background: url(http://images.gfx.no/573/573314/firefox-16x16.png) no-repeat; padding-left: 20px;\"><a href=\"http://www.mozilla-europe.org/no/firefox/\">Firefox</a></li>"
         + "<li style=\"background: url(http://images.gfx.no/573/573315/opera-16x16.png) no-repeat; padding-left: 20px;\"><a href=\"http://www.opera.com/\">Opera</a></li></ul>";


    container.innerHTML = html;
    
    var close = document.createElement("a");
    close.setAttribute("href", "#");
    close.className = "close";
    close.appendChild(document.createTextNode("Lukk"));
    close.onclick = function(evt) {
        if (evt) {
            evt.preventDefault();
        }
        else {
            window.event.returnValue = false;
        }
        _removeElem(container);
        _removeElem(overlay);
    }
    container.appendChild(close);

    frag.appendChild(overlay);
    frag.appendChild(container);

    root.appendChild(frag);
    
    var containerStyles = {
        width: "500px",
        backgroundColor: "#fff",
        position: "absolute",
        zIndex: 200,
        marginLeft: "-250px",
        border: "3px solid #000",
        textAlign: "left",
        padding: "6px",
        left: "50%",
        top: "100px"
    };
    var overlayStyles = {
        backgroundColor: "#000",
        filter: "alpha(opacity = 70)",
        opacity: .7,
        height: root.clientHeight + "px",
        width: "100%",
        position: "absolute",
        zIndex: 100
    };

    for (var name in containerStyles) {
        container.style[name] = containerStyles[name];
    }
    for (var name in overlayStyles) {
        overlay.style[name] = overlayStyles[name];
    }
}

var _removeElem = function(elem) {
    elem.parentNode.removeChild(elem);
}

var _setCookie = function(name, value, ttl) {
    var exdate = new Date();
    exdate.setDate(exdate.getDate() + ttl);
    document.cookie = name + '=' + escape(value) + ((ttl == null) ? '' : ';expires=' + exdate.toGMTString());
}

var _getCookies = function() {
    var cookies = document.cookie.split(/\s?;\s?/g);
    for (var x = 0; x < cookies.length; x++) {
        var temp = cookies[x].split(/=/);
        cookies[temp[0]] = temp[1];
        delete cookies[x];
    }

    return cookies;
}

// Load it
window.onload = function() {
    if (oldIE === true) {
        var cookieName = 'shown_ie';
        var cookies = _getCookies();
        if (!cookies[cookieName]) {
            _setCookie('shown_ie', "true", ttl); 
            displayPopup();
            var container = document.getElementById("ieOld");
        }
    }
}
