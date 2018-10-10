"""Main application package."""
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

UPLOAD_FOLDER = '/app/uploads'
CURRENT_DATA_FILE = 'currentdata.xlsx'

#put these at the end (per Flask Documentation)
import jaspr.webUI
import jaspr.webAPI

#TODO: take this last stuff out when ready to deploy to production use
app.config['SECRET_KEY']="pleasedonttellme"
toolbar = DebugToolbarExtension(app)
