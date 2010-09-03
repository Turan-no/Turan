/**
 * Class for handeling graph plotting of pulse data.
 * Still needs loads of work and is only a cut/paste from template for now
 */
var plot;
var GraphPlotter = {
    choiceContainer: null,
    datasets: null,
    backendUrl: null,
    max_hr: 200,
    formatters: {
            speed: function(val, axis) {
                return (val).toFixed(axis.tickDecimals) + ' km/h';
            },
            altitude: function(val, axis) {
                return (val).toFixed(axis.tickDecimals) + ' m';
            },
            length: function(val, axis) {
                return (val).toFixed(axis.tickDecimals) + ' km';
            },
            power: function(val, axis) {
                return (val).toFixed(axis.tickDecimals) + ' W';
            },
            hr: function(val, axis) {
                return (val).toFixed(axis.tickDecimals) + ' BPM';
            },
            time: function(val, axis) {
                var hours = Math.floor(val / 60);
                var minutes = val;

                if (hours)
                        return hours + 'h&nbsp;' + minutes + 'm';
                return minutes + 'm';
            }

    },

    plotAccordingToChoices: function(ranges) {
        data = [];
        var that = this;
        var minIndex = null;
        var maxIndex = null;
        var min = null;
        var max = null;
        var xaxisattrs = { 
            tickDecimals: 0,
            tickFormatter: this.xaxisformatter
        };
        if (ranges.xaxis != undefined) {
            var xaxe = plot.getXAxes()[0];
            min = ranges.xaxis.from;
            max = ranges.xaxis.to;
            xaxisattrs.min = min;
            xaxisattrs.max = max;

            for (dataset in this.datasets) { 

                series = this.datasets[dataset]['data']

                for (k in series) {
                    if (min >= series[k][0])
                        minIndex = k;
                    if (max <= series[k][0]) {
                        maxIndex = k;
                        break;
                    }
                }
                break;
            }
        }
        $("#choices").find("input:checked").each(function () {
            var key = $(this).attr("name");
            if (key && that.datasets[key])
                data.push(that.datasets[key]);
        });

        if (data.length > 0) {
            plot = $.plot($("#tripdiv"), data, {
                yaxes: [
                    { tickFormatter: this.formatters['speed']},
                    { position: "right", min: 80, max: this.max_hr, tickFormatter: this.formatters['hr'] }, 
                    { position: "right", tickFormatter: this.formatters['power']},
                    { tickFormatter: this.formatters['altitude']}
                    ],
                xaxis: xaxisattrs,
                legend: { 
                    container: $("#tripdiv_legend"),
                    noColumns: 10
                },
                grid: { 
                    hoverable: true, 
                    clickable: true,
                },
                selection: { mode: "x" }
            });
        }

        if (minIndex != null && maxIndex != null) {
            if (typeof(Mapper) != "undefined")
                Mapper.loadGeoJSON(minIndex, maxIndex);
            $.getJSON(this.backendUrl, { start: minIndex, stop: maxIndex }, function (avgs) {
                var items = $("#averages ul .data");
                $("#averages h4").removeClass("hidden");

                $.each(items, function (i, elem) {
                    var classlist = elem.className.split(" ");
                    for (k in classlist) {
                        if (classlist[k] in avgs) {
                            var key = classlist[k];
                            var e = $(elem);
                            var val = Math.round(avgs[key] * 10) / 10;
                            e.text(val);
                            e.parents(".hidden").removeClass("hidden");
                        }
                    }
                });
            });
        }
        else {
            if (typeof(Mapper) != "undefined")
                Mapper.loadGeoJSON(0, 0);
            $("#averages ul li").addClass("hidden");
            $("#averages h4").addClass("hidden");
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
    init: function(args) {
        this.datasets = args.datasets;
        var backendUrl = args.backendUrl;
        this.max_hr = args.max_hr;
        this.xaxisformatter = this.formatters[args.xaxisformatter];

        var that = this;
        this.backendUrl = backendUrl;
        this.choiceContainer = $("#choices");

        $.each(this.datasets, function(key, val) {
            var checked = "checked = checked";
            if (key == 'cadence') 
                checked = ''

            that.choiceContainer.append('<input type="checkbox" name="' + key +
                '" ' + checked + ' id="chk_' + key + '"><label for="chk_' + key + 
                '">' + val.label + '</label></input>');
        });
        this.choiceContainer.append('<input type="reset" value="Reset zoom" />');
        this.choiceContainer.find("input").bind("click", function(evt) {
                that.plotAccordingToChoices({}); 
        });
        this.plotAccordingToChoices({});
        var previousPoint = null;
        $("#tripdiv").bind("plothover", function (event, pos, item) {
            if (item) {
            /* FIXME
                // Move marker to current pos
                if (typeof(Mapper) != "undefined") {
                    var x = route_points[item.dataIndex].x;
                    var y = route_points[item.dataIndex].y;
                    Mapper.updatePosMarker(x, y);
                }
            */

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

