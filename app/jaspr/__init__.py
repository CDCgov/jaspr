"""Main application package."""
from flask import Flask
from flask_session import Session
# from flask_debugtoolbar import DebugToolbarExtension
from openpyxl import Workbook
import redis
import os
import glob


app = Flask(__name__)
app.secret_key = b'HoleyMoleyRocky'
app.config['TESTING'] = True
app.config['SESSION_TYPE'] = 'redis'
redis_host = os.getenv("REDIS_HOST", "redis")  # "redis" in multi-container; "127.0.0.1" in single-container
app.config['SESSION_REDIS'] = redis.from_url(f"redis://{redis_host}:6379")

#allow intercepts without stopping while debugging
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug=True

#delete png files in temp directory
print("deleting files")
files = glob.glob('tmp/*.png')
for f in files:
    print(f)
    os.remove(f)

Session(app)
# toolbar = DebugToolbarExtension(app)

#put these at the end (per Flask Documentation)
import jaspr.routes