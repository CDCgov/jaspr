rem this batch program gathers the bokeh js files from the version specified
set BOKEHVERSION=1.0.1
curl http://cdn.pydata.org/bokeh/release/bokeh-%BOKEHVERSION%.min.css > bokeh.min.css
curl http://cdn.pydata.org/bokeh/release/bokeh-tables-%BOKEHVERSION%.min.css > bokeh-tables.min.css
curl http://cdn.pydata.org/bokeh/release/bokeh-widgets-%BOKEHVERSION%.min.css > bokeh-widgets.min.css
