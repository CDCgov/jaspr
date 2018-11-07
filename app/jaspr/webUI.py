#!/usr/bin/env python
# file jaspr/webGUI.py
"""Flask routes for browser based jaspr UI

"""

# python imports
import json
from urllib.parse import unquote

# flask imports
from flask import Flask, render_template, request,session, \
        jsonify, redirect, make_response

# local imports
from jaspr import app
from jaspr.model import JasprModel
from jaspr.charting import JasperCharts
from jaspr.sessionController import SessionController


@app.route('/reset')
def resetUI():
    """resets the UI to the default
    """
    session.clear()
    response = make_response("<div>clearing session</div>")
    response.set_cookie(app.session_cookie_name, expires=0)
    return redirect("/", code=302)

@app.route('/upload')
def upload_file():
   return render_template('upload.html')


@app.route('/settings')
def settings():
    """render the settings page"""
    return render_template('settings.html')


@app.route('/')
def mainPage():
    """render the main page"""
    sc = SessionController()
    jm = sc.getModel()
    #TODO wire up actual experiement selection from left menu
    experimentList = jm.getExperimentNames()
    currentExperiment = jm.getUIStateValue("currentExperiment")

    #TODO wire up actual sample selection from left menu
    sampleList = jm.getSampleNames(currentExperiment)
    selectedSample = jm.getUIStateValue("currentSample")

    return render_template('main.html',
        experimentList=experimentList,
        sampleList=sampleList,
        selectedSample=selectedSample)


@app.route("/changeSample/<sample_name>", methods=["post"])
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

    g_script, g_div = jc.create_chart(currentExperiment,selectedSample)
    t_script, t_div = jc.create_table(currentExperiment,selectedSample)

    #TODO pull this into the controller
    retVal = {}
    retVal["g_script"], retVal["g_div"] = \
          jc.create_chart(currentExperiment,selectedSample)
    retVal["t_script"], retVal["t_div"] = \
     jc.create_table(currentExperiment,selectedSample)

    return jsonify(retVal)
