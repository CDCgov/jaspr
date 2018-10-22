#!/usr/bin/env python
# file charting.py

"""
This module manages the charting functionality for Jaspr.  It's main object
is a class that contains the current data model

Todo:
    * None at this time

"""
import math
import numpy as np
import os
import logging

from pandas import pandas as pd
from numpy import arange,array,ones,linalg


from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.glyphs import Line
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn, Div

from jaspr.model import JasprModel

class JasperCharts(object):
    """Jaspr Charts class that builds chart artifacts based upon a data model

    """

    def __init__(self, model):
        self._model = model

    def createDataFrame(self, experimentKey, sampleKey):
        """Create a dataframe for a given sample using the current model

            Args:
                experimentKey: the experiement where the sample resides
                sampleKey: the sampleKey

            Returns:
                a dataframe object

        """
        (xSeries,ySeries) = self._model.getSampleDataSeries(
                          experimentKey=experimentKey,
                          sampleKey=sampleKey)

        (xLabel, yLabel) = self._model.getExperimentLabels(
                           experimentKey=experimentKey)

        chartIndex = pd.RangeIndex(11)

        return pd.DataFrame(np.array([xSeries,ySeries]).T,
                            index=chartIndex,
                            columns = [xLabel,yLabel])


    def create_chart(self, experimentKey, sampleKey):
        """Create HTML and Javascript components that will display a chart
           for a given sample using the current model

            Args:
                experimentKey: the experiement where the sample resides
                sampleKey: the sampleKey

            Returns:
                HTML string and JavaScript string

        """
        (xLabel,yLabel) = self._model.getExperimentLabels(experimentKey)

        df = self.createDataFrame(experimentKey,sampleKey)

        # Create the figure: p and chart the data
        p = figure(x_axis_label=xLabel, y_axis_label=yLabel ,
        title=experimentKey + " : " + sampleKey)
        p.circle(df[xLabel], df[yLabel], size=10)

        # regression line
        (slope,intercept) = np.polyfit(df[xLabel],df[yLabel],1)
        x = np.linspace(df[xLabel].min(),df[xLabel].max(), df.shape[0])
        y = list(map(lambda x: intercept + slope*x, x))

        lsource = ColumnDataSource(dict(x=x, y=y))

        glyph = Line(x="x", y="y", line_color="#3aaf13", line_width=3, line_alpha=0.6)
        p.add_glyph(lsource, glyph)

        return components(p)

    def create_table(self, experimentKey, sampleKey):
        """Create HTML and Javascript components that will display a table
           for a given sample using the current model

            Args:
                experimentKey: the experiement where the sample resides
                sampleKey: the sampleKey

            Returns:
                HTML string and JavaScript string

        """
        df = self.createDataFrame(experimentKey,sampleKey)
        source = ColumnDataSource(df)

        bcols = [TableColumn(field=Ci, title=Ci) for Ci in df.columns] # bokeh columns
        #Todo: pull out to its own function and make more robust
        #change the column format to date for any field called "date"
        for col in bcols:
            if col.field =="date":
                col.formatter = DateFormatter()
        data_table = DataTable(source=source, columns=bcols, height=580)
        title=Div(text="<strong>" + experimentKey + " : " + sampleKey + "</strong>")

        return components(widgetbox(title, data_table))
