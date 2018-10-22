#!/usr/bin/env python
# file jaspr/webGUI.py
"""Flask routes for browser based jaspr UI

"""

# python imports
import json

# flask imports
from flask import Flask, render_template, request,session, jsonify

# local imports
from jaspr import app
from jaspr.model import JasprModel
from jaspr.charting import JasperCharts
from jaspr.sessionController import SessionController


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
def changeSample(sample_name):
    sc = SessionController()
    sc.updateUIState("currentSample",sample_name)

    jm = sc.getModel()
    print("got to changeSample: " + jm.getUIStateValue("currentSample"))
    print("got to changeSample: " + jm.getUIStateString())
    print("cookie: " + json.dumps(request.cookies["session"]))
    return jsonify(request.json)


@app.route("/drawWidgetHTML", methods=["GET"])
def drawWidgetHTML():
    sc = SessionController()
    jm = sc.getModel()

    currentExperiment = jm.getUIStateValue("currentExperiment")
    selectedSample = jm.getUIStateValue("currentSample")

    print("got to draw widget: " + jm.getUIStateValue("currentSample"))
    print("got to draw widget: " + jm.getUIStateString())
    print("cookie: " + json.dumps(request.cookies["session"]))

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
