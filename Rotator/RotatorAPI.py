# pylint: disable=C0301,C0103,C0111,W0612
# W0612 Variables devno, cid defined for illustration but not used (see below)
# ==================
# ALPACA ROTATOR API
# ==================
# 15-Jul-2020   rbd FLask-RestPlus is dead -> Flask-RestX
# 13-Oct-2021   rbd 0.9 Linting with some messages disabled, no docstrings
# 18-Oct-2021   rbd 0.9 'interfaceversion' returns an integer, add model
#                   m_IntegerResponse

from flask import Blueprint, request, abort
from flask_restx import Api, Resource, fields
import ASCOMErrors                                      # All Alpaca Devices
import shr
import RotatorDevice                                    # Emulates a physical rotator

#
# Simulate nRot rotators
# ------
nRot = 4
hRot = nRot - 1                                         # High device number
#-------
RotDev = [None] * nRot
rRot = range(0, nRot)
for i in rRot:
    RotDev[i] = RotatorDevice.RotatorDevice()             # Start it up now

#
# Blueprint to create a URL prefix for the rotator API
#
rot_blueprint = Blueprint('Rotator', __name__,
                      url_prefix='/api/v1/rotator',
                      static_folder='static')

#
# Set up the  Flask-RESTX api for Rotator and use the above
# blueprint to establish the endpoint prefix.
#
api = Api(default='rotator',
            default_label='<h2>ASCOM Alpaca API for Rotator Devices: Base URL = <tt>/api/v1/rotator',
            contact='Bob Denny, DC-3 Dreams, SP',
            contact_email='rdenny@dc3.com',
            version='Exp. 1.0')

api.init_app(rot_blueprint,
            version = '1.0',
            title='ASCOM Alpaca Rotator Simulator',
            description='<div><a href=\'https://ascom-standards.org/Developer/Alpaca.htm\' target=\'_new\'>' +
                '<img src=\'/static/AlpacaLogo128.png\' align=\'right\' width=\'128\' height=\'101\' /></a>' +
                '<h2>This device is an ASCOM Rotator simulator that responds to ' +
                'the standard ASCOM Alpaca API for Rotator</h2>\r\n' +
                '<a href=\'https://ascom-standards.org/Developer/ASCOM%20Alpaca%20API%20Reference.pdf\' target=\'_new\'>' +
                    'View the ASCOM Alpaca API Reference (PDF)</a><br /><br />\r\n' +
                '<a href=\'https://ascom-standards.org/api/?urls.primaryName=ASCOM%20Alpaca%20Device%20API\' target=\'_new\'>' +
                'Try out the official live ASCOM Alpaca API (Swagger)</a><br /><br /></div>')




# ==========================
# Models and Wrapper Classes
# ==========================

m_ErrorMessage = api.model(shr.s_FldErrMsg, {shr.s_FldValue : fields.String(description=shr.s_DescErrMsg, required=True)})


m_BoolResponse = api.model('BoolResponse',
            {   shr.s_FldValue      : fields.Boolean(description='True or False value.', required=True),
                shr.s_FldCtId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescCtId),
                shr.s_FldStId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescStId),
                shr.s_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=shr.s_DescErrNum),
                shr.s_FldErrMsg     : fields.String(description=shr.s_DescErrMsg)
            })

m_IntegerResponse = api.model('IntegerResponse',
            {   shr.s_FldValue      : fields.Integer(description='Integer value.', required=True),
                shr.s_FldCtId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescCtId),
                shr.s_FldStId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescStId),
                shr.s_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=shr.s_DescErrNum),
                shr.s_FldErrMsg     : fields.String(description=shr.s_DescErrMsg)
            })

m_FloatResponse = api.model('FloatResponse',
            {   shr.s_FldValue      : fields.Float(description='Double value.', required=True),
                shr.s_FldCtId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescCtId),
                shr.s_FldStId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescStId),
                shr.s_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=shr.s_DescErrNum),
                shr.s_FldErrMsg     : fields.String(description=shr.s_DescErrMsg)
            })

