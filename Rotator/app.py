# https://ascom-standards.org/api
# https://exploreflask.com/en/latest/views.html#url-converters

import os
from flask import Flask, Blueprint, request, abort
from flask_restplus import Api, Resource, fields
import ASCOMErrors
import RotatorDevice


# *TODO* Make path matching caseless
# *TODO* Convert some 404s to 400s per ASCOM Spec
# *TODO* Implement error on changing Reverse while moving

# ===============================
# FLASK SERVER AND REST FRAMEWORK
# ===============================
#
app = Flask(__name__)
blueprint = Blueprint('Rotator', __name__, 
                      url_prefix='/API/V1/Rotator',
                      static_folder='static')
# Create a URL prefix for the whole application
api = Api(default='Rotator', 
            default_label='<h2>ASCOM REST V1 for Rotator Devices: Base URL = <tt>/API/V1/Rotator',
            contact='Bob Denny, DC-3 Dreams, SP',
            contact_email='rdenny@dc3.com',
            version='1.0.0-oas3')

api.init_app(blueprint, 
            version = '1.0',
            title='ASCOM Rotator Simulator', 
            description='<h2><img src=\'static/Bug72T.jpg\' align=\'right\' width=\'72\' ' + 
                'height=\'84\' />This device is an ASCOM Rotator simulator that responds to ' +
                'the standard REST API for Rotator</h2>')
app.register_blueprint(blueprint)

# ==============
# Rotator Device
# =============
#
_ROT = RotatorDevice.RotatorDevice()

#
# Connection
#
svrtransid = 0                                           # Counts up

# ==========================
# Models and Wrapper Classes
# ==========================

m_ErrorMessage = api.model('ErrorMessage', {'Value' : fields.String(description='Error message', required=True)})

# --------------------
# INPUTS (PUT methods)
# --------------------
m_ConnectedValue = api.model('ConnectedValue',
                    {   'Connected'                 : fields.Boolean(False, description='Set True to connect to the device hardware, set False to ' +
                                                                        'disconnect from the device hardware', required=True),
                        'ClientID'                  : fields.Integer(1, description='Client\'s unique ID'),
                        'ClientTransactionID'       : fields.Integer(1234, description='Client\'s transaction ID')
                    })
    
m_ActionValue = api.model('ActionValue',
                    {   'Action'                    : fields.String('', description='A well known name that represents the action to be carried out.', required=True),
                        'Parameters'                : fields.String('', description='List of parameters or empty string if none are required.', required=True),
                        'ClientID'                  : fields.Integer(1, description='Client\'s unique ID'),
                        'ClientTransactionID'       : fields.Integer(1234, description='Client\'s transaction ID')
                    })

m_CommandValues = api.model('CommandValues',
                    {   'Command'                   : fields.String('', description='The literal command string to be transmitted', required=True),
                        'Raw'                       : fields.Boolean('', description='If set to true the string is transmitted \'as-is\', ' +
                                                                        'if set to false then protocol framing characters may be added prior ' +
                                                                        'to transmission', required=True),
                        'ClientID'                  : fields.Integer(1, description='Client\'s unique ID'),
                        'ClientTransactionID'       : fields.Integer(1234, description='Client\'s transaction ID')
                    })
    
m_ReverseValue = api.model('ReverseValue',
                    {   'Reverse'                   : fields.Boolean(False, description='True if the rotation and angular ' + 
                                                                        'direction must be reversed to match the optical ' +
                                                                        'characteristics', required=True),
                        'ClientID'                  : fields.Integer(1, description='Client\'s unique ID'),
                        'ClientTransactionID'       : fields.Integer(1234, description='Client\'s transaction ID')
                    })
    
m_RelPosValue = api.model('RelPosValue',
                    {   'Position'                  : fields.Float(0.0, description='Angle to move in degrees relative to the current <b>Position</b>.', required=True),
                        'ClientID'                  : fields.Integer(1, description='Client\'s unique ID'),
                        'ClientTransactionID'       : fields.Integer(1234, description='Client\'s transaction ID')
                    })
    
m_AbsPosValue = api.model('AbsPosValue',
                    {   'Position'                  : fields.Float(0.0, description='Destination mechanical angle to which the rotator will move (degrees).', required=True),
                        'ClientID'                  : fields.Integer(1, description='Client\'s unique ID'),
                        'ClientTransactionID'       : fields.Integer(1234, description='Client\'s transaction ID')
                    })


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
        self.ClientTransactionIDForm = request.args.get('ClientTransactionID', 1)
        self.ServerTransactionID = svrtransid
        self.Method = request.method
        self.ErrorNumber = err.Number
        self.ErrorMessage = err.Message
        self.DriverException = None

