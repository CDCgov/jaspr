#!/usr/bin/env python
from flask import Flask, render_template,request,session,jsonify
from jaspr import app
from jaspr.model import JasprModel
from jaspr.charting import JasperCharts
from jaspr.sessionController import SessionController

@app.route('/upload')
def upload_file():
   return render_template('upload.html')

@app.route("/settings")
def settings():
    """ render the settings page
    """
    return render_template('settings.html')

@app.route("/")
def mainPage():
    """ render the main page
    """
    sc = SessionController()
    jm = sc.getModel()
    #TODO: wire up actual experiement selection from left menu
    experimentList = jm.getExperimentNames()
    currentExperiment = jm.getUIStateValue("currentExperiment")

    #TODO: wire up actual sample selection from left menu
    sampleList = jm.getSampleNames(currentExperiment)
    selectedSample = jm.getUIStateValue("currentSample")

    jc = JasperCharts(jm)
    g_script, g_div = jc.create_chart(currentExperiment,selectedSample)
    t_script, t_div = jc.create_table(currentExperiment,selectedSample)

    return render_template('main.html',
        experimentList=experimentList,
        sampleList=sampleList,
        selectedSample=selectedSample,
        graph_script=g_script, graph_div=g_div,
        table_script=t_script, table_div=t_div)

@app.route("/graphHTML", methods=["GET"])
def graphHTML():
    sc = SessionController()
    jm = sc.getModel()

    currentExperiment = jm.getUIStateValue("currentExperiment")
    selectedSample = jm.getUIStateValue("currentSample")

    jc = JasperCharts(jm)
    g_script, g_div = jc.create_chart(currentExperiment,selectedSample)
    t_script, t_div = jc.create_table(currentExperiment,selectedSample)

#TODO pull this into the controller
    retVal = {}
    retVal["g_script"] = g_script
    retVal["g_div"] = g_div
    retVal["t_script"] = t_script
    retVal["t_div"] = t_div
    return jsonify(retVal)
