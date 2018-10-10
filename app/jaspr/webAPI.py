#!/usr/bin/env python
# file webAPI.py
import os
from flask import Flask, request, redirect
from jaspr import app, UPLOAD_FOLDER, CURRENT_DATA_FILE


@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
   if request.method == 'POST':
      f = request.files['file']
      f.save(os.path.join(jaspr.UPLOAD_FOLDER, jaspr.CURRENT_DATA_FILE))
   return redirect("/", code=302)

@app.route("/ping")
def ping():
 """ Simple function for AJAX test:
 """
 global pinging
 returnStr = "";
 if pinging:
     pinging = False;
     returnStr = "Pong"
 else:
     pinging = True;
     returnStr = "Ping"
 return returnStr
