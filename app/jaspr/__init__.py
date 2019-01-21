"""Main application package."""
from flask import Flask, session
from flask_session import Session
from flask_debugtoolbar import DebugToolbarExtension
import redis

app = Flask(__name__)
app.config['TESTING'] = True
app.secret_key = b'HoleyMoleyRocky'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://redis:6379')
#allow intercepts without stopping while debugging
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug=True
app.TEMPFILEDIR="temp"
Session(app)
toolbar = DebugToolbarExtension(app)

#put these at the end (per Flask Documentation)
import jaspr.webUI
import jaspr.webAPI
