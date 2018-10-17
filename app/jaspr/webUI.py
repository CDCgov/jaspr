#!/usr/bin/env python
from flask import Flask, render_template,request
from jaspr import app
from jaspr.Model import JasprModel
from jaspr.Charting import JasperCharts

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
#TODO: I Just mocked up one graph for now and check it in.
    jm = JasprModel()
    jm.loadDefaultSession()
    jc = JasperCharts(jm)
    sampleList = jm.getSampleNames("Anscombe")
    selectedSample = sampleList[0]

    #TODO: wire up actual sample selection from left
    g_script, g_div = jc.create_chart("Anscombe","Set I")
    t_script, t_div = jc.create_table("Anscombe","Set I")

    return render_template('main.html',
        sampleList=sampleList,selectedSample=selectedSample,
        graph_script=g_script, graph_div=g_div,
        table_script=t_script, table_div=t_div)
