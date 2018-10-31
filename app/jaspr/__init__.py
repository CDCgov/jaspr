"""Main application package."""
SESSION_TYPE = 'FileSystemSessionInterface'
SESSION_FILE_THRESHOLD = 30
PERMANENT_SESSION_LIFETIME = 600

from flask import Flask, session
from flask_session import Session
from flask_debugtoolbar import DebugToolbarExtension


app = Flask(__name__)
app.config['TESTING'] = True
app.secret_key = b'HoleyMoleyRocky'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug=True
app.TEMPFILEDIR="temp"
#allow intercepts without stopping while debugging


Session(app)
toolbar = DebugToolbarExtension(app)

#put these at the end (per Flask Documentation)
import jaspr.webUI
import jaspr.webAPI
