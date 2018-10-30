from flask import Flask, request, redirect, session
from datetime import datetime
import json,tempfile

from jaspr import app
from jaspr.sessionController import SessionController
from jaspr.standardImport import StandardImport_CSV
from jaspr.model import JasprModel

@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
   #todo read dilution values from settings
   dilutionValues = [2.5e-2, 1.25e-2, 6.25e-3, 3.125e-3, 1.5625e-3, 7.8125e-4,
                     3.90625e-4, 1.953125e-4, 9.765625e-5, 4.8832813e-5, 0]
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
      #todo we probably have to update session data there
      #todo: delete temporary files
   return redirect("/", code=302)

@app.route("/ping", methods = ['GET', 'POST'])
def ping():
    """ Simple function for AJAX test:
    """
    returnStr = "Server Contacted at:" +datetime.utcnow() \
                .strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return json.dumps(returnStr)
