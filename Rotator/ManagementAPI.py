# ==========================
# ALPACA JSON MANAGEMENT API
# ==========================

from flask import Flask, Blueprint, request, abort
from flask_restplus import Api, Resource, fields
import ASCOMErrors                                      # All Alpaca Devices
import shr

mgmt_blueprint = Blueprint('Management', __name__, 
                      url_prefix='/management',
                      static_folder='static')

#
# Set up the  Flask-RESTPlus api for Management and use the above 
# blueprint to establish the endpoint prefix.
#
api = Api(default='management', 
            default_label='<h2>ASCOM Alpaca Management API (JSON): Base URL = <tt>/management</tt>',
            contact='Bob Denny, DC-3 Dreams, SP',
            contact_email='rdenny@dc3.com',
            version='Exp. 1.0')

api.init_app(mgmt_blueprint, 
            version = '1.0',
            title='ASCOM Alpaca Management API (JSON)', 
            description='<div><a href=\'https://ascom-standards.org/Developer/Alpaca.htm\' target=\'_new\'>'+
                '<img src=\'static/AlpacaLogo128.png\' align=\'right\' width=\'128\' height=\'101\' /></a>'+ 
                '<h2>This API enables Alpaca devices to be managed</h2>\r\n' +
                '<a href=\'https://ascom-standards.org/Developer/ASCOM%20Alpaca%20API%20Reference.pdf\' target=\'_new\'>' +
                    'View the ASCOM Alpaca API Reference (PDF)</a><br /><br />\r\n' + 
                '<a href=\'https://ascom-standards.org/api/?urls.primaryName=ASCOM%20Alpaca%20Management%20API\' target=\'_new\'>' +
                'Try out the official live ASCOM Alpaca Management API (Swagger)</a><br /><br /></div>')

# ============================
# Models and their Static Data
# ============================

m_ErrorMessage = api.model(shr.s_FldErrMsg, {shr.s_FldValue : fields.String(description=shr.s_DescErrMsg, required=True)})

# -----------------------------
# For the /apiversions endpoint
# -----------------------------
m_IntArrayResponse  = api.model('IntArrayResponse', 
                    {   shr.s_FldValue      : fields.List(fields.Integer, description='Array of integer values.', required=True),
                        shr.s_FldCtId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescCtId),
                        shr.s_FldStId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescStId),
                        shr.s_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=shr.s_DescErrNum),
                        shr.s_FldErrMsg     : fields.String(description=shr.s_DescErrMsg)
                    })

# --------------------------------
# For the /v1/description endpoint
# --------------------------------
s_FldSvrName    = 'ServerName'
s_FldManuf      = 'Manufacturer'
s_FldManufVers  = "ManufacturerVersion"
s_FldLocation   = 'Location'

m_Description       = api.model('Description', 
                    {   
                        s_FldSvrName        : fields.String(description='The device or server\'s overall name.'),
                        s_FldManuf          : fields.String(description='The manufacturer\'s name.'),
                        s_FldManufVers      : fields.String(description='The device or server\'s version number.'),
                        s_FldLocation       : fields.String(description='The device or server\'s location.')
                    })

m_DescriptionResponse = api.model('DescriptionResponse',
                    {   shr.s_FldValue      : fields.Nested(m_Description, skip_none=True),
                        shr.s_FldCtId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescCtId),
                        shr.s_FldStId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescStId),
                        shr.s_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=shr.s_DescErrNum),
                        shr.s_FldErrMsg     : fields.String(description=shr.s_DescErrMsg)
                    })

# --------------------------------------
# For the /v1/configureddevices endpoint
# --------------------------------------
s_FldDevName    = 'DeviceName'
s_FldDevType    = 'DeviceType'
s_FldDevNum     = 'DeviceNumber'
s_FldUniqId     = 'UniqueID'

m_DeviceConfiguration       = api.model('DeviceConfiguration', 
                    {   
                        s_FldDevName        : fields.String(description='A short name for this device that a user would expect to see in a list of available devices.'),
                        s_FldDevType        : fields.String(description='One of the supported ASCOM Devices types such as Telescope, Camera, Focuser etc.'),
                        s_FldDevNum         : fields.Integer(description='The device number that must be used to access this device through the Alpaca Device API.'),
                        s_FldUniqId         : fields.String(description='This should be the ProgID for COM devices or a GUID for native Alpaca devices. The GUID identifies a particular type of hardware device, it does not have to be different for every user of that hardware device. For example, the GUID for "SuperSwish Focuser" would be the same for all people who purchased that focuser, but would be different to the GUID for the "SuperSwish FilterWheel".')
                    })

m_ConfiguredDevicesResponse = api.model('ConfiguredDevicesResponse',
                    {   shr.s_FldValue      : fields.List(fields.Nested(m_DeviceConfiguration, skip_none=True)),
                        shr.s_FldCtId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescCtId),
                        shr.s_FldStId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescStId),
                        shr.s_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=shr.s_DescErrNum),
                        shr.s_FldErrMsg     : fields.String(description=shr.s_DescErrMsg)
                    })


# ==============
# MANAGEMENT API
# ==============

# -----------
# APIVersions
# -----------
#
@api.route('/apiversions', methods=['GET']) 
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class apiversions(Resource):

    @api.doc(description='An integer array of supported Alpaca API version numbers.')
    @api.marshal_with(m_IntArrayResponse, description='Integer array of supported Alpaca API versions', skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self):
        R = shr.PropertyResponse(shr.m_DriverAPIVersions, request.args)
        return vars(R)

# -----------
# Description
# -----------
# This is the actual static description data we return
#
DescData =  {
                s_FldSvrName        : 'Alpaca Rotator Simulator',
                s_FldManuf          : 'Robert B. Denny <rdenny@dc3.com>',
                s_FldManufVers      : shr.m_DriverVersion,
                s_FldLocation       : "The Great American West"
            }

@api.route('/v1/description', methods=['GET']) 
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class description(Resource):

    @api.doc(description='Returns cross-cutting information that applies to all devices available at this URL:Port.')
    @api.marshal_with(m_DescriptionResponse, description='Cross cutting information that applies to all devices servered through this URL:Port.', skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self):
        R = shr.PropertyResponse(DescData, request.args)
        return vars(R)

# -----------------
# ConfiguredDevices
# -----------------
# This is the actual static description data we return
#
ConfData =  {
                s_FldDevName        : 'Alpaca Rotator Simulator',
                s_FldDevType        : 'Rotator',
                s_FldDevNum         : 0,
                s_FldUniqId         : "5897B4BC-2A4D-4893-8CC0-6A440D6B2D51"
            }

@api.route('/v1/configureddevices', methods=['GET']) 
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class configureddevices(Resource):

    @api.doc(description='Returns an array of device description objects, providing unique information for each served device, enabling them to be accessed through the Alpaca Device API.')
    @api.marshal_with(m_ConfiguredDevicesResponse, description='Array of device description objects, providing unique information for each served device, enabling them to be accessed through the Alpaca Device API.', skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self):
        R = shr.PropertyResponse(ConfData, request.args)
        return vars(R)
