from flask import Flask, request, redirect, session
from jaspr import app

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
    returnStr = "";
    NOT_SET='not set'
    pingValue = session.get('pingvalue', NOT_SET)
    if pingValue == NOT_SET:
        session['pingvalue']=False
        pingValue=False
    if pingValue:
        session['pingvalue'] = False;
        returnStr = "Pong"
    else:
        session['pingvalue'] = True;
        returnStr = "Ping"
    session.modified = True
    return returnStr
