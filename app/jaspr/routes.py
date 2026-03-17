#!/usr/bin/env python
# file jaspr/routes.py

"""Flask routes for browser based jaspr UI"""

# python imports
import json
from urllib.parse import unquote
from pandas import pandas as pd
import numpy as np
from io import BytesIO
import pprint
import itertools 
import os.path
import glob
import os
import tempfile
import zipfile


def _noop_pprint(*args, **kwargs):
    return None


# Disable verbose pprint output in request handlers to avoid blocking stdout under uWSGI.
pprint.pprint = _noop_pprint


def _noop_pprint(*args, **kwargs):
    return None


# Disable verbose pprint output in request handlers to avoid blocking stdout under uWSGI.
pprint.pprint = _noop_pprint

# flask imports
from flask import Flask, render_template, request, \
    jsonify, redirect, make_response, send_from_directory, send_file, session, render_template_string
from jinja2 import TemplateNotFound

# local imports
from jaspr import app
from jaspr.model import JasprModel
from jaspr.charts import JasprChart

# additional imports from api.py 6/10/21
from datetime import datetime
from tempfile import NamedTemporaryFile

from outlet import ParserRegistry
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'csv', 'xls', 'xlsx'])


def _set_analysis_session_ready():
    """Mark session state for analysis/report navigation availability."""
    session['analysis_ready'] = True
    session['report_ready'] = True
    session.modified = True


def _is_report_ready():
    """Return whether report routes should be available for current session."""
    return bool(session.get('analysis_ready', False) and session.get('report_ready', False))


def _first_result_record(jm):
    """Return a representative result dict from the loaded run or {}."""
    if not jm.experiment_list or not jm.sample_list:
        return {}

    try:
        exp = jm.experiment_list[0]
        sample = jm.sample_list[0]
        return jm.experiments[exp]['results'][jm.curr_function][sample]
    except (KeyError, IndexError, TypeError):
        return {}


def _available_report_links(jm):
    """Build report links that are expected to work for current analysis data."""
    if _is_anscombe_dataset(jm):
        return []

    if _is_frnt_parser(jm):
        return [
            {
                'label': 'Download Antigenic Report',
                'href': '/reportAntigenic',
                'description': 'Virus-by-sera table of assay titers.'
            },
            {
                'label': 'Download FRNT Results Report',
                'href': '/reportFRNTResultAnalysis',
                'description': 'FRNT-formatted output for pooled sera workflows.'
            },
        ]

    links = []

    first_result = _first_result_record(jm)
    keys = set(first_result.keys()) if isinstance(first_result, dict) else set()

    # General summary reports rely on titer/ec50-like result keys.
    if {'titer', 'ec50'}.intersection(keys):
        links.append({
            'label': 'Download Antigenic Report',
            'href': '/reportAntigenic',
            'description': 'Virus-by-sera table of assay titers.'
        })
        links.append({
            'label': 'Download Result Analysis Report',
            'href': '/reportResultAnalysis',
            'description': 'Summary table with titer/fold/SB metrics.'
        })

    # ICP-specific endpoint expects ICP1000 result output.
    if 'ICP1000' in keys:
        links.append({
            'label': 'Download ICP 1000 Report',
            'href': '/reportICP1000',
            'description': 'Dilution estimates at ICP=1000 for each virus.'
        })

    # FRNT exports depend on pooled_sera metadata and FRNT result keys.
    has_pooled_sera = False
    if jm.experiment_list:
        first_exp = jm.experiment_list[0]
        has_pooled_sera = 'pooled_sera' in jm.experiments.get(first_exp, {})

    if has_pooled_sera and {'IC50', 'h', 'Vmax', 'titer'}.intersection(keys):
        links.append({
            'label': 'Download FRNT Results Report',
            'href': '/reportFRNTResultAnalysis',
            'description': 'FRNT-formatted output for pooled sera workflows.'
        })

    return links


def _guard_report_route():
    """Redirect to load flow when report routes are accessed without data."""
    if not _is_report_ready():
        return redirect('/upload', code=302)
    return None


def _guard_specific_report_href(jm, href):
    """Return a friendly response when a direct report route is not available."""
    available_links = _available_report_links(jm)
    available_hrefs = {item.get('href') for item in available_links}

    if href in available_hrefs:
        return None

    return render_template(
        'report.html',
        report_links=available_links,
        no_reports_message='This report is not available for the current parser and data. Please choose from the available reports.'
    )


def _is_anscombe_dataset(jm):
    """Return True when the active session is the built-in Anscombe dataset."""
    return bool(jm.experiment_list and jm.experiment_list[0] == 'Anscombe')


