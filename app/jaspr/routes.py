#!/usr/bin/env python
# file jaspr/routes.py

"""Flask routes for browser based jaspr UI"""


# python imports
import json
from urllib.parse import unquote
from pandas import pandas as pd
from io import BytesIO

# flask imports
from flask import render_template, request, \
        jsonify, redirect, make_response, send_from_directory, send_file

# local imports
from jaspr import app
from jaspr.model import JasprModel
from jaspr.charts import JasprChart
from outlet import FunctionRegistry




@app.route('/reset')
def reset():
    """reset UI to the default"""
    JasprModel().ensure_session(reset=True)
    response = make_response("<div>clearing session</div>")
    response.set_cookie(app.session_cookie_name, expires=0)
    return redirect('/', code=302)


@app.route('/upload')
def upload_file():
    jm = JasprModel()
    return render_template('upload.html', **jm.context)


@app.route('/settings')
def settings():
    """render the settings page"""
    jm = JasprModel()
    return render_template('settings.html', **jm.context)


@app.route('/')
def main():
    """render the main page"""
    #TODO wire up actual experiement selection from left menu
    jm = JasprModel()
    return render_template('main.html', **jm.context)


@app.route("/changeSample/<path:sample_name>", methods=["post"])
def change_sample(sample_name):
    jm = JasprModel()

    jm.curr_sample = unquote(sample_name).replace('%28', '('
            ).replace('%29', ')')
    jm.update_session()
    return 'true'


@app.route("/changeExperiment/<path:experiment_name>", methods=["post"])
def change_experiment(experiment_name):
    jm = JasprModel()
    jm.curr_experiment = unquote(experiment_name).replace('%28', '('
            ).replace('%29', ')')
    jm.curr_sample = jm.sample_list[0]
    jm.update_session()
    return 'true'


@app.route("/drawWidgetHTML", methods=["GET"])
def drawWidgetHTML():
    chart = JasprChart()
    return jsonify(chart())

@app.route('/reportPNG', methods=["GET"])
def reportPngs():
    jc = JasprChart()
    pngList = jc.get_pngs()
    return render_template('reportPNG.html', pngList=pngList)

@app.route('/report', methods=["GET"])
def report():
    """render the reports"""
    #The charting report is broken so we bypass it for now
    # to make progress on other reports
    # jc = JasprChart()
    # pngList = jc.get_pngs()
    #return render_template('report.html', pngList=pngList)
    return render_template ('report.html')

@app.route('/reportpngs/<path:filename>')
def reportpngs(filename):
    return send_from_directory(f"/app/tmp", filename)

@app.route('/reportExcel')
def reportexcel():
    """Generate Excel Report"""
    jm = JasprModel()
    # df = pd.DataFrame({'Data': [10,20,40,20,15,30,45]})

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    sampleList = ["Virus"]
    for sample in jm.sample_list:
        sampleList.append(sample)
        
    sampleList.append("VC")
    sampleList.append("CC")
        
    #df = pd.DataFrame(columns=sampleList)

    rowList = []
    
    # loop sample sets
    for experiment in jm.experiment_list:
        rowAdd = []
        rowAdd.append(experiment)
        for sample in jm.sample_list:
            rowAdd.append(jm.experiments[experiment]['data'][sample]['y_values'][0])
            
        rowAdd.append(jm.experiments[experiment]['cc'])
        rowAdd.append(jm.experiments[experiment]['vc'])
        
        rowList.append(rowAdd)
        
        #df = pd.DataFrame(jm.experiments[jm.curr_experiment]['data'][sample_set])
    
    df = pd.DataFrame(rowList, columns=sampleList)
    df.to_excel(writer, sheet_name="FRA", index=False)
    
    writer.close()

    output.seek(0)
    return send_file(output, attachment_filename="report.xlsx", as_attachment=True)
