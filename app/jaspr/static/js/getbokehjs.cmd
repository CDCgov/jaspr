rem this batch program gathecrs the bokeh js files from the version specified
set BOKEHVERSION=1.0.1
curl http://cdn.pydata.org/bokeh/release/bokeh-%BOKEHVERSION%.min.js > bokeh.min.js
curl http://cdn.pydata.org/bokeh/release/bokeh-tables-%BOKEHVERSION%.min.js > bokeh-tables.min.js
curl http://cdn.pydata.org/bokeh/release/bokeh-widgets-%BOKEHVERSION%.min.js > bokeh-widgets.min.js
curl http://cdn.pydata.org/bokeh/release/bokeh-api-%BOKEHVERSION%.min.js > bokeh-api.min.js