m_StringResponse = api.model('StringResponse',
            {   shr.s_FldValue      : fields.String(description='String value.', required=True),
                shr.s_FldCtId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescCtId),
                shr.s_FldStId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescStId),
                shr.s_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=shr.s_DescErrNum),
                shr.s_FldErrMsg     : fields.String(description=shr.s_DescErrMsg)
            })

m_StringListResponse = api.model('StringListResponse',
                    {   shr.s_FldValue      : fields.List(fields.String(), description='List of string values.', required=True),
                        shr.s_FldCtId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescCtId),
                        shr.s_FldStId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescStId),
                        shr.s_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=shr.s_DescErrNum),
                        shr.s_FldErrMsg     : fields.String(description=shr.s_DescErrMsg)
                    })

m_MethodResponse = api.model('MethodResponse',
                    {   shr.s_FldCtId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescCtId),
                        shr.s_FldStId       : fields.Integer(min=0, max=4294967295, description=shr.s_DescStId),
                        shr.s_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=shr.s_DescErrNum),
                        shr.s_FldErrMsg     : fields.String(description=shr.s_DescErrMsg)
                    })

# ============================
# ALPACA ROTATOR API ENDPOINTS
# ============================

# Note the additonal items retrieved from the request in Connected (typ.)

# ------
# Action
# ------
#
@api.route('/<int:DeviceNumber>/action', methods=['PUT'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class action(Resource):

    @api.doc(description='Invokes the specified device-specific action.')
    @api.marshal_with(m_MethodResponse, description=shr.s_DescMthRsp, skip_none=True)
    @api.param('Action', 'A well known name that represents the action to be carried out.', 'formData', type='string', required=True)
    @api.param('Parameters', 'List of parameters or empty string if none are required.', 'formData', type='string', default='', required=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'formData', type='integer', default=1234)
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        #?# global connected
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        R = shr.MethodResponse(request.form, ASCOMErrors.NotImplementedException)
        return vars(R)

# ------------
# CommandBlind
# ------------
#
@api.route('/<int:DeviceNumber>/commandblind', methods=['PUT'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class commandblind(Resource):

    @api.doc(description='Transmits an arbitrary string to the device and does not wait for a response. ' +
                        'Optionally, protocol framing characters may be added to the string before transmission.')
    @api.marshal_with(m_MethodResponse, description=shr.s_DescMthRsp, skip_none=True)
    @api.param('Command', 'The literal command string to be transmitted.', 'formData', type='string', required=True)
    @api.param('Raw', 'If set to true the string is transmitted \'as-is\', ' +
                      'if set to false then protocol framing characters may be added prior ' +
                      'to transmission', 'formData', type='boolean', default=False, required=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'formData', type='integer', default=1234)
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        #?# global connected
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        R = shr.MethodResponse(request.form, ASCOMErrors.NotImplementedException)
        return vars(R)


# -----------
# CommandBool
# -----------
#
@api.route('/<int:DeviceNumber>/commandbool', methods=['PUT'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class commandbool(Resource):

    @api.doc(description='Transmits an arbitrary string to the device and waits for a boolean response. ' +
                        'Optionally, protocol framing characters may be added to the string before transmission.')
    @api.marshal_with(m_MethodResponse, description=shr.s_DescMthRsp, skip_none=True)
    @api.param('Command', 'The literal command string to be transmitted.', 'formData', type='string', required=True)
    @api.param('Raw', 'If set to true the string is transmitted \'as-is\', ' +
                      'if set to false then protocol framing characters may be added prior ' +
                      'to transmission', 'formData', type='boolean', default=False, required=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'formData', type='integer', default=1234)
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        R = shr.MethodResponse(request.form, ASCOMErrors.NotImplementedException)
        return vars(R)


# -------------
# CommandString
# -------------
#
@api.route('/<int:DeviceNumber>/commandstring', methods=['PUT'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class commandstring(Resource):

    @api.doc(description='Transmits an arbitrary string to the device and waits for a string response. ' +
                        'Optionally, protocol framing characters may be added to the string before transmission.')
    @api.marshal_with(m_MethodResponse, description=shr.s_DescMthRsp, skip_none=True)
    @api.param('Command', 'The literal command string to be transmitted.', 'formData', type='string', required=True)
    @api.param('Raw', 'If set to true the string is transmitted \'as-is\', ' +
                      'if set to false then protocol framing characters may be added prior ' +
                      'to transmission', 'formData', type='boolean', default=False, required=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'formData', type='integer', default=1234)
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        R = shr.MethodResponse(request.form, ASCOMErrors.NotImplementedException)
        return vars(R)


# ---------
# Connected
# ---------
#
@api.route('/<int:DeviceNumber>/connected', methods=['GET','PUT'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class connected(Resource):

    @api.doc(description='Retrieves the connected state of the Rotator.')
    @api.marshal_with(m_BoolResponse, description=shr.s_DescGetRsp, skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default=1234)
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default=1)
    def get(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        devno = DeviceNumber                                              # Used later for multi-device (typ.)
        cid = shr.get_args_caseless(shr.s_FldClId, request.args, 1234)    # Used if need to ident the Client (typ.)
        R = shr.PropertyResponse(RotDev[DeviceNumber].connected, request.args)
        return vars(R)

    @api.doc(description='Sets the connected state of the Rotator.')
    @api.marshal_with(m_MethodResponse, description=shr.s_DescMthRsp, skip_none=True)
    @api.param('Connected', 'Set True to connect to the device hardware. Set False to ' +
                            'disconnect from the device hardware.',
                            'formData', type='boolean', default=False, required=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'formData', type='integer', default=1234)
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        devno = DeviceNumber
        cid = shr.get_form_caseless(shr.s_FldClId, request.form, 1234)
        RotDev[DeviceNumber].connected = (shr.get_form_caseless('Connected', request.form, 'false').lower() == 'true')
        R = shr.MethodResponse(request.form)
        return vars(R)

# -----------
# Description
# -----------
#
@api.route('/<int:DeviceNumber>/description', methods=['GET'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class description(Resource):

    @api.doc(description='Returns a description of the device, such as manufacturer and modelnumber. Any ASCII characters may be used.')
    @api.marshal_with(m_StringResponse, description=shr.s_DescGetRsp, skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        desc = 'Simulated Rotator implemented in Python.'
        R = shr.PropertyResponse(desc, request.args)
        return vars(R)


# ----------
# DriverInfo
# ----------
#
@api.route('/<int:DeviceNumber>/driverinfo', methods=['GET'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class driverinfo(Resource):

    @api.doc(description='Descriptive and version information about this ASCOM driver.')
    @api.marshal_with(m_StringResponse, description=shr.s_DescGetRsp, skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        desc = 'ASCOM Alpaca driver for a simulated Rotator. Experimental V' + shr.m_DriverVersion + ' (Python)'
        R = shr.PropertyResponse(desc, request.args)
        return vars(R)


# -------------
# DriverVersion
# -------------
#
@api.route('/<int:DeviceNumber>/driverversion', methods=['GET'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class driverversion(Resource):

    @api.doc(description='A string containing only the major and minor version of the driver.')
    @api.marshal_with(m_StringResponse, description=shr.s_DescGetRsp, skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        R = shr.PropertyResponse(shr.m_DriverVersion, request.args)
        return vars(R)


# ----------------
# InterfaceVersion
# ----------------
#
@api.route('/<int:DeviceNumber>/interfaceversion', methods=['GET'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class interfaceversion(Resource):

    @api.doc(description='The interface version number that this device supports. Should return 2 for this interface version.')
    @api.marshal_with(m_IntegerResponse, description=shr.s_DescGetRsp, skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        R = shr.PropertyResponse(2, request.args)
        return vars(R)


# ----
# Name
# ----
#
@api.route('/<int:DeviceNumber>/name', methods=['GET'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class name(Resource):

    @api.doc(description='The short name of the driver, for display purposes.')
    @api.marshal_with(m_StringResponse, description=shr.s_DescGetRsp, skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        R = shr.PropertyResponse('Rotator Simulator', request.args)
        return vars(R)


# ----------------
# SupportedActions
# ----------------
#
@api.route('/<int:DeviceNumber>/supportedactions', methods=['GET'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class supportedactions(Resource):

    @api.doc(description='Returns the list of action names supported by this driver.')
    @api.marshal_with(m_StringListResponse, description='List of supported <b>Action()</b> commands.', skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        R = shr.PropertyResponse([], request.args)
        return vars(R)


# ----------
# CanReverse
# ----------
#
@api.route('/<int:DeviceNumber>/canreverse', methods=['GET'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class canreverse(Resource):

    @api.doc(description='True if the Rotator supports the <b>Reverse</b> method.')
    @api.marshal_with(m_BoolResponse, description=shr.s_DescGetRsp, skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        if not RotDev[DeviceNumber].connected:
            R = shr.PropertyResponse(None, request.args, ASCOMErrors.NotConnectedException)
            return vars(R)
        R = shr.PropertyResponse(RotDev[DeviceNumber].can_reverse, request.args)
        return vars(R)


# --------
# IsMoving
# --------
#
@api.route('/<int:DeviceNumber>/ismoving', methods=['GET'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class ismoving(Resource):

    @api.doc(description='True if the Rotator is currently moving to a new position. False if the Rotator is stationary.')
    @api.marshal_with(m_BoolResponse, description=shr.s_DescGetRsp, skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        if not RotDev[DeviceNumber].connected:
            R = shr.PropertyResponse(None, request.args, ASCOMErrors.NotConnectedException)
            return vars(R)
        R = shr.PropertyResponse(RotDev[DeviceNumber].is_moving, request.args)
        return vars(R)


# --------
# Position
# --------
#
@api.route('/<int:DeviceNumber>/position', methods=['GET'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class position(Resource):

    @api.doc(description='Current instantaneous Rotator mechanical angle (degrees).')
    @api.marshal_with(m_FloatResponse, description=shr.s_DescGetRsp, skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        if not RotDev[DeviceNumber].connected:
            R = shr.PropertyResponse(None, request.args, ASCOMErrors.NotConnectedException)
            return vars(R)
        R = shr.PropertyResponse(RotDev[DeviceNumber].position, request.args)
        return vars(R)


# -------
# Reverse
# -------
#
@api.route('/<int:DeviceNumber>/reverse', methods=['GET','PUT'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class reverse(Resource):

    @api.doc(description='Returns the Rotator\'s <b>Reverse</b> state.')
    @api.marshal_with(m_BoolResponse, description=shr.s_DescGetRsp, skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        if not RotDev[DeviceNumber].connected:
            R = shr.PropertyResponse(None, request.args, ASCOMErrors.NotConnectedException)
            return vars(R)
        R = shr.PropertyResponse(RotDev[DeviceNumber].reverse, request.args)
        return vars(R)

    @api.doc(description='Sets the Rotator\'s <b>Reverse</b> state.')
    @api.marshal_with(m_MethodResponse, description=shr.s_DescMthRsp, skip_none=True)
    @api.param('Reverse', 'True if the rotation and angular ' +
                          'direction must be reversed to match the optical ' +
                          'characteristics', 'formData', type='boolean', default=False, required=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'formData', type='integer', default=1234)
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        if not RotDev[DeviceNumber].connected:
            R = shr.MethodResponse(request.form, ASCOMErrors.NotConnectedException)
            return vars(R)
        if RotDev[DeviceNumber].is_moving:
            R = shr.MethodResponse(request.form, ASCOMErrors.InvalidOperationException)
            return vars(R)
        RotDev[DeviceNumber].reverse = (shr.get_form_caseless('Reverse', request.form, 'false').lower() == 'true')     # **TODO** Is this right???
        R = shr.MethodResponse(request.form)
        return vars(R)


# --------
# StepSize
# --------
#
@api.route('/<int:DeviceNumber>/stepsize', methods=['GET'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class stepsize(Resource):

    @api.doc(description='The minimum angular step size (degrees).')
    @api.marshal_with(m_FloatResponse, description=shr.s_DescGetRsp, skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        if not RotDev[DeviceNumber].connected:
            R = shr.PropertyResponse(None, request.args, ASCOMErrors.NotConnectedException)
            return vars(R)
        R = shr.PropertyResponse(RotDev[DeviceNumber].step_size, request.args)
        return vars(R)


# --------------
# TargetPosition
# --------------
#
@api.route('/<int:DeviceNumber>/targetposition', methods=['GET'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class targetposition(Resource):

    @api.doc(description='The destination mechanical angle for <b>Move()</b> and <b>MoveAbsolute()</b>.')
    @api.marshal_with(m_FloatResponse, description=shr.s_DescGetRsp, skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'query', type='integer', default='1234')
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        if not RotDev[DeviceNumber].connected:
            R = shr.PropertyResponse(None, request.args, ASCOMErrors.NotConnectedException)
            return vars(R)
        R = shr.PropertyResponse(RotDev[DeviceNumber].target_position, request.args)
        return vars(R)


# ----
# Halt
# ----
#

@api.route('/<int:DeviceNumber>/halt', methods=['PUT'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class halt(Resource):

    @api.doc(description='Immediately stop any Rotator motion due to a previous <b>Move()</b> or <b>MoveAbsolute()</b>.')
    @api.marshal_with(m_MethodResponse, description=shr.s_DescMthRsp, skip_none=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'formData', type='integer', default=1234)
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        if not RotDev[DeviceNumber].connected:
            R = shr.PropertyResponse(None, request.args, ASCOMErrors.NotConnectedException)
            return vars(R)
        RotDev[DeviceNumber].Halt()
        R = shr.MethodResponse(request.form)
        return vars(R)


# ----
# Move
# ----
#

@api.route('/<int:DeviceNumber>/move', methods=['PUT'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class move(Resource):
    @api.doc(description='Causes the rotator to move <b>Position</b> degrees relative to the current <b>Position</b>.')
    @api.marshal_with(m_MethodResponse, description=shr.s_DescMthRsp, skip_none=True)
    @api.param('Position', 'Angle to move in degrees relative to the current <b>Position</b>.',
                           'formData', type='number', default = 0.0, required=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'formData', type='integer', default=1234)
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        if not RotDev[DeviceNumber].connected:
            R = shr.MethodResponse(request.form, ASCOMErrors.NotConnectedException)
            return vars(R)
        if RotDev[DeviceNumber].is_moving:
            R = shr.MethodResponse(request.form, ASCOMErrors.InvalidOperationException)
            return vars(R)
        relPos = float(shr.get_form_caseless('Position', request.form, 0.0))
        if relPos >= 360 or relPos <= -360.0:
            R = shr.MethodResponse(request.form, ASCOMErrors.InvalidValueException)
            return vars(R)
        RotDev[DeviceNumber].Move(relPos)
        R = shr.MethodResponse(request.form)
        return vars(R)


# ------------
# MoveAbsolute
# ------------
#

@api.route('/<int:DeviceNumber>/moveabsolute', methods=['PUT'])
@api.param(shr.s_FldDevNum, shr.s_DescDevNum, 'path', type='integer', default='0')
@api.response(400, shr.s_Resp400Missing, m_ErrorMessage)
@api.response(500, shr.s_Resp500SrvErr, m_ErrorMessage)
class moveabsolute(Resource):
    @api.doc(description='Causes the rotator to move the absolute position of <b>Position</b> degrees.')
    @api.marshal_with(m_MethodResponse, description=shr.s_DescMthRsp, skip_none=True)
    @api.param('Position', 'Destination mechanical angle to which the rotator will move (degrees).',
                            'formData', type='number',  default=0.0, required=True)
    @api.param(shr.s_FldClId, shr.s_DescClId, 'formData', type='integer', default=1234)
    @api.param(shr.s_FldCtId, shr.s_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if not DeviceNumber in rRot:
            abort(400, shr.s_Resp400NoDevNo)
        if not RotDev[DeviceNumber].connected:
            R = shr.MethodResponse(request.form, ASCOMErrors.NotConnectedException)
            return vars(R)
        if RotDev[DeviceNumber].is_moving:
            R = shr.MethodResponse(request.form, ASCOMErrors.InvalidOperationException)
            return vars(R)
        newPos = float(shr.get_form_caseless('Position', request.form, 0.0))
        if newPos >= 360 or newPos < 0:
            R = shr.MethodResponse(request.form, ASCOMErrors.InvalidValueException)
            return vars(R)
        RotDev[DeviceNumber].MoveAbsolute(newPos)
        R = shr.MethodResponse(request.form)
        return vars(R)
