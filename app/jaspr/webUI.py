#!/usr/bin/env python
# file jaspr/webUI.py

from flask import render_template, request, session
from jaspr import app
from jaspr.model import JasprModel
from jaspr.charting import JasperCharts

"""Flask routes for browser based jaspr UI

"""


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
    jm = JasprModel()

    #TODO: I am just loading a default model for now
    jm.loadDefaultModel()
    session["config"]=jm.getConfigString()
    session["model"]=jm.getExperimentString()
    session.modified=True

    #TODO: wire up actual sample selection from left menu
    currentExperiment = jm.getExperimentNames()[0]
    sampleList = jm.getSampleNames(currentExperiment)
    selectedSample = sampleList[0]
    #TODO: wire up actual experiement selection from left menu
    experimentList = jm.getExperimentNames()

    jc = JasperCharts(jm)
    g_script, g_div = jc.create_chart(currentExperiment,selectedSample)
    t_script, t_div = jc.create_table(currentExperiment,selectedSample)

    return render_template('main.html',
        experimentList=experimentList,
        sampleList=sampleList,
        selectedSample=selectedSample,
        graph_script=g_script, graph_div=g_div,
        table_script=t_script, table_div=t_div)
