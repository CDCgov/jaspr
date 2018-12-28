from flask import Flask, request, redirect, session,render_template
from datetime import datetime
import json,tempfile

from jaspr import app
from jaspr.sessionController import SessionController
from jaspr.standardImport import StandardImport_CSV
from jaspr.Model.model import JasprModel

@app.route('/updateConfigSetting', methods =['POST'])
def updateConfigSetting():
    showCurveFit=request.form.get('showCurveFit','notFound')
    #todo: DRY  this code
    if showCurveFit != 'notFound':
        key = 'showCurveFit'
    blankCorrection=request.form.get('blankCorrection','notFound')
    if blankCorrection != 'notFound':
        key = 'blankCorrection'
    axisScale=request.form.get('axisScale','notFound')
    if axisScale !='notFound':
        key = 'axisScale'
    selectedAlgorithm=request.form.get('selectedAlgorithm','notFound')
    if selectedAlgorithm !='notFound':
        key = 'selectedAlgorithm'
    value = request.form.get(key)
    print("updateConfigSetting: Set value {} to {}".format(key, value))
    sc = SessionController()
    model = sc.getModel()
    model._jasprConfig.setConfigSetting(key,value)
    sc.loadSessionFromModel()
    return "success"

@app.route('/uploader', methods = ['POST'])
def uploader():
   #todo read dilution values from settings
   #todo Note that we converted a zero to a "near zero for this to work"
   dilutionValues = [2.5e-2, 1.25e-2, 6.25e-3, 3.125e-3, 1.5625e-3, 7.8125e-4,
                     3.90625e-4, 1.953125e-4, 9.765625e-5, 4.8832813e-5, 1e-6]
   if request.method == 'POST':
      datafile_req = request.files['datafile']
      datafile_temp = tempfile.NamedTemporaryFile(delete=False,dir=app.TEMPFILEDIR)
      datafile_temp.close()
      datafile_req.save(datafile_temp.name)

      keyfile_req = request.files['keyfile']
      keyfile_temp = tempfile.NamedTemporaryFile(delete=False,dir=app.TEMPFILEDIR)
      keyfile_temp.close()
      keyfile_req.save(keyfile_temp.name)

      sc = SessionController()
      jm = sc.getModel()
      si = StandardImport_CSV(dilutionValues,jm)
      si.loadPlate(datafile_temp.name,keyfile_temp.name)
      #datafile_temp.delete()
      #keyfile_temp.delete()
      sc.loadSessionFromModel()
      sc.resetUISession()
      # print("\n\n\nIn uploader")
      # for item in session:
      #     print(item, "-->",session[item])
      # print("So that is what you should see\n\n\n")
      #todo we probably have to update session data there
      #todo: delete temporary files
   return redirect("/", code=302)

@app.route("/ping", methods = ['GET'])
def ping():
    """ Simple function for AJAX test:
    """
    returnStr = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return json.dumps(returnStr)
