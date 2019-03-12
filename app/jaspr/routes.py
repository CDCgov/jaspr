#!/usr/bin/env python
# file jaspr/routes.py

"""Flask routes for browser based jaspr UI

"""

# python imports
import json
from urllib.parse import unquote

# flask imports
from flask import render_template, request, \
        jsonify, redirect, make_response, send_from_directory

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
   return render_template('upload.html')


@app.route('/settings')
def settings():
    """render the settings page"""
    jm = JasprModel()
    context = jm.context
    return render_template('settings.html', **context)


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
    print(request.headers)
    chart = JasprChart()
    return jsonify(chart())

@app.route('/report', methods=["GET"])
def report():
    """render the reports"""
    jc = JasprChart()
    pngList = jc.get_pngs()
    return render_template('report.html', pngList=pngList)

@app.route('/reportpngs/<path:filename>')
def reportpngs(filename):
    return send_from_directory(f"/app/{app.TEMPFILEDIR}", filename)