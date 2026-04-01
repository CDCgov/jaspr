"""Main application package."""
from flask import Flask
from flask_session import Session
# from flask_debugtoolbar import DebugToolbarExtension
from bokeh.resources import INLINE
from openpyxl import Workbook
import redis
import os
import glob


app = Flask(__name__)
app.secret_key = b'HoleyMoleyRocky'
app.config['TESTING'] = True
redis_host = os.getenv("REDIS_HOST", "127.0.0.1")  # Override to "redis" in multi-container compose.
redis_client = redis.from_url(f"redis://{redis_host}:6379", socket_connect_timeout=1, socket_timeout=1)

try:
    redis_client.ping()
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = redis_client
except redis.RedisError:
    # Keep the app available even when Redis is unreachable in local/single-container runs.
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'
    app.config['SESSION_PERMANENT'] = False

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


@app.context_processor
def inject_bokeh_resources():
    """Keep browser BokehJS/CSS version aligned with installed Python bokeh."""
    return {
        'bokeh_js_resources': INLINE.render_js(),
        'bokeh_css_resources': INLINE.render_css(),
    }

#put these at the end (per Flask Documentation)
import jaspr.routes