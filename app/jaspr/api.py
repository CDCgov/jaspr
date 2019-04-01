from flask import Flask, request, redirect, render_template
from datetime import datetime
import json
from tempfile import NamedTemporaryFile

from jaspr import app
from jaspr.model import JasprModel
from outlet import ParserRegistry


@app.route('/updateConfigSetting', methods=['POST'])
def updateConfigSetting():
    jm = JasprModel()
    print(request.form)
    for k, v in request.form.items():
        jm.update_attribute(k, v)
    return 'true'


@app.route('/uploader', methods = ['POST'])
def uploader():
    if request.method == 'POST':
        df = request.files['datafile']
        df_temp = NamedTemporaryFile(delete=False, dir=app.TEMPFILEDIR)
        df_temp.close()
        df.save(df_temp.name)

        kf = request.files['keyfile']
        kf_temp = NamedTemporaryFile(delete=False, dir=app.TEMPFILEDIR)
        kf_temp.close()
        kf.save(kf_temp.name)

        settings = ParserRegistry.plugins['large_fra'](
                kf_temp.name, df_temp.name)()
        jm = JasprModel().set_defaults(settings)
    return redirect("/", code=302)
   

@app.route("/ping", methods = ['GET'])
def ping():
    """Simple function for AJAX test"""
    returnStr = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return json.dumps(returnStr)
