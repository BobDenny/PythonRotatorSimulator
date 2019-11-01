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
#                   pf ClientTransactionID on methos responses (was always 0).
# =================================================================================================

#
# https://ascom-standards.org/api
# http://flask.pocoo.org/docs/1.0/
# https://flask-restplus.readthedocs.io/en/stable/index.html
#
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
from flask import Flask, Blueprint, request, abort, make_response, render_template, flash
from flask_restplus import Api, Resource, fields
from gevent.pywsgi import WSGIServer

import ASCOMErrors                                      # All Alpaca Devices

import shr                                              # Thread-safe shared vars
shr.init()

# -----------------
#Network Connection
# ----------------
if os.name == 'nt':                                     # This is really Windows (my dev system eh?)
    HOST = '127.0.0.1'
    print(' * Running on Windows... ' + HOST)
else:
    HOST = '192.168.0.40'                               # Unbelievable what you need to do to get your live IP address on Linux (which one????)
    print(' * Assuming run on Raspberry Pi Linux ' + HOST)
PORT = 5555                                             # Port on which Alpaca interface(s) respond

# -------------------
# Discovery responder
# -------------------
import DiscoveryResponder
_DSC = DiscoveryResponder.DiscoveryResponder(HOST, PORT)

# --------------------------------
# Rotator API and Device Simulator (self-starting thread)
#---------------------------------
import RotatorAPI

# ===============================
# FLASK SERVER AND REST FRAMEWORK
# ===============================

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
# needed for session (flash queue uses this), CSRF protection
app.config['FLASK_ENV'] = 'development'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'we-did-it-for-harambe'
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'        # Open Swagger with list displayed by default
app.config['RESTPLUS_MASK_SWAGGER'] = False         # Not used in our device, so hide this from Swagger

# -----------------
# Register our APIs
# -----------------
app.register_blueprint(RotatorAPI.rot_blueprint)

import logging
log = logging.getLogger('werkzeug')                 # Webserver used by Flask (dev/small server)
log.setLevel(logging.ERROR)                         # Prevent successful HTTP traffic from being logged


# ======================
# BROWSER MANAGEMENT API
# ======================
#
# Need full path as this is not running through the blueprinted FRP REST api
# Simplified yet CSRF protected via Flask-WTF and its FlaskForm
#
from forms import SetupForm                             # Provides web-based setup UI for the rotator
@app.route('/setup/v1/rotator/0/setup', methods=['GET', 'POST'])
def setup():
    _ROT = RotatorAPI._ROT
    setup_form = SetupForm()                            # FlaskForm auto-loads the form from a POST
    if setup_form.validate_on_submit():
        _ROT.reverse = setup_form.reverse.data
        _ROT.step_size = setup_form.step_size.data
        _ROT.steps_per_sec = setup_form.steps_sec.data
        flash('Settings successfully updated')

    setup_form.reverse.data = _ROT.reverse
    setup_form.step_size.data = _ROT.step_size
    setup_form.steps_sec.data = _ROT.steps_per_sec

    return render_template('/setup.html', 
                form=setup_form, 
                template='form_page',
                title='Rotator Simulator Setup Form')


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

