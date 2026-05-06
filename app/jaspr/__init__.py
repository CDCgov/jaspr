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

# Session storage:
#   * If REDIS_HOST is set (multi-container deploy), try Redis and fall back
#     to filesystem when Redis is unreachable.
#   * If REDIS_HOST is unset (single-container / Singularity / Apptainer),
#     skip Redis entirely so we don't pay the connect timeout.
#   * Filesystem sessions live under /tmp, which is the only path reliably
#     writable as a non-root user across Docker, Podman, and Singularity.
_session_file_dir = os.getenv("JASPR_SESSION_DIR", "/tmp/flask_session")
redis_host = os.getenv("REDIS_HOST")
_use_redis = False
if redis_host:
    try:
        redis_client = redis.from_url(
            f"redis://{redis_host}:6379",
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        redis_client.ping()
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_REDIS'] = redis_client
        _use_redis = True
    except redis.RedisError:
        _use_redis = False

if not _use_redis:
    try:
        os.makedirs(_session_file_dir, exist_ok=True)
    except OSError:
        # Final fallback: in-process cookie session.  Last resort for
        # extremely locked-down read-only environments.
        _session_file_dir = None
    if _session_file_dir:
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SESSION_FILE_DIR'] = _session_file_dir
        app.config['SESSION_PERMANENT'] = False

#allow intercepts without stopping while debugging
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug=True

# Best-effort cleanup of any stray chart png temp files.  Wrapped in
# try/except so a read-only or non-existent path never breaks startup.
try:
    for f in glob.glob('/tmp/jaspr_*.png'):
        try:
            os.remove(f)
        except OSError:
            pass
except Exception:
    pass

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