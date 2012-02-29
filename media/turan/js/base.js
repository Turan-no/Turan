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
    cadence: function(val, axis) {
        return (val).toFixed(axis.tickDecimals) + ' RPM';
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
    var profile_avatar = $('#profile_avatar');
    if(profile_avatar) {
        profile_avatar.bind('mouseenter', function() {
            $('#avatar_replace').css('display', 'block');
        }).bind('mouseleave', function() {
            $('#avatar_replace').css('display', 'none');
        });
    }
});
$(function() { // Stuff for for search input field
	$('#listSearch').bind("focus", function (evt) {
		if ($(this).val() == $(this).data("text")) {
			$(this).data("text", $(this).val());
			$(this).val("");
            $(this).animate({ width: '90px' }, 250);
		}
	});
	$('#listSearch').bind("blur", function (evt) {
		if ($(this).val().length == 0)
			$(this).val($(this).data("text"));
            $(this).animate({ width: '60px' }, 250);
	});
	$('#listSearch').data("text", $('#listSearch').val());
	$('#listSearch').attr("id", "listSearch-" + Math.random());

});
$(function() { // Scroller thingymagic
    // fix sub nav on scroll
    var $win = $(window)
      , $nav = $('.sortbar')
      , navTop = $('.sortbar').length && $('.sortbar').offset().top - 40
      , isFixed = 0

    processScroll()

    $win.on('scroll', processScroll)

    function processScroll() {
      var i, scrollTop = $win.scrollTop()
      if (scrollTop >= navTop && !isFixed) {
        isFixed = 1
        $nav.addClass('sortbar-fixed')

        /*
        var $headLength = $(".fullsize thead th").length;
        $(".fullsize tbody tr:last td").each(function(index) {
            $thisWidth = $(".fullsize thead th:eq(" + index + ")").width();
            console.log($thisWidth);
            $(this).width( $thisWidth);
        });*/
      } else if (scrollTop <= navTop && isFixed) {
        isFixed = 0
        $nav.removeClass('sortbar-fixed')
      }
    }


});
// Declare namespace
var Turan = {};
