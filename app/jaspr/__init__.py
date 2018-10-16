"""Main application package."""
from flask import Flask, session
from flask_session import Session
from flask_debugtoolbar import DebugToolbarExtension

SESSION_TYPE = 'FileSystemSessionInterface'
SESSION_FILE_THRESHOLD = 30
app = Flask(__name__)
app.config['TESTING'] = True
app.secret_key = b'HoleyMoleyRocky'
app.config['SESSION_TYPE'] = 'filesystem'
app.debug=True

Session(app)
toolbar = DebugToolbarExtension(app)

#put these at the end (per Flask Documentation)
import jaspr.webUI
import jaspr.webAPI
