{% load i18n %}
{
        {% if speed%}
        "speed": {
            data: [{{ speed}}],
            label: "{% trans "Speed" %}",
            color: 0,
        },
        {% endif %}
        {% if hr%}
        "hr": {
            data: [{{ hr}} ],
            label: "{% trans "HR" %}",
            lines: { show: true, fill: 0.0 },
            yaxis: 2,
            constraints: [constraint0, constraint1, constraint2, constraint3, constraint4, constraint5],
        },
        {% endif %}
        {% if cadence%}
        "cadence": {
            data: [ {{ cadence}}],
            label: "{% trans "Cadence" %}",
            color: 1,
            },
        {% endif %}
        {% if altitude%}
        "altitude":{
            data: [ {{ altitude}}],
            label: "{% trans "Altitude" %}",
            lines: { show: true, fill: 0.3 },
            color: 3,
        },
        {% endif %}
        {% if power%}
        "power": {
            data: [ {{ power}}],
            label: "{% trans "Power" %}",
            points: { show: false } ,
            color: 5,
            yaxis: 3,
            },
        {% endif %}
        {% if poweravg30s%}
        "poweravg30s": {
            data: [ {{ poweravg30s}}],
            label: "{% trans "Power Avg30" %}",
            points: { show: false } ,
            color: 4,
            yaxis: 3,
            },
        {% endif %}
}
