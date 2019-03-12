# =================================================================================================
# ASCOM Alpaca Rotator Simulator - Alpaca Interface Module & Main Program
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
# =================================================================================================

# https://ascom-standards.org/api
# http://flask.pocoo.org/docs/1.0/
# https://flask-restplus.readthedocs.io/en/stable/index.html

import os
from flask import Flask, Blueprint, request, abort, make_response
from flask_restplus import Api, Resource, fields

import ASCOMErrors
import RotatorDevice

# --------------
# Driver Version
# --------------
m_DriverVersion = '0.3'                                 # Major.Minor only

# ===============================
# FLASK SERVER AND REST FRAMEWORK
# ===============================

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'        # Open Swagger with list displayed by default
app.config['RESTPLUS_MASK_SWAGGER'] = False         # Not used in our device, so hide this from Swagger

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)                         # Prevent successful HTTP traffic from being logged

blueprint = Blueprint('Rotator', __name__, 
                      url_prefix='/api/v1/rotator',
                      static_folder='static')
# Create a URL prefix for the whole application
api = Api(default='rotator', 
            default_label='<h2>ASCOM Alpaca API for Rotator Devices: Base URL = <tt>/api/v1/rotator',
            contact='Bob Denny, DC-3 Dreams, SP',
            contact_email='rdenny@dc3.com',
            version='Exp. 1.0')

api.init_app(blueprint, 
            version = '1.0',
            title='ASCOM Alpaca Rotator Simulator', 
            description='<div><a href=\'https://ascom-standards.org/Developer/Alpaca.htm\' target=\'_new\'>'+
                '<img src=\'static/AlpacaLogo128.png\' align=\'right\' width=\'128\' height=\'101\' /></a>'+ 
                '<h2>This device is an ASCOM Rotator simulator that responds to ' +
                'the standard ASCOM Alpaca API for Rotator</h2>\r\n' +
                '<a href=\'https://ascom-standards.org/Developer/ASCOM%20Alpaca%20API%20Reference.pdf\' target=\'_new\'>' +
                    'View the ASCOM Alpaca API Reference (PDF)</a><br /><br />\r\n' + 
                '<a href=\'https://ascom-standards.org/api/\' target=\'_new\'>View the ASCOM Alpaca Definitive API (Swagger)</a><br /><br /></div>')

app.register_blueprint(blueprint)

# --------------
# Rotator Device
# --------------
# **TODO** Create 8 of these and allow 8 clients with different device ID!
#
_ROT = RotatorDevice.RotatorDevice()

#
# Connection state - server transaction ID
#
svrtransid = 0                                          # Counts up

#
# Get query string data with case-insensitive name
#
def get_args_caseless(name, default):
    lcName = name.lower()
    a = request.args                                    # Why does this work (no need for list(request.args.keys()))? (typ.)
    for an in a:
        if an.lower() == lcName:
            return a.get(an, default)
    return name                                         # not in form, let caller punt

#
# Get form data with case-insensitive name
#
def get_form_caseless(name, default):
    lcName = name.lower()
    f = request.form
    for fn in f:
        if fn.lower() == lcName:
            return f.get(fn, default)
    return name                                         # not in form, let caller punt

# ------------------------------
# Common strings used throughout
# ------------------------------

#
# Common/shared field name strings
#
m_FldDevNum =   'DeviceNumber'
m_FldClId =     'ClientID'
m_FldValue =    'Value'
m_FldCtId =     'ClientTransactionID'
m_FldStId =     'ServerTransactionID'
m_FldErrNum =   'ErrorNumber'
m_FldErrMsg =   'ErrorMessage'

#
# Common/shared description strings
#
m_DescDevNum =  'Zero-based device number as set on the server'
m_DescClId =    'Client\'s unique ID. The client should choose a random value at startup and send this value with every transaction.'
m_DescCtId =    'Client\'s transaction ID as supplied by the client in the command request. The cleint should start this count at 1 and increment by 1 on each successive transaction.'
m_DescStId =    'Server\'s transaction ID; should be unique for each client transaction so that log messages on the client can be associated with logs on the device.'
m_DescErrNum =  'Zero for a successful transaction, or a 12-bit non-zero Alpaca error code if the device encountered an issue.'
m_DescErrMsg =  'Empty string for a successful transaction, or a message describing the issue that was encountered.'
m_DescMthRsp =  'Transaction complete or exception'