def _is_frnt_parser(jm):
    """Return True when the current parser is one of the FRNT parser variants."""
    return jm.curr_parser in {
        'FRNT Virus-Serum-Serum Plate Layout Cx5',
        'FRNT Serum-Virus-Virus Plate Layout Cx5',
        'FRNT Virus-Serum-Serum Plate Layout Cytation7',
    }

def page_not_found(e):
    return render_template('502.html'), 502

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

#  # Original code \/ \/ \/ ###
# @app.route('/upload', methods = ['POST'])
# def upload():
#     datafile = save_tmpfile(request.files['datafile'])
#     keyfile = save_tmpfile(request.files['keyfile'])

#     jm = JasprModel()
#     settings = ParserRegistry.plugins[jm.curr_parser](keyfile, datafile)()
#     jm = JasprModel().set_defaults(settings)
        
#     return redirect("/", code=302)
#  # Original code /\ /\ /\ ###

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods = ['POST'])
def upload():
    datafile = save_tmpfile(request.files['datafile'])
    keyfile = save_tmpfile(request.files['keyfile'])

    # \/ \/ Capture Key File Name \/ \/ #
    file = request.files['keyfile']
    filename = secure_filename(file.filename)
    tmp_folder = '/tmp'
    # pprint.pprint(os.getcwd())
    os.chdir('../tmp')
    # pprint.pprint(os.getcwd())
    file.save(filename)    
    # pprint.pprint(os.getcwd())
    os.chdir('../app')
    # pprint.pprint(os.getcwd())
    # /\ /\ Capture Key File Name /\ /\ #        

    jm = JasprModel()
    settings = ParserRegistry.plugins[jm.curr_parser](keyfile, datafile)()
    jm = JasprModel().set_defaults(settings)

    _set_analysis_session_ready()

    return redirect('/analysis', code=302)
   
@app.route("/ping", methods = ['GET'])
def ping():
    """Simple function for AJAX test"""
    returnStr = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return json.dumps(returnStr)

@app.route('/reset')
def reset():
    """reset UI to the default"""
    JasprModel().ensure_session(reset=True)
    session.clear()
    return redirect('/', code=302)


@app.route('/upload')
def upload_file():
    jm = JasprModel()
    return render_template('upload.html', **jm.context)


@app.route('/loadAnscombeData')
def load_anscombe_data():
    """Reset the session to the built-in Anscombe dataset."""
    jm = JasprModel()
    jm.set_defaults()
    _set_analysis_session_ready()
    return redirect('/analysis', code=302)


@app.route('/analysis')
def analysis():
    """Render the analysis page once data has been loaded."""
    if not session.get('analysis_ready', False):
        return redirect('/upload', code=302)

    jm = JasprModel()
    return render_template('analysis.html', **jm.context)


@app.route('/downloadExampleData')
def download_example_data():
    """Download bundled example input files as a zip archive."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    example_dir = os.path.join(repo_root, 'example_data')

    if not os.path.isdir(example_dir):
        return redirect('/error502', code=302)

    tmp_handle = tempfile.NamedTemporaryFile(prefix='jaspr_example_data_', suffix='.zip', delete=False)
    tmp_handle.close()

    with zipfile.ZipFile(tmp_handle.name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(example_dir):
            for file_name in files:
                abs_path = os.path.join(root, file_name)
                arcname = os.path.relpath(abs_path, repo_root)
                zf.write(abs_path, arcname)

    response = make_response(send_file(
        tmp_handle.name,
        as_attachment=True,
        download_name=f'jaspr_example_data_{datetime.now().strftime("%Y_%m_%d")}.zip'
    ))
    response.headers['cache-control'] = 'no-cache'
    return response

@app.route('/error502')
def error502():
    jm = JasprModel()
    return render_template('502.html', **jm.context)


@app.route('/favicon.ico')
def favicon():
    """Serve favicon for app servers that are not fronted by nginx."""
    return send_from_directory(app.static_folder, 'favicon.ico')


@app.route('/favicon_32.png')
def favicon_32():
    """Serve 32px favicon fallback for browser icon selection."""
    return send_from_directory(app.static_folder, 'favicon_32.png')

@app.route('/settings')
def settings():
    """render the settings page"""
    jm = JasprModel()
    return render_template('settings.html', **jm.context)


@app.route('/license')
def license_page():
    """Render the license page with the app navigation menu."""
    jm = JasprModel()
        try:
                return render_template('license.html', **jm.context)
        except TemplateNotFound:
                return render_template_string(
                        """
