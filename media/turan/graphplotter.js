/**
 * Class for handeling graph plotting of pulse data.
 * Still needs loads of work and is only a cut/paste from template for now
 */
var plot;
var GraphPlotter = {
    choiceContainer: null,

    findMinMaxAvg: function (datasets, from, to) {
        var avgs = {};
        for (key in datasets) {
            var avg = { start: null, end: null, sum: 0, num: 0, avg: null, min: null, max: null, incline: null, decline: null, length: null };
            var lastAltitude = null;
            var label = datasets[key].label;
            for (l in datasets[key].data) {
                var pos = datasets[key].data[l][0];
                if (from != null && (pos >= from && pos <= to)) {
                    if (avg.start == null)
                        avg.start = pos;
                    avg.end = pos;

                    var value = datasets[key].data[l][1];
                    if (avg.min == null)
                        avg.min = value;
                    else
                        avg.min = Math.min(avg.min, value);

                    if (avg.max == null)
                        avg.max = value;
                    else
                        avg.max = Math.max(avg.max, value);

                    avg.sum += value;
                    avg.num++;

                    if (key == "altitude") {
                        if (avg.incline == null) 
                            avg.incline = 0;
                        if (avg.decline == null) 
                            avg.decline = 0;

                        var altitude = datasets[key].data[l][1];
                        if (lastAltitude != null) {
                            if (altitude > lastAltitude) {
                                avg.incline += altitude - lastAltitude;
                            } else if (altitude < lastAltitude) {
                                avg.decline += lastAltitude - altitude;
                            }
                        }
                        lastAltitude = altitude;
                    }
                }
            }
            if (avg.num > 0) {
                avg.avg = avg.sum / avg.num;
                avg.label = datasets[key].label;
                avgs[key] = avg;
            }
        }
        return avgs;
    },
    plotAccordingToChoices: function(ranges, maxhr) {
        data = [];
        var min = null;
        var max = null;
        if (maxhr == undefined)
            maxhr = 0;
        var xaxisattrs = { 
                tickDecimals: 0,
        };
        if (ranges.xaxis != undefined) {
            min = ranges.xaxis.from;
            max = ranges.xaxis.to;
            xaxisattrs.min = min;
            xaxisattrs.max = max;
        }
        $("#choices").find("input:checked").each(function () {
            var key = $(this).attr("name");
            if (key && datasets[key])
                data.push(datasets[key]);
        });

        if (data.length > 0) {
            plot = $.plot($("#tripdiv"), data, {
                yaxes: [{ min: 0 }, { min: 80 }],
                xaxis: xaxisattrs,
                legend: { container: $("#tripdiv_legend") },
                grid: { 
                    hoverable: true, 
                    clickable: true,
                },
                selection: { mode: "x" }
            });
        }

        avgs = this.findMinMaxAvg(datasets, min, max);
        var avglist = $("#averages ul").empty();

        // Only show if we've selected an area
        if (min != null) {
            var text = "";
            for (k in avgs) {
                text += "<li style=\"margin-left: 30px; float:left\" class=\"" + k + "\"><span class=\"label\">" + (k != "altitude" ? avgs[k].label : "Ascent/Descent") + ": </span>";
                if (k != "altitude") {
                    text += Math.round(avgs[k].min*10)/10 + "/" + Math.round(avgs[k].max*10)/10 + "/" + Math.round(avgs[k].avg*10)/10;
                }
                else {
                    text += Math.round(avgs[k].incline*10)/10 + "/" + Math.round(avgs[k].decline*10)/10;
                }
                text += "</li>";
            }
            text += "<li style=\"margin-left: 30px; float:left\" class=\"distance\"><span class=\"label\">Distance: </span>" + Math.round((avgs['speed'].end - avgs['speed'].start) * 10)/10 + "</span></li>";
            avglist.append(text);

            $("#averages h4").show();
        }
        else {
            $("#averages h4").hide();
        }

    },
    showTooltip: function (x, y, contents) {
        $('<div id="tooltip">' + contents + '</div>').css( {
            position: 'absolute',
            display: 'none',
            top: y + 5,
            left: x + 5,
            border: '1px solid #fdd',
            padding: '2px',
            'background-color': '#fee',
            opacity: 0.80
        }).appendTo("body").fadeIn(200);
    },
    init: function(datasets) {
        this.choiceContainer = $("#choices");
        var that = this;
        $.each(datasets, function(key, val) {
            that.choiceContainer.append('<br/><input type="checkbox" name="' + key +
                '" checked="checked" id="chk_' + key + '"><label for="chk_' + key + 
                '">' + val.label + '</label></input>');
        });
        this.choiceContainer.append('<br /><input type="reset" value="Reset zoom" />');
        this.choiceContainer.find("input").bind("click", function(evt) {
                that.plotAccordingToChoices({}); 
        });
        this.plotAccordingToChoices({});
        var previousPoint = null;
        $("#tripdiv").bind("plothover", function (event, pos, item) {
            var y = 0;
            if (pos.y)
                y = pos.y;
            else
                y = pos.y2;

            if (item) {
                if (previousPoint != item.datapoint) {
                    previousPoint = item.datapoint;
                    
                    $("#tooltip").remove();
                    var x = item.datapoint[0].toFixed(2),
                        y = item.datapoint[1].toFixed(2);
                    
                    that.showTooltip(item.pageX, item.pageY,
                    item.series.label + " at " + x + " is " + y);
                }
            }
            else {
                $("#tooltip").remove();
                previousPoint = null;            
            }
        });

        $("#tripdiv").bind("plotclick", function (event, pos, item) {
            if (item) {
                $("#clickdata").text("You clicked point " + item.dataIndex + " in " + item.series.label + ".");
                plot.highlight(item.series, item.datapoint);
            }
        });


        $("#tripdiv").bind("plotselected", function (event, ranges) {
            that.plotAccordingToChoices(ranges);
        });
    }
};

