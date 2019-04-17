from flask import Flask, request, redirect, render_template
from datetime import datetime
import json
from tempfile import NamedTemporaryFile

from jaspr import app
from jaspr.model import JasprModel
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