#
# Common/shared response strings
#
m_Resp400Missing =  'DeviceNumber, command, or parameter values, are missing or invalid'
m_Resp400NoDevNo =  'No such DeviceNumber'
m_Resp500SrvErr =   'Server internal error, check error message'

# ==========================
# Models and Wrapper Classes
# ==========================

m_ErrorMessage = api.model(m_FldErrMsg, {m_FldValue : fields.String(description=m_DescErrMsg, required=True)})

# ------------------
# PropertyResponse
# ------------------
# Construct the response for a property-get. Common to all
# of the properties in this driver. Models (see below) 
# differ to specify data type and documentation of Value.
#
class PropertyResponse(dict):
    def __init__(self, value, err = ASCOMErrors.Success):
        global svrtransid
        svrtransid += 1
        self.Value = value
        self.ClientTransactionID = get_args_caseless(m_FldCtId, 1)
        self.ServerTransactionID = svrtransid
        self.ErrorNumber = err.Number
        self.ErrorMessage = err.Message

m_BoolResponse = api.model('BoolResponse', 
                    {   m_FldValue      : fields.Boolean(description='True or False value.', required=True),
                        m_FldCtId       : fields.Integer(min=0, max=4294967295, description=m_DescCtId),
                        m_FldStId       : fields.Integer(min=0, max=4294967295, description=m_DescStId),
                        m_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=m_DescErrNum),
                        m_FldErrMsg     : fields.String(description=m_DescErrMsg)
                    })

m_FloatResponse = api.model('FloatResponse', 
                    {   m_FldValue      : fields.Float(description='Double value.', required=True),
                        m_FldCtId       : fields.Integer(min=0, max=4294967295, description=m_DescCtId),
                        m_FldStId       : fields.Integer(min=0, max=4294967295, description=m_DescStId),
                        m_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=m_DescErrNum),
                        m_FldErrMsg     : fields.String(description=m_DescErrMsg)
                    })

m_StringResponse = api.model('StringResponse', 
                    {   m_FldValue      : fields.String(description='String value.', required=True),
                        m_FldCtId       : fields.Integer(min=0, max=4294967295, description=m_DescCtId),
                        m_FldStId       : fields.Integer(min=0, max=4294967295, description=m_DescStId),
                        m_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=m_DescErrNum),
                        m_FldErrMsg     : fields.String(description=m_DescErrMsg)
                    })

m_StringListResponse = api.model('StringListResponse', 
                    {   m_FldValue      : fields.List(fields.String(), description='List of string values.', required=True),
                        m_FldCtId       : fields.Integer(min=0, max=4294967295, description=m_DescCtId),
                        m_FldStId       : fields.Integer(min=0, max=4294967295, description=m_DescStId),
                        m_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=m_DescErrNum),
                        m_FldErrMsg     : fields.String(description=m_DescErrMsg)
                    })

# --------------
# MethodResponse
# --------------
#
class MethodResponse(dict):
    def __init__(self, err = ASCOMErrors.Success):
        global svrtransid
        svrtransid += 1
        self.ClientTransactionID =  get_form_caseless(m_FldCtId, 1)
        self.ServerTransactionID = svrtransid
        self.ErrorNumber = err.Number
        self.ErrorMessage = err.Message

m_MethodResponse = api.model('MethodResponse', 
                    {   m_FldCtId       : fields.Integer(min=0, max=4294967295, description=m_DescCtId),
                        m_FldStId       : fields.Integer(min=0, max=4294967295, description=m_DescStId),
                        m_FldErrNum     : fields.Integer(min=0, max=0xFFF, description=m_DescErrNum),
                        m_FldErrMsg     : fields.String(description=m_DescErrMsg)
                    })

# ==============================
# API ENDPOINTS (REST Resources)
# ==============================

# Note the additonal items retrieved from the request in Connected (typ.)


