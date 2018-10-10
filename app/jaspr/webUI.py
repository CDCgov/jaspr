#!/usr/bin/env python
# file webUI.py


import math
import numpy as np
import os
import logging
from flask import Flask, render_template
from werkzeug import secure_filename
from pandas import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.glyphs import Line
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
from jaspr import app, UPLOAD_FOLDER, CURRENT_DATA_FILE

pinging = True
def pol():
    logging.warning("We can call into WebUI at least")
    return

def gather_data():
    """
    gather data from the excel file in the uploader directory
    """
    xlsx = pd.ExcelFile(os.path.join(UPLOAD_FOLDER, CURRENT_DATA_FILE))
    df = pd.read_excel(xlsx, 'Sheet1',na_filter=False)
    return df

def create_chart(df):
    """
    creating the results chart
    """
    # Create the figure: p and chart the data
    p = figure(x_axis_label='titer', y_axis_label='result',title='jaspr Data')
    p.circle(df['titer'], df['result'], size=10)

    #create a standard log curve and plot on chart for reference
    y = np.linspace(df['result'].min(),df['result'].max(), df.shape[0]*5)#add 5x the points of what we are plotting
    y = np.flip(y)
    x = list(map(lambda n: df['titer'].max()-math.log2(n)+df['titer'].min(), y))

    lsource = ColumnDataSource(dict(x=x, y=y))

    glyph = Line(x="x", y="y", line_color="#3aaf13", line_width=3, line_alpha=0.6)
    p.add_glyph(lsource, glyph)

    #modify the x-axis to be log 2
    #p.xaxis[0].ticker.base = 2
    #p.xaxis[0].formatter.ticker = p.xaxis[0].ticker

    return components(p)
    # Plot result by date

def create_table(df):
    """
    creating the data table
    """

    source = ColumnDataSource(df)

    bcols = [TableColumn(field=Ci, title=Ci) for Ci in df.columns] # bokeh columns
    for col in bcols:
        if col.field =="date":
            col.formatter = DateFormatter()
    data_table = DataTable(source=source, columns=bcols, height=580)

    # Plot result by date
    return components(widgetbox(data_table))

@app.route('/upload')
def upload_file():
   return render_template('upload.html')

@app.route("/settings")
def settings():
    """ render the settings page
    """
    return render_template('settings.html')

@app.route("/")
def main():
    """ render the main page
    """
    df = gather_data()
    g_script, g_div = create_chart(df)
    t_script, t_div = create_table(df)
    return render_template('main.html',graph_script=g_script, graph_div=g_div, table_script=t_script, table_div=t_div)
