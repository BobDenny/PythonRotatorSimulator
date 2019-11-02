# ==========================
# ALPACA HTML MANAGEMENT API
# ==========================

from flask import Flask, Blueprint, request, response, abort, render_template, flash
from flask_restplus import Api, Resource, fields
import ASCOMErrors                                      # All Alpaca Devices
import RotatorAPI
import shr

html_blueprint = Blueprint('Setup', __name__, 
                      url_prefix='/setup',
                      static_folder='static')

#
# Set up the  Flask-RESTPlus api for Setup and use the above 
# blueprint to establish the endpoint prefix.
#
api = Api(default='setup', 
            default_label='<h2>ASCOM Alpaca HTML Browser UI: Base URL = <tt>/setup</tt>',
            contact='Bob Denny, DC-3 Dreams, SP',
            contact_email='rdenny@dc3.com',
            version='Exp. 1.0')

api.init_app(html_blueprint, 
            version = '1.0',
            title='ASCOM Alpaca HTML Browser UI', 
            description='<div><a href=\'https://ascom-standards.org/Developer/Alpaca.htm\' target=\'_new\'>'+
                '<img src=\'static/AlpacaLogo128.png\' align=\'right\' width=\'128\' height=\'101\' /></a>'+ 
                '<h2>This API enables Alpaca devices to be managed</h2>\r\n' +
                '<a href=\'https://ascom-standards.org/Developer/ASCOM%20Alpaca%20API%20Reference.pdf\' target=\'_new\'>' +
                    'View the ASCOM Alpaca API Reference (PDF)</a><br /><br />\r\n' + 
                '<a href=\'https://ascom-standards.org/api/?urls.primaryName=ASCOM%20Alpaca%20Management%20API\' target=\'_new\'>' +
                'Try out the official live ASCOM Alpaca Management API (Swagger)</a><br /><br /></div>')

m_ErrorMessage = api.model(shr.s_FldErrMsg, {shr.s_FldValue : fields.String(description=shr.s_DescErrMsg, required=True)})

from forms import SetupForm                             # Provides web-based setup UI for the rotator
@api.route('/v1/rotator/<int:DeviceNumber>/setup', methods=['GET', 'POST'])
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class devsetup(Resource):

    @api.doc(description='Web page user interface that enables device specific configuration to be set for each available device. This must be implemented, even if the response to the user is that the device is not configurable.')
    def get(self, DeviceNumber):
        if DeviceNumber != 0:
            abort(400, shr.s_Resp400NoDevNo)
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