# ------
# Action
# ------
#
@api.route('/<int:DeviceNumber>/action', methods=['PUT'])
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class action(Resource):

    @api.doc(description='Invokes the specified device-specific action.')
    @api.marshal_with(m_MethodResponse, description=m_DescMthRsp)
    @api.param('Action', 'A well known name that represents the action to be carried out.', 'formData', type='string', required=True)
    @api.param('Parameters', 'List of parameters or empty string if none are required.', 'formData', type='string', default='', required=True)
    @api.param(m_FldClId, m_DescClId, 'formData', type='integer', default=1234)
    @api.param(m_FldCtId, m_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        global connected
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        R = MethodResponse(ASCOMErrors.NotImplemented)
        return vars(R)

# ------------
# CommandBlind
# ------------
#
@api.route('/<int:DeviceNumber>/commandblind', methods=['PUT'])
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class commandblind(Resource):

    @api.doc(description='Transmits an arbitrary string to the device and does not wait for a response. ' +
                        'Optionally, protocol framing characters may be added to the string before transmission.')
    @api.marshal_with(m_MethodResponse, description=m_DescMthRsp)
    @api.param('Command', 'The literal command string to be transmitted.', 'formData', type='string', required=True)
    @api.param('Raw', 'If set to true the string is transmitted \'as-is\', ' +
                      'if set to false then protocol framing characters may be added prior ' +
                      'to transmission', 'formData', type='boolean', default=False, required=True)
    @api.param(m_FldClId, m_DescClId, 'formData', type='integer', default=1234)
    @api.param(m_FldCtId, m_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        global connected
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        R = MethodResponse(ASCOMErrors.NotImplemented)
        return vars(R)


# -----------
# CommandBool
# -----------
#
@api.route('/<int:DeviceNumber>/commandbool', methods=['PUT'])
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class commandbool(Resource):

    @api.doc(description='Transmits an arbitrary string to the device and waits for a boolean response. ' +
                        'Optionally, protocol framing characters may be added to the string before transmission.')
    @api.marshal_with(m_MethodResponse, description=m_DescMthRsp)
    @api.param('Command', 'The literal command string to be transmitted.', 'formData', type='string', required=True)
    @api.param('Raw', 'If set to true the string is transmitted \'as-is\', ' +
                      'if set to false then protocol framing characters may be added prior ' +
                      'to transmission', 'formData', type='boolean', default=False, required=True)
    @api.param(m_FldClId, m_DescClId, 'formData', type='integer', default=1234)
    @api.param(m_FldCtId, m_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        R = MethodResponse(ASCOMErrors.NotImplemented)
        return vars(R)


# -------------
# CommandString
# -------------
#
@api.route('/<int:DeviceNumber>/commandstring', methods=['PUT'])
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class commandstring(Resource):

    @api.doc(description='Transmits an arbitrary string to the device and waits for a string response. ' +
                        'Optionally, protocol framing characters may be added to the string before transmission.')
    @api.marshal_with(m_MethodResponse, description=m_DescMthRsp)
    @api.param('Command', 'The literal command string to be transmitted.', 'formData', type='string', required=True)
    @api.param('Raw', 'If set to true the string is transmitted \'as-is\', ' +
                      'if set to false then protocol framing characters may be added prior ' +
                      'to transmission', 'formData', type='boolean', default=False, required=True)
    @api.param(m_FldClId, m_DescClId, 'formData', type='integer', default=1234)
    @api.param(m_FldCtId, m_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        R = MethodResponse(ASCOMErrors.NotImplemented)
        return vars(R)


# ---------
# Connected
# ---------
#
@api.route('/<int:DeviceNumber>/connected', methods=['GET','PUT'])
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class connected(Resource):

    @api.doc(description='Retrieves the connected state of the Rotator.')
    @api.marshal_with(m_BoolResponse, description=m_DescMthRsp)
    @api.param(m_FldClId, m_DescClId, 'query', type='integer', default=1234)
    @api.param(m_FldCtId, m_DescCtId, 'query', type='integer', default=1)
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        devno = DeviceNumber                        # Used later for multi-device (typ.)
        cid = get_args_caseless(m_FldClId, 1234)    # Used if need to ident the Client (typ.)
        R = PropertyResponse(_ROT.connected)
        return vars(R)

    @api.doc(description='Sets the connected state of the Rotator.')
    @api.marshal_with(m_MethodResponse, description=m_DescMthRsp)
    @api.param('Connected', 'Set True to connect to the device hardware. Set False to ' +
                            'disconnect from the device hardware.',
                            'formData', type='boolean', default=False, required=True)
    @api.param(m_FldClId, m_DescClId, 'formData', type='integer', default=1234)
    @api.param(m_FldCtId, m_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        devno = DeviceNumber
        cid = get_form_caseless(m_FldClId, 1234)
        _ROT.connected = (get_form_caseless('Connected', 'false').lower() == 'true')
        R = MethodResponse()
        return vars(R)

# -----------
# Description
# -----------
#
@api.route('/<int:DeviceNumber>/description', methods=['GET']) 
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class description(Resource):

    @api.doc(description='Returns a description of the device, such as manufacturer and modelnumber. Any ASCII characters may be used.')
    @api.marshal_with(m_StringResponse, description=m_DescMthRsp)
    @api.param(m_FldClId, m_DescClId, 'query', type='integer', default='1234')
    @api.param(m_FldCtId, m_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        desc = 'Simulated Rotator implemented in Python.'
        R = PropertyResponse(desc)
        return vars(R)


# ----------
# DriverInfo
# ----------
#
@api.route('/<int:DeviceNumber>/driverinfo', methods=['GET']) 
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class driverinfo(Resource):

    @api.doc(description='Descriptive and version information about this ASCOM driver.')
    @api.marshal_with(m_StringResponse, description=m_DescMthRsp)
    @api.param(m_FldClId, m_DescClId, 'query', type='integer', default='1234')
    @api.param(m_FldCtId, m_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        desc = 'ASCOM Alpaca driver for a simulated Rotator. Experimental V' + m_DriverVersion + ' (Python)'
        R = PropertyResponse(desc)
        return vars(R)


# -------------
# DriverVersion
# -------------
#
@api.route('/<int:DeviceNumber>/driverversion', methods=['GET']) 
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class driverversion(Resource):

    @api.doc(description='A string containing only the major and minor version of the driver.')
    @api.marshal_with(m_StringResponse, description=m_DescMthRsp)
    @api.param(m_FldClId, m_DescClId, 'query', type='integer', default='1234')
    @api.param(m_FldCtId, m_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        R = PropertyResponse(m_DriverVersion)
        return vars(R)


# ----------------
# InterfaceVersion
# ----------------
#
@api.route('/<int:DeviceNumber>/interfaceversion', methods=['GET']) 
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class interfaceversion(Resource):

    @api.doc(description='The interface version number that this device supports. Should return 2 for this interface version.')
    @api.marshal_with(m_StringResponse, description=m_DescMthRsp)
    @api.param(m_FldClId, m_DescClId, 'query', type='integer', default='1234')
    @api.param(m_FldCtId, m_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        R = PropertyResponse(2)
        return vars(R)


# ----
# Name
# ----
#
@api.route('/<int:DeviceNumber>/name', methods=['GET']) 
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class name(Resource):

    @api.doc(description='The short name of the driver, for display purposes.')
    @api.marshal_with(m_StringResponse, description=m_DescMthRsp)
    @api.param(m_FldClId, m_DescClId, 'query', type='integer', default='1234')
    @api.param(m_FldCtId, m_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        R = PropertyResponse('Rotator Simulator')
        return vars(R)


# ----------------
# SupportedActions
# ----------------
#
@api.route('/<int:DeviceNumber>/supportedactions', methods=['GET']) 
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class supportedactions(Resource):

    @api.doc(description='Returns the list of action names supported by this driver.')
    @api.marshal_with(m_StringListResponse, description='List of supported <b>Action()</b> commands.')
    @api.param(m_FldClId, m_DescClId, 'query', type='integer', default='1234')
    @api.param(m_FldCtId, m_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        R = PropertyResponse([])
        return vars(R)


# ----------
# CanReverse
# ----------
#
@api.route('/<int:DeviceNumber>/canreverse', methods=['GET']) 
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class canreverse(Resource):

    @api.doc(description='True if the Rotator supports the <b>Reverse</b> method.')
    @api.marshal_with(m_BoolResponse, description=m_DescMthRsp)
    @api.param(m_FldClId, m_DescClId, 'query', type='integer', default='1234')
    @api.param(m_FldCtId, m_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        if (not _ROT.connected):
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        R = PropertyResponse(_ROT.can_reverse)
        return vars(R)


# --------
# IsMoving
# --------
#
@api.route('/<int:DeviceNumber>/ismoving', methods=['GET']) 
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class ismoving(Resource):

    @api.doc(description='True if the Rotator is currently moving to a new position. False if the Rotator is stationary.')
    @api.marshal_with(m_BoolResponse, description=m_DescMthRsp)
    @api.param(m_FldClId, m_DescClId, 'query', type='integer', default='1234')
    @api.param(m_FldCtId, m_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        if not _ROT.connected:
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        R = PropertyResponse(_ROT.is_moving)
        return vars(R)


# --------
# Position
# --------
#
@api.route('/<int:DeviceNumber>/position', methods=['GET']) 
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class position(Resource):

    @api.doc(description='Current instantaneous Rotator mechanical angle (degrees).')
    @api.marshal_with(m_FloatResponse, description=m_DescMthRsp)
    @api.param(m_FldClId, m_DescClId, 'query', type='integer', default='1234')
    @api.param(m_FldCtId, m_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        if not _ROT.connected:
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        R = PropertyResponse(_ROT.position)
        return vars(R)


# -------
# Reverse
# -------
#
@api.route('/<int:DeviceNumber>/reverse', methods=['GET','PUT'])
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class reverse(Resource):

    @api.doc(description='Returns the Rotator\'s <b>Reverse</b> state.')
    @api.marshal_with(m_BoolResponse, description=m_DescMthRsp)
    @api.param(m_FldClId, m_DescClId, 'query', type='integer', default='1234')
    @api.param(m_FldCtId, m_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        if not _ROT.connected:
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        R = PropertyResponse(_ROT.reverse)
        return vars(R)

    @api.doc(description='Sets the Rotator\'s <b>Reverse</b> state.')
    @api.marshal_with(m_MethodResponse, description=m_DescMthRsp)
    @api.param('Reverse', 'True if the rotation and angular ' + 
                          'direction must be reversed to match the optical ' +
                          'characteristics', 'formData', type='boolean', default=False, required=True)
    @api.param(m_FldClId, m_DescClId, 'formData', type='integer', default=1234)
    @api.param(m_FldCtId, m_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        if not _ROT.connected:
            R = MethodResponse(ASCOMErrors.NotConnected)
            return vars(R)
        if _ROT.is_moving:
            R = MethodResponse(ASCOMErrors.InvalidOperationException)
            return vars(R)
        _ROT.reverse = (get_form_caseless('Reverse', 'false').lower() == 'true')     # **TODO** Is this right???
        R = MethodResponse()
        return vars(R)


# --------
# StepSize
# --------
#
@api.route('/<int:DeviceNumber>/stepsize', methods=['GET']) 
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class stepsize(Resource):

    @api.doc(description='The minimum angular step size (degrees).')
    @api.marshal_with(m_FloatResponse, description=m_DescMthRsp)
    @api.param(m_FldClId, m_DescClId, 'query', type='integer', default='1234')
    @api.param(m_FldCtId, m_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        if not _ROT.connected:
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        R = PropertyResponse(_ROT.step_size)
        return vars(R)


# --------------
# TargetPosition
# --------------
#
@api.route('/<int:DeviceNumber>/targetposition', methods=['GET']) 
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class targetposition(Resource):

    @api.doc(description='The destination mechanical angle for <b>Move()</b> and <b>MoveAbsolute()</b>.')
    @api.marshal_with(m_FloatResponse, description=m_DescMthRsp)
    @api.param(m_FldClId, m_DescClId, 'query', type='integer', default='1234')
    @api.param(m_FldCtId, m_DescCtId, 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        if not _ROT.connected:
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        R = PropertyResponse(_ROT.target_position)
        return vars(R)


# ----
# Halt
# ----
#

@api.route('/<int:DeviceNumber>/halt', methods=['PUT'])
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class halt(Resource):

    @api.doc(description='Immediately stop any Rotator motion due to a previous <b>Move()</b> or <b>MoveAbsolute()</b>.')
    @api.marshal_with(m_MethodResponse, description=m_DescMthRsp)
    @api.param(m_FldClId, m_DescClId, 'formData', type='integer', default=1234)
    @api.param(m_FldCtId, m_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        if not _ROT.connected:
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        _ROT.Halt()
        R = MethodResponse()
        return vars(R)


# ----
# Move
# ----
#

@api.route('/<int:DeviceNumber>/move', methods=['PUT'])
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class move(Resource):
    
    
    @api.doc(description='Causes the rotator to move <b>Position</b> degrees relative to the current <b>Position</b>.')
    @api.marshal_with(m_MethodResponse, description=m_DescMthRsp)
    @api.param('Position', 'Angle to move in degrees relative to the current <b>Position</b>.', 
                           'formData', type='number', default = 0.0, required=True)
    @api.param(m_FldClId, m_DescClId, 'formData', type='integer', default=1234)
    @api.param(m_FldCtId, m_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        if not _ROT.connected:
            R = MethodResponse(ASCOMErrors.NotConnected)
            return vars(R)
        if _ROT.is_moving:
            R = MethodResponse(ASCOMErrors.InvalidOperationException)
            return vars(R)
        relPos = float(get_form_caseless('Position', 0.0))
        if relPos >= 360 or relPos <= -360.0:
            R = MethodResponse(ASCOMErrors.InvalidValue)
            return vars(R)
        _ROT.Move(relPos)
        R = MethodResponse()
        return vars(R)


# ------------
# MoveAbsolute
# ------------
#

@api.route('/<int:DeviceNumber>/moveabsolute', methods=['PUT'])
@api.param(m_FldDevNum, m_DescDevNum, 'path', type='integer', default='0')
@api.response(400, m_Resp400Missing, m_ErrorMessage)
@api.response(500, m_Resp500SrvErr, m_ErrorMessage)
class moveabsolute(Resource):
    
    @api.doc(description='Causes the rotator to move the absolute position of <b>Position</b> degrees.')
    @api.marshal_with(m_MethodResponse, description=m_DescMthRsp)
    @api.param('Position', 'Destination mechanical angle to which the rotator will move (degrees).',
                            'formData', type='number',  default=0.0, required=True)
    @api.param(m_FldClId, m_DescClId, 'formData', type='integer', default=1234)
    @api.param(m_FldCtId, m_DescCtId, 'formData', type='integer', default=1)
    def put(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, m_Resp400NoDevNo)
        if not _ROT.connected:
            R = MethodResponse(ASCOMErrors.NotConnected)
            return vars(R)
        if _ROT.is_moving:
            R = MethodResponse(ASCOMErrors.InvalidOperationException)
            return vars(R)
        newPos = float(get_form_caseless('Position', 0.0))
        if newPos >= 360 or newPos < 0:
            R = MethodResponse(ASCOMErrors.InvalidValue)
            return vars(R)
        _ROT.MoveAbsolute(newPos)
        R = MethodResponse()
        return vars(R)


# ==================
# SERVER APPLICATION
# ==================
#
# Start it this way to get  the automatic tab on Chrome
# with the right host/port.
#
if __name__ == '__main__':

    if os.name == 'nt':             # This is really Windows (my dev system eh?)
        HOST = '127.0.0.1'
        print(' * Running on Windows... 127.0.0.1')
    else:
        HOST = '192.168.0.40'       # Unbelievable what you need to do to get your live IP address on Linux (which one????)
        print(' * Assuming run on Raspberry Pi Linux 192.168.0.40')
    PORT = 5555
    app.run(HOST, PORT)