m_BoolResponse = api.model('BoolResponse', 
                    {   'Value'                     : fields.Boolean(description='True or False value.', required=True),
                        'ClientTransactionIDForm'   : fields.Integer(description='Client\'s transaction ID.'),
                        'ServerTransactionID'       : fields.Integer(description='Server\'s transaction ID.'),
                        'Method'                    : fields.String(description='Name of the calling method.'),
                        'ErrorNumber'               : fields.Integer(description='Error number from device.'),
                        'ErrorMessage'              : fields.String(description='Error message description from device.')
                    })

m_FloatResponse = api.model('FloatResponse', 
                    {   'Value'                     : fields.Float(description='Double value.', required=True),
                        'ClientTransactionIDForm'   : fields.Integer(description='Client\'s transaction ID.'),
                        'ServerTransactionID'       : fields.Integer(description='Server\'s transaction ID.'),
                        'Method'                    : fields.String(description='Name of the calling method.'),
                        'ErrorNumber'               : fields.Integer(description='Error number from device.'),
                        'ErrorMessage'              : fields.String(description='Error message description from device.')
                    })

m_StringResponse = api.model('StringResponse', 
                    {   'Value'                     : fields.String(description='String value.', required=True),
                        'ClientTransactionIDForm'   : fields.Integer(description='Client\'s transaction ID.'),
                        'ServerTransactionID'       : fields.Integer(description='Server\'s transaction ID.'),
                        'Method'                    : fields.String(description='Name of the calling method.'),
                        'ErrorNumber'               : fields.Integer(description='Error number from device.'),
                        'ErrorMessage'              : fields.String(description='Error message description from device.')
                    })

m_StringListResponse = api.model('StringListResponse', 
                    {   'Value'                     : fields.List(fields.String(), description='List of string values.', required=True),
                        'ClientTransactionIDForm'   : fields.Integer(description='Client\'s transaction ID.'),
                        'ServerTransactionID'       : fields.Integer(description='Server\'s transaction ID.'),
                        'Method'                    : fields.String(description='Name of the calling method.'),
                        'ErrorNumber'               : fields.Integer(description='Error number from device.'),
                        'ErrorMessage'              : fields.String(description='Error message description from device.')
                    })

# --------------
# MethodResponse
# --------------
#
class MethodResponse(dict):
    def __init__(self, err = ASCOMErrors.Success):
        global svrtransid
        svrtransid += 1
        self.ClientTransactionIDForm = api.payload['ClientTransactionID']
        self.ServerTransactionID = svrtransid
        self.Method = request.method
        self.ErrorNumber = err.Number
        self.ErrorMessage = err.Message
        self.DriverException = None

m_MethodResponse = api.model('MethodResponse', 
                    {   'ClientTransactionIDForm'   : fields.Integer(description='Client\'s transaction ID.'),
                        'ServerTransactionID'       : fields.Integer(description='Server\'s transaction ID.'),
                        'Method'                    : fields.String(description='Name of the calling method.'),
                        'ErrorNumber'               : fields.Integer(description='Error number from device.'),
                        'ErrorMessage'              : fields.String(description='Error message description from device.')
                    })

# ==============================
# API ENDPOINTS (REST Resources)
# ==============================


# ------
# Action
# ------
#
@api.route('/<int:DeviceNumber>/Action', methods=['PUT'])
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class Action(Resource):

    @api.doc(description='Invokes the specified device-specific action.')
    @api.marshal_with(m_MethodResponse, description='Driver response')
    @api.expect(m_ActionValue)
    def put(self, DeviceNumber):
        global connected
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        R = MethodResponse(ASCOMErrors.NotImplemented)
        return vars(R)

# ------------
# CommandBlind
# ------------
#
@api.route('/<int:DeviceNumber>/CommandBlind', methods=['PUT'])
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class CommandBlind(Resource):

    @api.doc(description='Transmits an arbitrary string to the device and does not wait for a response. ' +
                        'Optionally, protocol framing characters may be added to the string before transmission..')
    @api.marshal_with(m_MethodResponse, description='Driver response')
    @api.expect(m_CommandValues)
    def put(self, DeviceNumber):
        global connected
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        R = MethodResponse(ASCOMErrors.NotImplemented)
        return vars(R)


