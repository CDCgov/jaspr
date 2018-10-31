#!/usr/bin/env python
from flask import Flask, render_template,request,session,jsonify,redirect,make_response
from jaspr import app
from jaspr.model import JasprModel
from jaspr.charting import JasperCharts
from jaspr.sessionController import SessionController
from urllib.parse import unquote
import json

@app.route('/reset')
def resetUI():
    """resets the UI to the default
    """
    session.clear()
    sc = SessionController()
    sc.resetDefaultSession()
    sc.resetUISession()
    return redirect("/", code=302)

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

    sampleList = jm.getSampleNames(currentExperiment)
    selectedSample = jm.getUIStateValue("currentSample")

    return render_template('main.html',
        experimentList=experimentList,
        sampleList=sampleList,
        selectedSample=selectedSample)

@app.route("/changeSample/<path:sample_name>", methods=["post"])
def changeSample(sample_name):
    sc = SessionController()
    #return the \ and ( ) characters among others i nhe sample name
    realSampleName = unquote(sample_name).replace("%28","(").replace("%29",")")
    sc.updateUIState("currentSample",realSampleName)
    return jsonify(request.json)

@app.route("/changeExperiment/<path:experiment_name>", methods=["post"])
def changeExperiment(experiment_name):
    sc = SessionController()
    #return the \ and ( ) characters among others in the experiment name
    realExperimentName = unquote(experiment_name).replace("%28","(").replace("%29",")")
    sc.updateUIState("currentExperiment",unquote(realExperimentName))
    jm = sc.getModel()
    firstSample = jm.getSampleNames(realExperimentName)[0]
    sc.updateUIState("currentSample",firstSample)
    return jsonify(request.json)

@app.route("/drawWidgetHTML", methods=["GET"])
def drawWidgetHTML():
    sc = SessionController()
    jm = sc.getModel()
    currentExperiment = jm.getUIStateValue("currentExperiment")
    selectedSample = jm.getUIStateValue("currentSample")
    jc = JasperCharts(jm)

    retVal = {}
    retVal["g_script"], retVal["g_div"] = \
          jc.create_chart(currentExperiment,selectedSample)
    retVal["t_script"], retVal["t_div"] = \
     jc.create_table(currentExperiment,selectedSample)

    return jsonify(retVal)
