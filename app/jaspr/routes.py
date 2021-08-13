#!/usr/bin/env python
# file jaspr/routes.py

"""Flask routes for browser based jaspr UI"""


# python imports
import json
from urllib.parse import unquote
from pandas import pandas as pd
from io import BytesIO

# flask imports
from flask import Flask, render_template, request, \
        jsonify, redirect, make_response, send_from_directory, send_file

# local imports
from jaspr import app
from jaspr.model import JasprModel
from jaspr.charts import JasprChart
from outlet import FunctionRegistry

# additional imports from api.py 6/10/21
from datetime import datetime
from tempfile import NamedTemporaryFile

from outlet import ParserRegistry

def save_tmpfile(upload_handle):
    """Save uploaded files to /tmp"""
    tmp_handle = NamedTemporaryFile(delete=False)
    tmp_handle.close()
    upload_handle.save(tmp_handle.name)
    return tmp_handle.name


@app.route('/updateConfigSetting', methods=['POST'])
def updateConfigSetting():
    jm = JasprModel()
    for k, v in request.form.items():
        jm.update_attribute(k, v)
    return 'true'


@app.route('/upload', methods = ['POST'])
def upload():
    datafile = save_tmpfile(request.files['datafile'])
    keyfile = save_tmpfile(request.files['keyfile'])

    jm = JasprModel()
    settings = ParserRegistry.plugins[jm.curr_parser](keyfile, datafile)()
    jm = JasprModel().set_defaults(settings)
        
    return redirect("/", code=302)
   

@app.route("/ping", methods = ['GET'])
def ping():
    """Simple function for AJAX test"""
    returnStr = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return json.dumps(returnStr)

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


@app.route('/reportResultAnalysis')
def reportOther():
    """Generate Excel Report"""
    jm=JasprModel()

    output=BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    headerList = ['Virus']
    for sample in jm.sample_list:
        headerList.append(sample + ', Titer')
        headerList.append(sample + ', Fold')
        headerList.append(sample + ', S/B')
        #headerList.append(sample)
        #secondHeader.append("Titer")
        #headerList.append("")
        #secondHeader.append("Fold")
        #headerList.append("")
        #secondHeader.append("S/B")

    rowList = []

    for experiment in jm.experiment_list:
        rowAdd = []
        rowAdd.append(experiment)
        for sample in jm.sample_list:
            rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample]['titer'])
            rowAdd.append('')
            #rowAdd.append(10000/float(jm.experiments[experiment]['results'][jm.curr_function][sample]['titer']))
            try:
                rowAdd.append('{:.1f}'.format(float(jm.experiments[experiment]['results'][jm.curr_function][sample]['Vmax'])/float(jm.experiments[experiment]['results'][jm.curr_function][sample]['cc'])))
            except ZeroDivisionError:
                rowAdd.append('{:.1f}'.format(float(jm.experiments[experiment]['results'][jm.curr_function][sample]['Vmax'])))
        rowList.append(rowAdd)

    df = pd.DataFrame(rowList, columns = headerList)
    a = df.columns.str.split(', ', expand=True).values
    df.columns = pd.MultiIndex.from_tuples([('', x[0]) if pd.isnull(x[1]) else x for x in a])
    df.to_excel(writer, sheet_name="Result Analysis")

    writer.close()

    output.seek(0)
    response = make_response(send_file(output, attachment_filename="reportResultAnalysis.xlsx", as_attachment=True))
    response.headers['cache-control'] = 'no-cache'
    return response


@app.route('/reportAntigenic')
def reportTiter():
    """Generate Excel Report"""
    jm=JasprModel()

    output=BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    headerList = ["Virus"]
    for sample in jm.sample_list:
        headerList.append(sample)

    rowList = []

    for experiment in jm.experiment_list:
        rowAdd = []
        rowAdd.append(experiment)
        for sample in jm.sample_list:
            import pprint
            pprint.pprint(sample)
            pprint.pprint (jm.experiments[experiment]['results'][jm.curr_function][sample])
            rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample]['titer'])

        rowList.append(rowAdd)

    df = pd.DataFrame(rowList, columns=headerList)
    df.to_excel(writer, sheet_name="Antigenic", index=False)

    writer.close()

    output.seek(0)
    response = make_response(send_file(output, attachment_filename="reportAntigenic.xlsx", as_attachment=True))
    response.headers['cache-control'] = 'no-cache'
    return response

# Print Report for ICP = 1000 values
@app.route('/reportICP1000')
def reportICP():
    """Generate Excel Report"""
    import pprint
    jm=JasprModel()
    output=BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    headerList = ["Virus"]
    
    for sample in jm.sample_list:
        headerList.append("Dilution")

    rowList = []

    for experiment in jm.experiment_list:
        rowAdd = []
        rowAdd.append(experiment)

        for sample in jm.sample_list:
            print("sample:")
            pprint.pprint(sample)
            pprint.pprint (jm.experiments[experiment]['results'])
            rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample]['ICP1000'])

        rowList.append(rowAdd)

    df = pd.DataFrame(rowList, columns=headerList)
    df.to_excel(writer, sheet_name="ICP_1000", index=False)

    writer.close()

    output.seek(0)
    response = make_response(send_file(output, attachment_filename="reportICP1000.xlsx", as_attachment=True))
    response.headers['cache-control'] = 'no-cache'
    return response

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
    response = make_response(send_file(output, attachment_filename="report.xlsx", as_attachment=True))
    response.headers['cache-control'] = 'no-cache'
    return response
