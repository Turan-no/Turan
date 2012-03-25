/**
 * Class for handling graph plotting of pulse data.
 */
var plot;
var GraphPlotter = {
    choiceContainer: null,
    datasets: null,
    backendUrl: null,
    max_hr: 200,
    markings: [],
    graphlabels: [],
    ranges: {},

    setRange: function(range) {
        this.ranges = range;
    },
    plot: function() {
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
        if (this.ranges.xaxis != undefined) {
            min = this.ranges.xaxis.from;
            max = this.ranges.xaxis.to;
            xaxisattrs.min = min;
            xaxisattrs.max = max;

            for (dataset in this.datasets) { 

                series = this.datasets[dataset]['data']

                for (k in series) {
                    if (min >= series[k][0]) {
                        minIndex = k;
                    }
                    if (max <= series[k][0]) {
                        maxIndex = k;
                        break;
                    }
                }
                break;
            }
        }
        $("#choices>button[checked=checked]").each(function () {
            var key = $(this).attr("name");
            if (key && that.datasets[key]) {
                if (key == 'hr') {
                    //that.datasets[key]['constraints'] = that.hrconstraints;
                  that.datasets[key]['threshold']= that.newhrconstraints;
                }
                else if (key == 'altitude') {
                    //that.datasets[key]['constraints'] = segmentconstraints;
                }
                if (key != 'lon' && key != 'lat') { // lon and lat doesn't go in the graph
                    data.push(that.datasets[key]);
                }
            }
        });

        if (data.length > 0) {
            plot = $.plot($("#exercisegraph"), data, {
                series: {
                    lines: {
                        lineWidth: 2, // less cluttere
                    },
                    shadowSize: 3 //drawing is faster without shadoes
                },
                yaxes: [
                    { tickFormatter: axisformatters['speed'] },
                    { position: "right", min: 80, max: this.max_hr, tickFormatter: axisformatters['hr'] }, 
                    { position: "right", tickFormatter: axisformatters['power']},
                    { tickFormatter: axisformatters['altitude']} ,
                    { tickFormatter: axisformatters['temp']},
                    { tickFormatter: axisformatters['cadence']}
                    ],
                xaxis: xaxisattrs,
                legend: { 
                    labelFormatter: function(label, series) {
                        // series is the series object for the label
                        return label;
                    },
                    position: 'se',
                    noColumns: 15
                },
                grid: { 
                    hoverable: true, 
                    clickable: true,
                    backgroundColor: { colors: ["#fff", "#eee"] },
                    markings: this.markings,
                    markingsLineWidth: 2,
                },
                crosshair: { mode: "x" },
                selection: { mode: "x" }
            });
        }

        if (minIndex != null && maxIndex != null) { // Means ranges were set (a selection)

            // Show the progress bar for loading selection info
            $('.progressbarcontainer').removeClass('hide');
            $('.progress .bar').attr('style', 'width: 70%;');

            // Show segment add button
            var segment_link = $("#segment_add");
            segment_link.attr('href' , segment_link.attr('href')+ '&start=' + minIndex + '&stop=' + maxIndex).removeClass('hide');

            // Save selection range in URL
            window.location.hash = 'graph-zoom-' + min + '-' + max;

            // Get the data for the selection from backend
            $.getJSON(this.backendUrl, { start: minIndex, stop: maxIndex }, function (avgs) {
                // Update progrssbar
                var items = $("#averages ul .data");
                $("#averages h4").removeClass("hide");

                $('.progress .bar').attr('style', 'width: 100%;');
                $('.progressbarcontainer').addClass('hide');
                $.each(items, function (i, elem) {
                    var classlist = elem.className.split(" ");
                    for (k in classlist) {
                        if (classlist[k] in avgs) {
                            var key = classlist[k];
                            var e = $(elem);
                            var val = avgs[key];
                            if (val) {
                                if (typeof(val) == 'number') {
                                    val = Math.round(val * 10) / 10;
                                }
                                e.text(val);
                                e.parents(".hide").removeClass("hide");
                                e.attr('title', key.replace(/_/g, ' '))
                                e.parents('li').attr('title', key.replace(/_/g, ' '))
                            }
                        }
                    }
                });
            });
            if (typeof(Mapper) != "undefined")
                Mapper.loadGeoJSON(minIndex, maxIndex);

        }
        else {
            if (typeof(Mapper) != "undefined")
                Mapper.loadGeoJSON(0, 0);
            $("#averages ul li").addClass("hide");
            $("#averages h4").addClass("hide");
        }

        this.drawGraphText();
    },
    updateLegend: function(pos) {
        this.updateLegendTimeout = null;
       // var pos = this.latestPosition; 
        var axes = plot.getAxes(); 
        if (pos.x < axes.xaxis.min || pos.x > axes.xaxis.max || 
            pos.y < axes.yaxis.min || pos.y > axes.yaxis.max) 
            return; 

        var i, j, dataset = plot.getData(); 
        for (i = 0; i < dataset.length; ++i) { 
            var series = dataset[i]; 

            // find the nearest points, x-wise 
            for (j = 0; j < series.data.length; ++j) 
                if (series.data[j]) {
                    if (series.data[j][0] > pos.x) 
                        break;
                }

            // now interpolate 
            var y, p1 = series.data[j - 1], p2 = series.data[j];


            if (p1 == null) 
                y = p2[1]; 
            else if (p2 == null) 
                y = p1[1]; 
            else 
                y = p1[1] + (p2[1] - p1[1]) * (pos.x - p1[0]) / (p2[0] - p1[0]); 

            this.legends.eq(i).text(series.label.replace(/=.*/, "= " + y.toFixed(2))); 
        } 
    },
    showTooltip: function (x, y, contents) {
        $('<div class="tooltip" id="flotTip">' + contents + '</div>').css( {
            position: 'absolute',
            display: 'none',
            top: y + 5,
            left: x + 5,
            padding: '10px',
            opacity: 0.9
        }).appendTo("body").delay(200).fadeIn(200);
    },
    addGraphText: function(x, text) {
        this.graphlabels.push([x,text] );
    },
    drawGraphText: function() {
        var ymax = plot.getAxes().yaxis.max;
        for (key in this.graphlabels) {
            var o= plot.pointOffset({ x: this.graphlabels[key][0], y: ymax});
            var placeholder = plot.getPlaceholder()
            placeholder.append('<div class="graphlabel" style="position:absolute;left:' + (o.left) + 'px;top:' + o.top + 'px;">' + this.graphlabels[key][1] + '</div>');
        }
    },
    init: function(args) {
        this.datasets = args.datasets;
        var backendUrl = args.backendUrl;
        this.max_hr = args.max_hr;
        this.markings = args.markings;
        this.xaxisformatter = axisformatters[args.xaxisformatter];
        this.posFeature = null;
        this.fullscreen = false;
        function evaluate(y,threshold) { 
            return y < threshold;
        }
        this.hrconstraints = [{
                threshold: this.max_hr*0.6,
                color: colors[0],
                evaluate : evaluate
            },
            {
                threshold: this.max_hr*0.72,
                color: colors[1],
                evaluate : evaluate
            },
            {
                threshold: this.max_hr*0.82,
                color: colors[2],
                evaluate : evaluate
            },
            {
                threshold: this.max_hr*0.87,
                color: colors[3],
                evaluate : evaluate
            },
            {
                threshold: this.max_hr*0.92,
                color: colors[4],
                evaluate : evaluate
            },
            {
                threshold: this.max_hr*0.97,
                color: colors[5],
                evaluate : evaluate
        }]

        this.newhrconstraints = [{
                below: this.max_hr*0.6,
                color: colors[0]
            },
            {
                below: this.max_hr*0.72,
                color: colors[1]
            },
            {
                below: this.max_hr*0.82,
                color: colors[2]
            },
            {
                below: this.max_hr*0.87,
                color: colors[3]
            },
            {
                below: this.max_hr*0.92,
                color: colors[4]
            },
            {
                below: this.max_hr*0.97,
                color: colors[5]
        }]

        var that = this;
        this.backendUrl = backendUrl;
        this.choiceContainer = $("#choices");

        $.each(this.datasets, function(key, val) {
            var checked = 'checked=checked';
            if (key == 'cadence') 
                checked = ''
            if (key == 'temp') 
                checked = ''
            if (key == 'power') 
                checked = ''
            var btn_class = "active";
            if (checked == '')
                btn_class = ''

            if (key != 'lon' && key != 'lat') {

                that.choiceContainer.append('<button class="btn ' + btn_class + '" name="' + key + '" ' + checked + ' id="chk_' + key + '">' + val.label + '</button>');
            }
        });
        $("#reset_zoom").bind("click", function(evt) {
            evt.preventDefault();
            $("#flotTip").remove(); // tooltips messes up pos
            that.setRange({});
            that.plot(); 
            $('#reset_zoom').toggleClass('hide');
            $('#segment_add').toggleClass('hide');
        });
        $(window).bind("keyup", function(evt) { if (evt.keyCode == 70) { $('#enlarge').click() } });
        $("#enlarge").bind("click", function(evt) {
            evt.preventDefault();
            $("#flotTip").remove(); // tooltips messes up pos
            // Press escape to leave fullscreen
            $(window).bind("keyup", function(evt) { if (evt.keyCode == 27) { $('#enlarge').click() } });
            if(!that.fullscreen) {
                //$("#scrollhack").css("overflow", "scroll");
                //$("#exercisegraph").width( $("#exercisegraph").width()*4);
                $("#exercisegraph").appendTo('body');
                $("#exercisegraph").css("position", "absolute"); // Somehow needed, even though it's set in the css
                $("#exercisegraph").addClass('exercisegraphoverlay');
                $("#exercisegraph").removeClass('exercisegraph');
                $("#exercisegraph").css("overflow", "hidden");


                $("#averages").addClass('extraoverlay');
                $("#averages").appendTo('body');
                that.fullscreen = true;
            }
            else {
                $("#exercisegraph").removeClass('exercisegraphoverlay');
                $("#exercisegraph").addClass('exercisegraph');
                $("#exercisegraph").css("position", "relative"); // Somehow needed, even though it's set in the css
                $("#exercisegraph").appendTo($('#graphcontainer'));

                $("#averages").removeClass('extraoverlay');
                $("#averages").appendTo($('#graphcontainer'));
                that.fullscreen = false;
            }
        });
        this.choiceContainer.find("button").bind("click", function(evt) {
                evt.stopPropagation(); // Stop bootstrap event from firing
                $(this).toggleClass('active'); // Handle bootstrap event ourselves before we plot so class is set
                $(this).attr("checked", !$(this).attr("checked"));
                that.plot(); 
        });
        $('.legendColorBox > div').each(function(i){
            $(this).clone().prependTo(that.choiceContainer.find("li").eq(i));
        });

        this.legends = $(".legendLabel"); 
        this.legends.each(function () { 
            // fix the widths so they don't jump around
            $(this).css('width', $(this).width());
        });

        var previousPoint = null;
        this.updateLegendTimeout = null;
        this.latestPosition = null;
        $("#exercisegraph").bind("plothover", function (event, pos, item) {
            that.latestPosition = pos; 
  //          if (!that.updateLegendTimeout) that.updateLegendTimeout = setTimeout(that.updateLegend, 50); 
            //that.updateLegend(pos);

            $("#flotTip").remove();
            var axes = plot.getAxes(); 
            // Just retrn if we're hovering around outside the graph area
            if (pos.x < axes.xaxis.min || pos.x > axes.xaxis.max || 
                pos.y < axes.yaxis.min || pos.y > axes.yaxis.max) 
                return; 

            var posIndex = 0;
            for (serieskey in that.datasets) { // Find first and best series that we got
                var series = that.datasets[serieskey]['data'];
                if (series == undefined) {
                    continue; // lon and lat dataseries does not have data object
                }
                for (key in series) {
                    if (series[key][0] >= pos.x) {
                        var posIndex = key;
                        break;
                    }
                }
                break;
            }
            if (posIndex <= 0)  // No index found
                return;

            // Move marker to current pos
            if (typeof(Mapper) != "undefined" && Mapper.map != null && Mapper.posLayer != undefined) {
            
                var route_lon = that.datasets['lon'];
                var route_lat = that.datasets['lat'];
                if (route_lon.length >= posIndex) {
                    var x = route_lon[posIndex];
                    var y = route_lat[posIndex];
                    if (!this.posFeature) {
                        this.posFeature = Mapper.createFeature(Mapper.posLayer, x, y, 0);
                    }
                    // Mapper.updatePosMarker(x, y);
                    Mapper.moveFeature(this.posFeature, x, y, 0); // Hardcoded to 0 degrees
                }
            }
                
            var x = pos.x;
            var highlightedseries = null;
            if (item) 
                highlightedseries = item.series.label;
            
            var tooltipHtml = '<h3>'+ that.xaxisformatter(x, plot.getAxes().xaxis) + '</h3><ul class="iconlist">';
            for (skey in that.datasets) {
                if (skey == 'lon' || skey == 'lat') 
                    continue;
                var series = that.datasets[skey];
                var label = series['label'];
                var tickFormatter = axisformatters[skey];
                if (skey == 'poweravg30s')
                    tickFormatter = axisformatters['power'];
                var val = series['data'][posIndex][1]; // Must fetch this from datasets rather thatn the graph data itself because of multiple treshold splits up the indexes
                if(tickFormatter != undefined) 
                    val = tickFormatter(val, plot.getAxes().xaxis);
                var color = plot.getOptions().colors[series['color']];
                if(label == highlightedseries) // Highlight if item selected
                    skey += ' label label-important'
                tooltipHtml += '<li class="'+skey+'"><span class="old-label">' + label + '</span> ' + val + '</li>';
            }
            tooltipHtml += '</ul>';
            that.showTooltip(pos.pageX, pos.pageY, tooltipHtml);
            

        });
        /*$("#exercisegraph").bind("plotclick", function (event, pos, item) {
            if (item) {
                plot.highlight(item.series, item.datapoint);
            }
            // reset zoom on click
            that.setRange({});
            that.plot(); 
        });*/


        $("#exercisegraph").bind("plotselected", function (event, ranges) {
            $('#tab-graph-link').click();
            $('#reset_zoom.hide').toggleClass('hide');
            that.setRange(ranges);
            that.plot();
        });
    }
};

