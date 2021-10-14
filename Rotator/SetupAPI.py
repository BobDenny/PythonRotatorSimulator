# pylint: disable=C0301,C0103,C0111
# ==========================
# ALPACA HTML MANAGEMENT API
# ==========================
# 15-Jul-2020   rbd     Flask-RestPlus is dead -> Flask-RestX
# 23-Jan-2021   rbd     0.8 Version strings for form footers etc now in shr module
# 17-Jan-2021   rbd     0.8 /setup endpoints are GET only (no POST)
# 13-Oct-2021   rbd     0.9 Linting with some messages disabled, no docstrings

from flask import  Blueprint, abort, render_template, make_response, flash
from flask_restx import Api, Resource, fields
import RotatorAPI
import shr
from forms import SvrSetupForm, DevSetupForm    # Provides web-based setup UI for the server

html_blueprint = Blueprint('Setup', __name__,
                      url_prefix='',
                      static_folder='static')

#
# Set up the  Flask-RESTX api for Setup and use the above
# blueprint to establish the endpoint prefix.
#
# This puts the Swagger UI for the HTML Browser UI on '/html/' leaving '/' and '/setup' open
api = Api(default='',
            doc='/html/',
            default_label='<h2>ASCOM Alpaca HTML Browser UI: Base URL = <tt>/</tt>',
            contact='Bob Denny, DC-3 Dreams, SP',
            contact_email='rdenny@dc3.com',
            version='Exp. 1.0')

api.init_app(html_blueprint,
            version = '1.0',
            title='ASCOM Alpaca HTML Browser UI',
            description=
'<div><a href=\'https://ascom-standards.org/Developer/Alpaca.htm\' target=\'_new\'>' +
'<img src=\'/static/AlpacaLogo128.png\' align=\'right\' width=\'128\' height=\'101\' /></a>' +
'<h2>This API enables Alpaca devices to be managed</h2>\r\n' +
'<a href=\'https://ascom-standards.org/Developer/ASCOM%20Alpaca%20API%20Reference.pdf\' target=\'_new\'>' +
    'View the ASCOM Alpaca API Reference (PDF)</a><br /><br />\r\n' +
'<a href=\'https://ascom-standards.org/api/?urls.primaryName=ASCOM%20Alpaca%20Management%20API\' target=\'_new\'>' +
'Try out the official live ASCOM Alpaca Management API (Swagger)</a><br /><br /></div>')

m_ErrorMessage = api.model(shr.s_FldErrMsg, {shr.s_FldValue : fields.String(description=shr.s_DescErrMsg, required=True)})

@api.route('/setup/', methods=['GET']) # The trailing / is vital
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class svrsetup(Resource):

    @api.doc(description='Primary browser web page for the overall collection of devices. ' +
                         'To access this use the <a href=\'/setup\'>HTML Interface</a>, not this Swagger UI')
    def get(self):
        setup_form = SvrSetupForm()
        response = make_response(render_template('/svrsetup.html',
                    form=setup_form,
                    template='form_page',
                    title='Settings for the Server',
                    nDev=RotatorAPI.nRot,                   # For Jinja to render the device stuff
                    rDev=RotatorAPI.rRot,
                    verFooter=shr.m_DriverVersion + ' ' + shr.m_DriverVerDate))
        #
        # Maybe there's a better way, but I wanted Flask-RESTX to make the
        # Swagger UI for the HTML Setup endpoints, so I needed to force the
        # content-type over to text/html.  (typ.)
        #
        response.headers['Content-Type'] = 'text/html'
        return response

    @api.doc(description='Primary browser web page for the overall collection of devices. ' +
                         'To access this use the <a href=\'/\'>HTML Interface</a>, not this Swagger UI')
    def post(self):
        setup_form = SvrSetupForm()                         # FlaskForm auto-loads the form from a POST (typ.)
        response = make_response(render_template('/svrsetup.html',
                    form=setup_form,
                    template='form_page',
                    title='Server Settings'))
        response.headers['Content-Type'] = 'text/html'
        return response


@api.route('/setup/v1/rotator/<int:DeviceNumber>/setup', methods=['GET'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class devsetup(Resource):

    @api.doc(description='Web page user interface that enables device specific configuration to be set ' +
                         'for each available device. This must be implemented, even if the response to ' +
                         'the user is that the device is not configurable. ' +
                         'To access this use the <a href=\'/\'>HTML Interface</a>, not this Swagger UI')
    def get(self, DeviceNumber):
        if not DeviceNumber in RotatorAPI.rRot:
            abort(400, shr.s_Resp400NoDevNo)
        rotDev = RotatorAPI.RotDev[DeviceNumber]
        setup_form = DevSetupForm()
        setup_form.reverse.data = rotDev.reverse
        setup_form.step_size.data = rotDev.step_size
        setup_form.steps_sec.data = rotDev.steps_per_sec
        response = make_response(render_template('/devsetup.html',
                    form=setup_form,
                    template='form_page',
                    title='Settings for Rotator #' + str(DeviceNumber),
                    nDev=RotatorAPI.nRot,                       # For Jinja to render the device stuff (typ)
                    rDev=RotatorAPI.rRot,
                    sDev=DeviceNumber,
                    verFooter=shr.m_DriverVersion + ' ' + shr.m_DriverVerDate))
        response.headers['Content-Type'] = 'text/html'
        return response

    @api.doc(description='Web page user interface that enables device specific configuration to be set ' +
                         'for each available device. This must be implemented, even if the response to ' +
                         'the user is that the device is not configurable. ' +
                         'To access this use the HTML Interface, not this Swagger UI')
    def post(self, DeviceNumber):
        if not DeviceNumber in RotatorAPI.rRot:
            abort(400, shr.s_Resp400NoDevNo)
        rotDev = RotatorAPI.RotDev[DeviceNumber]
        setup_form = DevSetupForm()                             # FlaskForm auto-loads the form from a POST
        if setup_form.validate_on_submit():
            rotDev.reverse = setup_form.reverse.data
            rotDev.step_size = setup_form.step_size.data
            rotDev.steps_per_sec = setup_form.steps_sec.data
            flash('Settings successfully updated')
        response = make_response(render_template('/devsetup.html',
                    form=setup_form,
                    template='form_page',
                    title='Settings for Rotator #' + str(DeviceNumber),
                    nDev=RotatorAPI.nRot,                       # For Jinja to render the device stuff
                    rDev=RotatorAPI.rRot,
                    sDev=DeviceNumber,
                    verFooter=shr.m_DriverVersion + ' ' + shr.m_DriverVerDate))
        response.headers['Content-Type'] = 'text/html'
        return response
