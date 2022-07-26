# pylint: disable=C0301,C0103,C0111
# =================================================================================================
# ASCOM Alpaca Rotator Simulator - Main Program & Revision Log
#
# Written By:   Robert B. Denny <rdenny@dc3.com>
#
# 24-Nov-2018   rbd Initial edit
# 08-Dec-2018   rbd Changes per Alpaca finalization, complete Conform test on Raspberry Pi
# 09-Mar-2019   rbd Refactor strings, add max/min values to models, 12-bit errors, cosmetics
#                   on Swagger UI
# 10-Mar-2019   rbd Version now 0.2. Hide the X-Fields mechanism from Swagger, not used here.
#                   Start the Swagger already showing the list. Looking good now. Passed
#                   Conform via ASCOM Remote. Other cosmetics.
# 12-Mar-2019   rbd Version 0.3 Make all query string and PUT/form data item retrieval
#                   have case-insensitive names. Remove repeated dead code except in Connected as
#                   examples.
# 13-Mar-2019   rbd Version 0.4 Make the parameters such as ClientTransactionId optional, and
#                   prevent them from showing in response as null if completely missing.
# 14-Mar-2019   rbd Version 0.5 Tidying. Not going with PEP-8 here. s_ are strings, m_ are models.
# 15-Mar-2019   rbd Version 0.5 (cont) Always return ClientID and ClientTransactionID even if not
#                   in the request, and in that case return 0.
# 17-Mar-2019   rbd Version 0.5 (cont) actually 2 days with the setup form, getting it 'right'
# 30-Oct-2019   rbd Version 0.6 Add discovery protocol responder, massive refactoring, no longer
#                   'simple' as we now have a discovery responder will be adding the management API
# 31-Oct-2019   rbd Version 0.6 (cont) MAJOR refactoring, cross-thread server trans ID, changing the
#                   browser setup and adding the management API. Add optional production WSGI server
#                   'gevent.WSGIServer' see https://stackoverflow.com/a/53918402. Fix pass-through
#                   of ClientTransactionID on method responses (was always 0). PASSES CONFORM.
# 01-Nov-2019   rbd Version 0.6 (cont) Correct Swagger 200 decscriptions on all GET methods in the
#                   Rotator API. Implement JSON Management API. Pick up stray cosmetics. Start
#                   HTML Browser UI
# 15-Jul-2020   rbd Version 0.7 Changes needed to migrate from the now dead Flask-RestPlus to the
#                   "drop-in-replacement" Flask-RestX.
# 23-Jan-2021   rbd Version 0.8 Add dynamic version footer to HTML setup pages. Make the select
#                   dropdown for selecting which device to set up work (was stubbed out).
# 12-Oct-2021   rbd Version 0.9 PyLint (VSCode Linux) corrections. No more Lint warnings. shr module
#                   no longer has init().
# 20-Jul-2022   rbd Version 1.0 Upgraded discovery. Testing with the latest of the packages out there.
#                   Repo moved from DC-3 Dreams private git server to GitHub  for eventual release
#                   as ASCOM Initiative sample. f-strings (modern me!)
# =================================================================================================

# ===============================
# https://ascom-standards.org/api
# ===============================
#
# References for the Flask web service and Flask-REST-X framework
#       https://flask.palletsprojects.com/
#       https://github.com/python-restx/flask-restx
#       https://flask-restx.readthedocs.io/en/latest/
# Strongly recommended Flask training, free, concise, and easy to understand.
# See the Building Flask Apps table of contents right under the main graphic.
#       https://hackersandslackers.com/creating-your-first-flask-application/
# Note particularly
#       https://hackersandslackers.com/serving-static-assets-in-flask/
#       https://hackersandslackers.com/guide-to-building-forms-in-flask
# And there's always Miguel Grinberg:
#       https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
# Also you should be aware of this 'awesome' resource (haha)
#       https://github.com/humiaozuzu/awesome-flask
# For the "production" WSGI webserver 'gevent' see
#       http://www.gevent.org/api/gevent.pywsgi.html
#

import os
import logging
from flask import Flask, render_template

# -----------------------------
# Shared vriables and functions
# -----------------------------
import shr

# -----------
# Rotator API (this hooks to simulator)
#------------
import RotatorAPI

# --------------
# Management API
#---------------
import ManagementAPI

# --------------
# HTML Setup API
#---------------
import SetupAPI

# -------------------
# Discovery responder
# -------------------
import DiscoveryResponder

# ----------------------
# Production server only
# ----------------------
# Uncomment if using gevent/WSGIServer, see the SERVER APPLICAITION section below
# from gevent.pywsgi import WSGIServer

#import ASCOMErrors                                     # All Alpaca Devices

# -----------------
# Network Connection
# ----------------
if os.name == 'nt':                                     # This is really Windows (my dev system eh?)
    HOST = '127.0.0.1'
    MCAST = '127.0.0.255'
    print(f' * Running on Windows for Development... {HOST}')
    print(f' * Assuming broadcast address is {MCAST}')
else:
#
# Unbelievable what you need to do to get your live IP address
# on Linux (which one????) and even more fun to know the 
# correct multicast address. This is a sample so I just hard code
# both here. See ipsddress and netifaces if you want some fun.
#
    HOST = '192.168.0.42'                               # Your device's IP(V4) address
    MCAST = '192.168.0.255'                             # Discovery: Depends on your CIDR block
    print(f' * Assuming run on Raspberry Pi Linux {HOST}')
PORT = 5555                                             # Port on which the device responds

sprt = str(PORT)
print(f' * Simulator accessible via Alpaca at {HOST}:{sprt}')
print(f'   For mangement home page http://{HOST}:{sprt}/')

_DSC = DiscoveryResponder.DiscoveryResponder(MCAST, HOST, PORT)


# ===============================
# FLASK SERVER AND REST FRAMEWORK
# ===============================

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
# needed for session (flash queue uses this), CSRF protection
app.config['FLASK_ENV'] = 'development'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'we-did-it-for-harambe'
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'        # Open Swagger with list displayed by default
app.config['RESTX_MASK_SWAGGER'] = False    # Not used in our device, so hide this from Swagger

# ----------
# Index page
# ----------
# Rendering depends on the RotatorAPI being initialized
# But it must come first to avoid having / overridden
#
@app.route('/')             # Must precede others or won't be recognized
def index():
    return render_template('/index.html',
                    title='Alpaca Rotator Simulator (Python 3 / Flask)',
                    nDev=RotatorAPI.nRot,   # For Jinja to render the device stuff
                    rDev=RotatorAPI.rRot,
                    verFooter=shr.m_DriverVersion + ' ' + shr.m_DriverVerDate)
# -----------------
# Register our APIs
# -----------------
app.register_blueprint(RotatorAPI.rot_blueprint)
app.register_blueprint(ManagementAPI.mgmt_blueprint)
app.register_blueprint(SetupAPI.html_blueprint)

log = logging.getLogger('werkzeug')     # Webserver used by Flask (dev/small server)
log.setLevel(logging.ERROR)             # Prevent successful HTTP traffic from being logged

# ==================
# SERVER APPLICATION
# ==================
#
# Start it this way to get the automatic tab on Chrome
# with the right host/port.
#
if __name__ == '__main__':
    #
    # -----------
    # Development
    # -----------
    # (built-in Werkzeug)
    #
    app.run(HOST, PORT)
    #
    # ----------
    # Production
    # ----------
    # You probably want to alter logging, it's going to the console by default
    # http://www.gevent.org/api/gevent.pywsgi.html
    #
    #http_server = WSGIServer((HOST, PORT), app)
    #http_server.serve_forever()
