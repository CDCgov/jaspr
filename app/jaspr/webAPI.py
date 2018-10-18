from flask import Flask, request, redirect, session
from jaspr import app
from datetime import datetime

@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
   if request.method == 'POST':
      f = request.files['file']
      #f.save(os.path.join(jaspr.UPLOAD_FOLDER, jaspr.CURRENT_DATA_FILE))
   return redirect("/", code=302)

@app.route("/ping", methods = ['GET', 'POST'])
def ping():
    """ Simple function for AJAX test:
    """
    returnStr = "Server Contacted at:" +datetime.utcnow() \
                .strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return returnStr
