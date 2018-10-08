"""Main application package."""
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
#TODO: take this last stuff out when ready to deploy to production use
app.config['SECRET_KEY']="pleasedonttellme"
toolbar = DebugToolbarExtension(app)
import jaspr.webUI
