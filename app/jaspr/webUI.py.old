#!/usr/bin/env python
# file jaspr/webGUI.py
"""Flask routes for browser based jaspr UI

"""

# python imports
import json
from urllib.parse import unquote

# flask imports
from flask import Flask, render_template, request,session, \
        jsonify, redirect, make_response, send_from_directory

# local imports
from jaspr import app
from jaspr.Model.model import JasprModel
from jaspr.charting import JasprCharts
from jaspr.sessionController import SessionController
from outlet import FunctionRegistry


@app.route('/reset')
def reset():
    """resets the UI to the default
    """
    session.clear()
    response = make_response("<div>clearing session</div>")
    response.set_cookie(app.session_cookie_name, expires=0)
    return redirect("/", code=302)

@app.route('/upload')
def upload_file():
   return render_template('upload.html')

@app.route('/report')
def report():
    """render the reports"""
    sc = SessionController()
    jm = sc.getModel()

    experimentList = jm._jasprExperiments.getExperimentNames()
    currentExperiment = jm._uiState.getUIStateValue("currentExperiment")

    sampleList = jm._jasprExperiments.getSampleNames(currentExperiment)
    pngList = []
    for selectedSample in sampleList:
        jc = JasprCharts(jm)
        pngList.append(jc.create_PNG(currentExperiment,selectedSample))

    return render_template('report.html', pngList=pngList)

@app.route('/reportpngs/<path:filename>')
def reportpngs(filename):
    return send_from_directory(f"/app/{app.TEMPFILEDIR}", filename)

@app.route('/settings')
def settings():
    """render the settings page"""
    sc = SessionController()
    jm = sc.getModel()
    showCurveFit = jm._jasprConfig.getConfigSetting('showCurveFit')
    blankCorrection = jm._jasprConfig.getConfigSetting('blankCorrection')
    axisScale=jm._jasprConfig.getConfigSetting('axisScale')
    selectedAlgorithm=jm._jasprConfig.getConfigSetting('selectedAlgorithm')
    functionList = FunctionRegistry.plugins
    return render_template('settings.html',
            blankCorrection=blankCorrection,
            showCurveFit=showCurveFit,
            axisScale=axisScale,
            functionList=functionList,
            selectedAlgorithm=selectedAlgorithm)

@app.route('/')
def mainPage():
    """render the main page"""
    sc = SessionController()
    jm = sc.getModel()

    experimentList = jm._jasprExperiments.getExperimentNames()
    currentExperiment = jm._uiState.getUIStateValue("currentExperiment")

    sampleList = jm._jasprExperiments.getSampleNames(currentExperiment)
    selectedSample = jm._uiState.getUIStateValue("currentSample")

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
    firstSample = jm._jasprExperiments.getSampleNames(realExperimentName)[0]
    sc.updateUIState("currentSample",firstSample)
    return jsonify(request.json)


@app.route("/drawWidgetHTML", methods=["GET"])
def drawWidgetHTML():
    sc = SessionController()
    jm = sc.getModel()
    currentExperiment = jm._uiState.getUIStateValue("currentExperiment")
    selectedSample = jm._uiState.getUIStateValue("currentSample")
    jc = JasprCharts(jm)

    g_script, g_div = jc.create_chart(currentExperiment,selectedSample)
    t_script, t_div = jc.create_table(currentExperiment,selectedSample)

    #TODO pull this into the controller
    retVal = {}
    retVal["g_script"], retVal["g_div"] = \
          jc.create_chart(currentExperiment,selectedSample)
    retVal["t_script"], retVal["t_div"] = \
     jc.create_table(currentExperiment,selectedSample)

    return jsonify(retVal)