<!DOCTYPE html>
<html lang="en">
    {% include "head.html" %}
    <body>
        <main class='site-content'>
            {% include "nav.html" %}
            <div class="container mt-3">
                <div class="row mb-3">
                    <div class="col-12">
                        <div class="card h-100">
                            <div class="card-body">
                                <h4 class="card-title mb-3">License</h4>
                                <p class="card-text">
                                    <strong>jaspr</strong> is released under the Apache License, Version 2.0 (Apache-2.0), a permissive open-source license
                                    that allows use, modification, and distribution in compliance with the License terms.
                                </p>
                                <p class="card-text mb-0">
                                    You may obtain a copy of the License at
                                    <a href="http://www.apache.org/licenses/LICENSE-2.0" target="_blank" rel="noopener noreferrer">
                                        http://www.apache.org/licenses/LICENSE-2.0
                                    </a>.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
        <footer>
            {% include "footer.html" %}
        </footer>
    </body>
</html>
                        """,
                        **jm.context,
                )


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


@app.route('/report', methods=["GET"])
def report():
    """render the reports"""
    guard = _guard_report_route()
    if guard is not None:
        return guard

    jm = JasprModel()
    report_links = _available_report_links(jm)
    no_reports_message = 'Results are not provided for the Anscombe data set.' if _is_anscombe_dataset(jm) else None

    return render_template('report.html', report_links=report_links, no_reports_message=no_reports_message)


@app.route('/reportResultAnalysis')
def reportOther():
    """Generate Excel Report"""
    guard = _guard_report_route()
    if guard is not None:
        return guard

    jm=JasprModel()
    specific_guard = _guard_specific_report_href(jm, '/reportResultAnalysis')
    if specific_guard is not None:
        return specific_guard

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
    response = make_response(send_file(output, download_name='reportResultAnalysis' + str(datetime.now().strftime('%Y_%m_%d')) +'.xlsx', as_attachment=True))
    response.headers['cache-control'] = 'no-cache'
    return response


@app.route('/reportAntigenic')
def reportTiter():
    """Generate Excel Report"""
    guard = _guard_report_route()
    if guard is not None:
        return guard

    jm=JasprModel()
    specific_guard = _guard_specific_report_href(jm, '/reportAntigenic')
    if specific_guard is not None:
        return specific_guard

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
            viral_sample = (jm.experiments[experiment]['results'][jm.curr_function][sample])
            ERROR = "Regression Failed"
            titer = 'titer'
            rowAdd.append(viral_sample.get(titer, ERROR))

        rowList.append(rowAdd)

    df = pd.DataFrame(rowList, columns=headerList)
    df.to_excel(writer, sheet_name="Antigenic", index=False)

    writer.close()

    output.seek(0)
    response = make_response(send_file(output, download_name='reportAntigenic' + str(datetime.now().strftime('%Y_%m_%d')) +'.xlsx', as_attachment=True))
    response.headers['cache-control'] = 'no-cache'
    return response

# Print Report for ICP = 1000 values
@app.route('/reportICP1000')
def reportICP():
    """Generate Excel Report"""
    guard = _guard_report_route()
    if guard is not None:
        return guard

    import pprint
    jm=JasprModel()
    specific_guard = _guard_specific_report_href(jm, '/reportICP1000')
    if specific_guard is not None:
        return specific_guard

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
            pprint.pprint("sample:")
            pprint.pprint(sample)
            pprint.pprint (jm.experiments[experiment]['results'])
            rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample]['ICP1000'])

        rowList.append(rowAdd)

    df = pd.DataFrame(rowList, columns=headerList)
    df.to_excel(writer, sheet_name="ICP_1000", index=False)

    writer.close()

    output.seek(0)

    response = make_response(send_file(output, download_name='reportICP1000_' + str(datetime.now().strftime('%Y_%m_%d')) +'.xlsx', as_attachment=True))
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
    response = make_response(send_file(output, download_name='report' + str(datetime.now().strftime('%Y_%m_%d')) +'.xlsx', as_attachment=True))
    response.headers['cache-control'] = 'no-cache'
    return response

# Print Full Report for the Experiment
@app.route('/Experiment_report')
def reportExperiment_Full():
    """Generate Excel Report"""
    jm=JasprModel()
   
    output=BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    headerList = ["Virus"]
    for sample in jm.sample_list:
        headerList.append(sample)

        pprint.pprint("Sample:")
        pprint.pprint(sample)
        
    rowList = []

    for experiment in jm.experiment_list:
        rowAdd = []
        rowAdd.append(experiment)
        pprint.pprint("Experiment")
        pprint.pprint(experiment)

        for sample in jm.sample_list:
            #print("sample:")
            #pprint.pprint(sample)
            #pprint.pprint (jm.experiments[experiment]['results'])
            rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample])

        rowList.append(rowAdd)

    df = pd.DataFrame(rowList, columns=headerList)
    print(df)
    df.to_excel(writer, sheet_name="Full_Report", index=False)

    writer.close()

    output.seek(0)

    response = make_response(send_file(output, download_name='Full_Report_' + str(datetime.now().strftime('%Y_%m_%d')) +'.xlsx', as_attachment=True))
    response.headers['cache-control'] = 'no-cache'
    return response

# Print Full Report for the Experiment
@app.route('/FRNT_Full_report')
def reportFRNT_Full():
    """Generate Excel Report"""
    jm=JasprModel()
   
    output=BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    headerList = ["Virus"]
    for sample in jm.sample_list:
        headerList.append(sample)

        pprint.pprint("Sample:")
        pprint.pprint(sample)
        
    rowList = []

    for experiment in jm.experiment_list:
        rowAdd = []
        rowAdd.append(experiment)
        pprint.pprint("Experiment")
        pprint.pprint(experiment)

        for sample in jm.sample_list:
            #print("sample:")
            #pprint.pprint(sample)
            #pprint.pprint (jm.experiments[experiment]['results'])
            rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample])

        rowList.append(rowAdd)

    df = pd.DataFrame(rowList, columns=headerList)
    print(df)
    df.to_excel(writer, sheet_name="Full_Report", index=False)

    writer.close()

    output.seek(0)

    response = make_response(send_file(output, download_name='FRNT_Report_' + str(datetime.now().strftime('%Y_%m_%d')) +'.xlsx', as_attachment=True))
    response.headers['cache-control'] = 'no-cache'
    return response

@app.route('/FRNT_Titers')
def reportFRNT_Titers():
    """Generate Excel Report"""
    jm=JasprModel()
   
    output=BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    headerList = ["Virus"]
    for sample in jm.sample_list:
        headerList.append(sample)

        pprint.pprint("Sample:")
        pprint.pprint(sample)
        
    rowList = []

    for experiment in jm.experiment_list:
        rowAdd = []
        rowAdd.append(experiment)
        pprint.pprint("Experiment")
        pprint.pprint(experiment)
    
        for sample in jm.sample_list:

            rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample]['IC50'])
        rowList.append(rowAdd)

    for experiment in jm.experiment_list:
        rowAdd = []
        rowAdd.append(experiment)
        pprint.pprint("Experiment")
        pprint.pprint(experiment)

        for sample in jm.sample_list:

            rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample]['h'])
        rowList.append(rowAdd)
    df = pd.DataFrame(rowList, columns=headerList)
    print(df)
    df.to_excel(writer, sheet_name="Titers_Report", index=False)

    for experiment in jm.experiment_list:
        rowAdd = []
        rowAdd.append(experiment)
        pprint.pprint("Experiment")
        pprint.pprint(experiment)

        for sample in jm.sample_list:
            rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample]['Vmax'])
        rowList.append(rowAdd)
    df = pd.DataFrame(rowList, columns=headerList)
    print(df)
    df.to_excel(writer, sheet_name="Titers_Report", index=False)

    for experiment in jm.experiment_list:
        rowAdd = []
        rowAdd.append(experiment)
        pprint.pprint("Experiment")
        pprint.pprint(experiment)

        for sample in jm.sample_list:

            rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample]['titer'])
        rowList.append(rowAdd)
    df = pd.DataFrame(rowList, columns=headerList)
    print(df)
    df.to_excel(writer, sheet_name="Titers_Report", index=False)

    writer.close()

    output.seek(0)

    response = make_response(send_file(output, download_name='FRNT_Titers_' + str(datetime.now().strftime('%Y_%m_%d')) +'.xlsx', as_attachment=True))
    response.headers['cache-control'] = 'no-cache'
    return response

@app.route('/reportFRNTResultAnalysis')
def reportFRNTresults():
    """Generate Excel Report"""
    guard = _guard_report_route()
    if guard is not None:
        return guard

    jm=JasprModel()
    specific_guard = _guard_specific_report_href(jm, '/reportFRNTResultAnalysis')
    if specific_guard is not None:
        return specific_guard

    pprint.pprint("The JASPR Model:")
    pprint.pprint(jm.experiments)
    
    # for experiment in jm.experiment_list:
    #     for sample in jm.sample_list:
    
    #         pprint.pprint("experiment")
    #         pprint.pprint(jm.experiments[experiment])

    # pprint.pprint(os.getcwd())
    os.chdir('../tmp')
    # pprint.pprint(os.getcwd())
    filename = glob.glob('/tmp/*xlsx')
    # pprint.pprint(filename)
    filename = max(filename, key=os.path.getctime)
    # pprint.pprint(filename)
    testname = pd.DataFrame([filename], columns=['Test Name'])
    testname = testname.replace(regex={'/tmp/':'', '.xlsx':''})
    # filename = testname.append(filename)
    # pprint.pprint(testname)


    output=BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    headerList = ['Virus']
    for sample in jm.sample_list:
        headerList.append(', Sera')
        headerList.append(', ec50')
        headerList.append(', h')
        headerList.append(', Vmax')
        headerList.append(', titer')

    # pprint.pprint("headerList")
    # pprint.pprint(headerList)

    rowList = []
    rowAdd = []
    for experiment in jm.experiments:
        # for sample in jm.sample_list:
        # rowAdd.append(sample)
        # rowAdd.append(experiment)
        rowList.append(rowAdd)
        for sample in jm.sample_list:
            rowAdd.append([jm.experiments[experiment]['results'][jm.curr_function][sample]['ec50']])
            rowAdd.append([jm.experiments[experiment]['results'][jm.curr_function][sample]['h']])
            rowAdd.append([jm.experiments[experiment]['results'][jm.curr_function][sample]['Vmax']])
            rowAdd.append([jm.experiments[experiment]['results'][jm.curr_function][sample]['titer']])
 
    pooled_CUIDs = pd.DataFrame(jm.experiments[experiment]['pooled_sera'])
    pooled_CUIDs = pooled_CUIDs.T


    with pd.option_context('display.max_rows', None, 
                             'display.max_columns', None, 
                             'display.precision', 0,):
        pprint.pprint("pooled_CUIDs")
        pprint.pprint(pooled_CUIDs)

    Start_dilution = pooled_CUIDs['Starting Dilution'].astype(str)
    Start_dilution = pd.DataFrame(Start_dilution)
    Start_dilution = Start_dilution['Starting Dilution'].values.tolist()

    Dilution_factor = pooled_CUIDs['Dilution Factor'].astype(str)
    Dilution_factor = pd.DataFrame(Dilution_factor)
    Dilution_factor = Dilution_factor['Dilution Factor'].values.tolist()

    Sera_CSIDs = pooled_CUIDs['CSID'].astype(str)
    Sera_CSIDs = pd.DataFrame(Sera_CSIDs)
    Sera_CSIDs = Sera_CSIDs['CSID'].values.tolist()

    Pooled_FluLIMS = pooled_CUIDs['Pooled in FluLIMS'].astype(str)
    Pooled_FluLIMS = pd.DataFrame(Pooled_FluLIMS)
    Pooled_FluLIMS = Pooled_FluLIMS['Pooled in FluLIMS'].values.tolist()

    # pprint.pprint(Start_dilution)
    # pprint.pprint(Dilution_factor)
    # pprint.pprint(Sera_CSIDs)

    CUIDs = pooled_CUIDs['CUID'].astype(str) + ", " + pooled_CUIDs['CUIDs in Pool'].astype(str)
    CUIDs = pd.DataFrame(CUIDs)

    # pprint.pprint("just CUIDs")
    # pprint.pprint(CUIDs)

    pooled_CUIDs['CUIDs'] = CUIDs
    
    # with pd.option_context('display.max_rows', None, 
    #         'display.max_columns', None, 
    #         ):
    #         pprint.pprint("pooled CUIDs")
    #         pprint.pprint(pooled_CUIDs)
    del pooled_CUIDs["Name"] 
    del pooled_CUIDs["CUID"]
    # with pd.option_context('display.max_rows', None, 
    #         'display.max_columns', None, 
    #         ):
    #         pprint.pprint("pooled CUIDs transpose 2")
    #         pprint.pprint(pooled_CUIDs)

    # pprint.pprint("look here--")
    pooled_CUIDs = pooled_CUIDs['CUIDs'].str.replace(', nan','')
    # with pd.option_context('display.max_rows', None, 
    #         'display.max_columns', None, 
    #         'display.precision', 0,):
    #         pprint.pprint("replace")
    #         pprint.pprint(pooled_CUIDs)

    pooled_CUIDs = pd.DataFrame(pooled_CUIDs)
    pooled_CUIDs.columns=['CUIDs']
    # pprint.pprint(pooled_CUIDs)

    sera_CUIDs = pooled_CUIDs['CUIDs'].values.tolist()
    # pprint.pprint(sera_CUIDs)

    Viruses = jm.experiment_list
    # pprint.pprint("Viruses")
    # pprint.pprint(Viruses)
    virus_CSIDs = jm.experiments[experiment]['virus_CSIDs']
    # pprint.pprint("virus_CSIDs")
    # pprint.pprint(virus_CSIDs)
    virus_pooled_FluLIMS = jm.experiments[experiment]['virus_pooled_FluLIMS']
   
    virus_pooled_ELIMs = jm.experiments[experiment]['virus_pooled_ELIMS']

    virus_pooled_CSIDs = jm.experiments[experiment]['virus_pooled_CSIDs']

    virus_type = jm.experiments[experiment]['virus_type']
    # pprint.pprint("virus_type")
    # pprint.pprint(virus_type)
    target_activity = jm.experiments[experiment]['target_activity']
    # pprint.pprint("target_activity")
    # pprint.pprint(target_activity)
    initial_activity = jm.experiments[experiment]['initial_activity']
    # pprint.pprint("initial_activity")
    # pprint.pprint(initial_activity)
    plate_layout = jm.experiments[experiment]['plate_layout']
    plate_layout = plate_layout[0]
    # pprint.pprint("plate_layout")
    # pprint.pprint(plate_layout)
    N_virus = len(jm.experiment_list)
    # pprint.pprint("N_viruses:")
    # pprint.pprint(N_virus)
    Sera = jm.sample_list
    # pprint.pprint("Sera")
    # pprint.pprint(Sera)
    N_sera = len(jm.sample_list)
    # pprint.pprint("N_sera:")
    # pprint.pprint(N_sera)
    SeraLIST = list(itertools.chain.from_iterable(itertools.repeat(Sera, N_virus)))
    # pprint.pprint("SeraLIST:")
    # pprint.pprint(SeraLIST)
    VirusLIST = list(itertools.chain.from_iterable(itertools.repeat(Viruses, N_sera)))
    # pprint.pprint("VirusLIST:")
    # pprint.pprint(VirusLIST)
    virus_CSIDs = list(itertools.chain.from_iterable(itertools.repeat(virus_CSIDs, N_sera)))
    # pprint.pprint("virus_CSIDs")
    # pprint.pprint(virus_CSIDs)
    virus_pooled_FluLIMS = list(itertools.chain.from_iterable(itertools.repeat(virus_pooled_FluLIMS, N_sera)))

    virus_pooled_ELIMs = list(itertools.chain.from_iterable(itertools.repeat(virus_pooled_ELIMs, N_sera)))

    virus_pooled_CSIDs = list(itertools.chain.from_iterable(itertools.repeat(virus_pooled_CSIDs, N_sera)))

    virus_type = list(itertools.chain.from_iterable(itertools.repeat(virus_type, N_sera)))
    # pprint.pprint("virus_type")
    # pprint.pprint(virus_type)
    target_activity = list(itertools.chain.from_iterable(itertools.repeat(target_activity, N_sera)))
    # pprint.pprint("target_activity")
    # pprint.pprint(target_activity)
    initial_activity = list(itertools.chain.from_iterable(itertools.repeat(initial_activity, N_sera)))
    # pprint.pprint("initial_activity")
    # pprint.pprint(initial_activity)

    pooled_CUIDs = list(itertools.chain.from_iterable(itertools.repeat(sera_CUIDs, N_virus)))
    Start_dilution = list(itertools.chain.from_iterable(itertools.repeat(Start_dilution, N_virus)))
    Dilution_factor = list(itertools.chain.from_iterable(itertools.repeat(Dilution_factor, N_virus)))
    Sera_CSIDs = list(itertools.chain.from_iterable(itertools.repeat(Sera_CSIDs, N_virus)))
    Pooled_FluLIMS = list(itertools.chain.from_iterable(itertools.repeat(Pooled_FluLIMS, N_virus)))
    # with pd.option_context('display.max_rows', None, 
    #         'display.max_columns', None, 
    #         'display.precision', 0,):
    #         pprint.pprint("pooled CUIDs")
    # pprint.pprint(pooled_CUIDs)
    # pprint.pprint(Start_dilution)
    # pprint.pprint(Dilution_factor)
    # pprint.pprint(Sera_CSIDs)

    N = N_virus * N_sera

    data = np.array(rowList[0])
    # pprint.pprint("data as array:")
    # pprint.pprint(data)
     
    data = np.reshape(data, (N,4))

    with pd.option_context('display.max_rows', None, 
            'display.max_columns', None, 
            'display.precision', 0,):
            pprint.pprint("data_to_reshape()")
            # pprint.pprint(data)

    SeraLIST = pd.DataFrame(SeraLIST, columns=['Sera'])
    VirusLIST = pd.DataFrame(VirusLIST, columns=['Virus'])
    virus_CSIDs = pd.DataFrame(virus_CSIDs, columns=['Virus CSIDs'])
    virus_pooled_FluLIMS = pd.DataFrame(virus_pooled_FluLIMS, columns=['Virus Pooled in FluLIMS'])
    virus_pooled_ELIMs = pd.DataFrame(virus_pooled_ELIMs, columns=['Virus Pooled in ELIMS'])
    virus_pooled_CSIDs = pd.DataFrame(virus_pooled_CSIDs, columns=['Virus CUIDs in Pool'])
    virus_type = pd.DataFrame(virus_type, columns=['Virus type'])
    target_activity = pd.DataFrame(target_activity, columns=['Target activity'])
    initial_activity = pd.DataFrame(initial_activity, columns=['Initial activity'])

    Virus_data = [VirusLIST, virus_CSIDs, virus_pooled_FluLIMS, virus_pooled_ELIMs, virus_pooled_CSIDs, \
                virus_type, target_activity, initial_activity]
    Virus_data = pd.concat(Virus_data, axis=1)
    Virus_data = Virus_data.sort_values(by=['Virus'])
    Virus_data = Virus_data.drop(['Virus'], axis=1)
    Virus_data = Virus_data.reset_index()
    Virus_data = Virus_data.drop(['index'], axis=1)
    with pd.option_context('display.max_rows', None, 
            'display.max_columns', None, ):
            pprint.pprint("Virus_data")
            pprint.pprint(Virus_data)

    VirusLIST = list(itertools.chain.from_iterable(itertools.repeat(Viruses, N_sera)))
    VirusLIST.sort()
    VirusLIST = pd.DataFrame(VirusLIST, columns=['Virus'])

    data = pd.DataFrame(data, columns=['ec50', 'h', 'Vmax', 'titer'])
    pooled_CUIDs = pd.DataFrame(pooled_CUIDs, columns=['Sera CUIDs'])
    Start_dilution = pd.DataFrame(Start_dilution, columns=['Starting dilution'])
    Dilution_factor = pd.DataFrame(Dilution_factor, columns=['Dilution factor'])
    Sera_CSIDs = pd.DataFrame(Sera_CSIDs, columns=['Sera CSIDs'])
    Sera_CSIDs = Sera_CSIDs.replace("nan","")
    Pooled_FluLIMS= pd.DataFrame(Pooled_FluLIMS, columns=['Sera Pooled in FluLIMS'])

    Combined = [SeraLIST, VirusLIST, data]
    data = pd.concat(Combined, axis=1)
    with pd.option_context('display.max_rows', None, 
            'display.max_columns', None, 
            'display.precision', 0,):
            pprint.pprint("data")
            pprint.pprint(data)

    sera_ = data['Sera'].str.split(' ', expand=True)
    sera_ = pd.DataFrame(sera_)
    sera_.columns=['Sera Number', 'Sera']
    # pprint.pprint(sera_)
    
    virus_ = data['Virus'].str.split(' ', expand=True)
    virus_ = pd.DataFrame(virus_)
    # virus_.columns=['Virus Number', 'Virus CUIDs']
    with pd.option_context('display.max_rows', None, 
            'display.max_columns', None, ):
            pprint.pprint('virus_')
            pprint.pprint(virus_)

    with pd.option_context('display.max_rows', None, 
            'display.max_columns', None, ):
            pprint.pprint("Virus_data")
            pprint.pprint(Virus_data)
    Error = pd.DataFrame(columns=['Error'])
    Error = Error.replace({'Error': {'NaN':''}})

    Combined2 = [sera_, pooled_CUIDs, Sera_CSIDs, Pooled_FluLIMS, Start_dilution, \
                 Dilution_factor, virus_, Virus_data, data, Error]
    data = pd.concat(Combined2, axis=1)
    del data["Sera"]
    del data["Virus"]

    with pd.option_context('display.max_rows', None, 
            'display.max_columns', None, 
            'display.precision', 0,):
            pprint.pprint("data")
            pprint.pprint(data)

    data['h'] = pd.to_numeric(data['h'])
    data.loc[data['h'] <= 0.5, 'Error'] = 'h <= 0.5'
    data.loc[data['h'] >= 2.0, 'Error'] = 'h >= 2.0'

    data['Vmax'] = pd.to_numeric(data['Vmax'])
    data.loc[data['Vmax'] < 40, 'Error'] = 'low input FFU (Vmax < 40)'

    with pd.option_context('display.max_rows', None, 
            'display.max_columns', None, 
            'display.precision', 0,):
            pprint.pprint("data")
            pprint.pprint(data)    

    pprint.pprint('testname')
    pprint.pprint(testname) 
    test_type = testname['Test Name'].str[:4]
    test_type = test_type.values.tolist()
    test_type = (','.join(test_type))
    testname_ = testname['Test Name'].str[:999]
    testname_ = testname_.values.tolist()
    testname_ = (','.join(testname_))
    test_date = testname['Test Name'].str[14:22]
    test_date = test_date.values.tolist()
    test_date = (''.join(test_date))
    test_date = datetime.strptime(test_date, "%m%d%Y").date()
    FluLIMS_run = testname['Test Name'].str[9:13]
    FluLIMS_run = FluLIMS_run.values.tolist()
    FluLIMS_run = (','.join(FluLIMS_run))    

    Table = [['Test type', test_type], \
            ['Protocol version', 2021], \
            ['Test name', testname_], \
            ['Test date', test_date], \
            ['FluLIMS run', FluLIMS_run], \
            ['Activity units', 'FFU / 25µL'], \
            ['Plate layout', plate_layout],     
            []    ]

    pprint.pprint('Table')
    pprint.pprint(Table)
    FRNT_date = str(test_date)
    pprint.pprint(data.columns)

    pprint.pprint('data')
    pprint.pprint(data)

    data = data.values.tolist()
    pprint.pprint('data')
    pprint.pprint(data)

    labels = [['Sera Number', 'Sera CUIDs', 'Sera CSIDs', 'Sera Pooled in FluLIMS', 'Starting dilution', 'Dilution factor', \
        'Virus Number', 'Virus CUIDs', 'Virus CSIDs', 'Virus Pooled in FluLIMS', 'Virus Pooled in ELIMS', 'Virus CUIDs in Pool', 'Virus type', 'Target activity', \
        'Initial activity', 'ec50', 'h', 'Vmax', 'titer', 'Error']]  

    FRNTreport = Table + labels + data
    FRNTreport = pd.DataFrame(FRNTreport)
    pprint.pprint('FRNTreport')
    pprint.pprint(FRNTreport)

    FRNTreport.to_excel(writer, sheet_name="FRNT Result Analysis", index=False, startrow = 0, header = False)

    writer.close()

    output.seek(0)
    response = make_response(send_file(output, download_name='FRNT-'+ FluLIMS_run +'-Results-' + FRNT_date +'.xlsx', as_attachment=True))
    response.headers['cache-control'] = 'no-cache'
    return response

# # This produces the report as 'Viruses X Sera' \/ \/ \/  ##
# @app.route('/reportFRNTResultAnalysis')
# def reportFRNTresults():
#     """Generate Excel Report"""
#     jm=JasprModel()

#     output=BytesIO()
#     writer = pd.ExcelWriter(output, engine='xlsxwriter')

#     headerList = ['Virus']
#     for sample in jm.sample_list:
#         headerList.append(sample + ', ec50')
#         headerList.append(sample + ', h')
#         headerList.append(sample + ', Vmax')
#         headerList.append(sample + ', titer')
#     rowList = []

#     for experiment in jm.experiment_list:
#         pprint.pprint(jm.experiments[experiment]['data'])
#         rowAdd = []
#         rowAdd.append(experiment)
#         for sample in jm.sample_list:
#             rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample]['ec50'])
#             rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample]['h'])
#             rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample]['Vmax'])
#             rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample]['titer'])
            
#         rowList.append(rowAdd)

#     df = pd.DataFrame(rowList, columns = headerList)
#     a = df.columns.str.split(', ', expand=True).values
#     df.columns = pd.MultiIndex.from_tuples([('', x[0]) if pd.isnull(x[1]) else x for x in a])
#     df.to_excel(writer, sheet_name="Result Analysis")

#     writer.close()

#     output.seek(0)
#     response = make_response(send_file(output, download_name='reportFRNTresults' + str(datetime.now().strftime('%Y_%m_%d')) +'.xlsx', as_attachment=True))
#     response.headers['cache-control'] = 'no-cache'
#     return response
# # This produces the report Viruses X Sera /\ /\ /\ /\  ##    