# -----------
# CommandBool
# -----------
#
@api.route('/<int:DeviceNumber>/CommandBool', methods=['PUT'])
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class CommandBool(Resource):

    @api.doc(description='Transmits an arbitrary string to the device and waits for a boolean response. ' +
                        'Optionally, protocol framing characters may be added to the string before transmission..')
    @api.marshal_with(m_MethodResponse, description='Driver response')
    @api.expect(m_CommandValues)
    def put(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        R = MethodResponse(ASCOMErrors.NotImplemented)
        return vars(R)


# -------------
# CommandString
# -------------
#
@api.route('/<int:DeviceNumber>/CommandString', methods=['PUT'])
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class CommandString(Resource):

    @api.doc(description='Transmits an arbitrary string to the device and waits for a string response. ' +
                        'Optionally, protocol framing characters may be added to the string before transmission..')
    @api.marshal_with(m_MethodResponse, description='Driver response')
    @api.expect(m_CommandValues)
    def put(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        R = MethodResponse(ASCOMErrors.NotImplemented)
        return vars(R)


# ---------
# Connected
# ---------
#
@api.route('/<int:DeviceNumber>/Connected', methods=['GET','PUT'])
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class Connected(Resource):

    @api.doc(description='Retrieves the connected state of the Rotator.')
    @api.marshal_with(m_BoolResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        devno = DeviceNumber
        cid = request.args.get('ClientID', 1234)
        R = PropertyResponse(_ROT.connected)
        return vars(R)

    @api.doc(description='Sets the connected state of the Rotator.')
    @api.marshal_with(m_MethodResponse, description='Driver response')
    @api.expect(m_ConnectedValue)
    def put(self, DeviceNumber):
        global connected
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        devno = DeviceNumber                            # Whatever this might be used for
        cid = api.payload['ClientID']                   # Ditto
        _ROT.connected = api.payload['Connected']
        R = MethodResponse()
        return vars(R)

# -----------
# Description
# -----------
#
@api.route('/<int:DeviceNumber>/Description', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class Description(Resource):

    @api.doc(description='The description of the device itself.')
    @api.marshal_with(m_StringResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        desc = 'Simulated Rotator implemented in Python.'
        R = PropertyResponse(desc)
        return vars(R)


# ----------
# DriverInfo
# ----------
#
@api.route('/<int:DeviceNumber>/DriverInfo', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class DriverInfo(Resource):

    @api.doc(description='The description of the driver.')
    @api.marshal_with(m_StringResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        desc = 'ASCOM REST driver for a simulated Rotator.'
        R = PropertyResponse(desc)
        return vars(R)


# -------------
# DriverVersion
# -------------
#
@api.route('/<int:DeviceNumber>/DriverVersion', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class DriverInfo(Resource):

    @api.doc(description='A string containing only the major and minor version of the driver.')
    @api.marshal_with(m_StringResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = PropertyResponse('0.1')
        return vars(R)


# ----
# Name
# ----
#
@api.route('/<int:DeviceNumber>/Name', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class Name(Resource):

    @api.doc(description='The name of the device.')
    @api.marshal_with(m_StringResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = PropertyResponse('Rotator Simulator')
        return vars(R)


# ----------------
# SupportedActions
# ----------------
#
@api.route('/<int:DeviceNumber>/SupportedActions', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class SupportedActions(Resource):

    @api.doc(description='The name of the device.')
    @api.marshal_with(m_StringListResponse, description='List of supported <b>Action()</b> commands.')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = PropertyResponse([])
        return vars(R)


# ----------
# CanReverse
# ----------
#
@api.route('/<int:DeviceNumber>/CanReverse', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class CanReverse(Resource):

    @api.doc(description='True if the Rotator supports the <b>Reverse</b> method.')
    @api.marshal_with(m_BoolResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        if (not _ROT.connected):
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = PropertyResponse(_ROT.can_reverse)
        return vars(R)


# --------
# IsMoving
# --------
#
@api.route('/<int:DeviceNumber>/IsMoving', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class IsMoving(Resource):

    @api.doc(description='True if the Rotator is currently moving to a new position. False if the Rotator is stationary.')
    @api.marshal_with(m_BoolResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        if (not _ROT.connected):
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = PropertyResponse(_ROT.is_moving)
        return vars(R)


# --------
# Position
# --------
#
@api.route('/<int:DeviceNumber>/Position', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class Position(Resource):

    @api.doc(description='Current instantaneous Rotator mechanical angle (degrees).')
    @api.marshal_with(m_FloatResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        if (not _ROT.connected):
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = PropertyResponse(_ROT.position)
        return vars(R)


# -------
# Reverse
# -------
#
@api.route('/<int:DeviceNumber>/Reverse', methods=['GET','PUT'])
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class Reverse(Resource):

    @api.doc(description='Returns the Rotator\'s <b>Reverse</b> state.')
    @api.marshal_with(m_BoolResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        if (not _ROT.connected):
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        devno = DeviceNumber
        cid = request.args.get('ClientID', 1234)
        R = PropertyResponse(_ROT.reverse)
        return vars(R)

    @api.doc(description='Sets the Rotator\'s <b>Reverse</b> state.')
    @api.marshal_with(m_MethodResponse, description='Driver response')
    @api.expect(m_ReverseValue)
    def put(self, DeviceNumber):
        global reverse
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        if (not _ROT.connected):
            R = MethodResponse(ASCOMErrors.NotConnected)
            return vars(R)
        devno = DeviceNumber                            # Whatever this might be used for
        cid = api.payload['ClientID']                   # Ditto
        _ROT.reverse = api.payload['Reverse']
        R = MethodResponse()
        return vars(R)


# --------
# StepSize
# --------
#
@api.route('/<int:DeviceNumber>/StepSize', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class StepSize(Resource):

    @api.doc(description='The minimum angular step size (degrees).')
    @api.marshal_with(m_FloatResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        if (not _ROT.connected):
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = PropertyResponse(_ROT.step_size)
        return vars(R)


# --------------
# TargetPosition
# --------------
#
@api.route('/<int:DeviceNumber>/TargetPosition', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class TargetPosition(Resource):

    @api.doc(description='The destination mechanical angle for <b>Move()</b> and <b>MoveAbsolute()</b>.')
    @api.marshal_with(m_FloatResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        if (not _ROT.connected):
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = PropertyResponse(_ROT.target_position)
        return vars(R)


# ----
# Halt
# ----
#

@api.route('/<int:DeviceNumber>/Halt', methods=['PUT'])
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class Halt(Resource):

    @api.doc(description='Immediately stop any Rotator motion due to a previous <b>Move()</b> or <b>MoveAbsolute()</b>.')
    @api.marshal_with(m_MethodResponse, description='Driver response')
    def put(self, DeviceNumber):
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        if (not _ROT.connected):
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        devno = DeviceNumber                            # Whatever this might be used for
        cid = api.payload['ClientID']                   # Ditto
        _ROT.Halt()
        R = MethodResponse()
        return vars(R)


# ----
# Move
# ----
#

@api.route('/<int:DeviceNumber>/Move', methods=['PUT'])
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class Move(Resource):
    
    
    @api.doc(description='Causes the rotator to move <b>Position</b> degrees relative to the current <b>Position</b>.')
    @api.marshal_with(m_MethodResponse, description='Driver response')
    @api.expect(m_RelPosValue)
    def put(self, DeviceNumber):
        global target_position
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        if (not _ROT.connected):
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        _ROT.Move(position + float(api.payload['Position']))
        devno = DeviceNumber                            # Whatever this might be used for
        cid = api.payload['ClientID']                   # Ditto
        R = MethodResponse()
        return vars(R)


# ------------
# MoveAbsolute
# -------------
#

@api.route('/<int:DeviceNumber>/MoveAbsolute', methods=['PUT'])
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'DeviceNumber, command, or parameter velues, are missing or invalid', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class MoveAbsolute(Resource):
    
    @api.doc(description='Causes the rotator to move the absolute position of <b>Position</b> degrees.')
    @api.marshal_with(m_MethodResponse, description='Driver response')
    @api.expect(m_AbsPosValue)
    def put(self, DeviceNumber):
        global target_position
        if (DeviceNumber != 0):
            abort(400, 'No such DeviceNumber.')
        if (not _ROT.connected):
            R = PropertyResponse(None, ASCOMErrors.NotConnected)
            return vars(R)
        _ROT.Move(float(api.payload['Position']))
        devno = DeviceNumber                            # Whatever this might be used for
        cid = api.payload['ClientID']                   # Ditto
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

    #HOST = os.environ.get('SERVER_HOST', 'localhost')

    #try:
    #    PORT = int(os.environ.get('SERVER_PORT', '5555'))
    #except ValueError:
    #    PORT = 5555
    #app.run(HOST, PORT, debug=True)
    app.run('127.0.0.1', 5555)
