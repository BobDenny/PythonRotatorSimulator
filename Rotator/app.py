# https://ascom-standards.org/api
# https://exploreflask.com/en/latest/views.html#url-converters

import os
from flask import Flask, Blueprint, request
from flask_restplus import Api, Resource, fields

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
            title='ASCOM Rotator Simulator API', 
            description='<h2><img src=\'static/Bug72T.jpg\' align=\'right\' width=\'72\' ' + 
                'height=\'84\' />This device is an ASCOM Rotator simulator that responds to ' +
                'the standard REST API for Rotator</h2>')
app.register_blueprint(blueprint)

# =========
# App State
# =========
#
# Including initialization (default contents)
# 
# State
#
position = 0.0 
can_reverse = True
reverse = False
step_size = 1.0
target_position = 0.0
is_moving = False

#
# Connection
#
svrtransid = 0                                           # Counts up

# ==========================
# Models and Wrapper Classes
# ==========================

m_ErrorMessage = api.model('ErrorMessage', {'Value' : fields.String(description='Error message', required=True)})

# -----------------
# ScalarPropResponse
# -----------------
# Construct the response fpor a property-get of a scalar. Common
# to all of the properties in this driver. Models (see below) 
# differ to specify data type and documentation of Value.
#
class ScalarPropResponse(dict):
    def __init__(self, value, method, clitransid):
        global svrtransid
        svrtransid += 1
        self.Value = value
        self.ClientTransactionIDForm = clitransid
        self.ServerTransactionID = svrtransid
        self.Method = method
        self.ErrorNumber = 0
        self.ErrorMessage = ''
        self.DriverException = None

m_BoolResponse = api.model('BoolResponse', 
                                {   'Value'                   : fields.Boolean(description='True or False value.', required=True),
                                    'ClientTransactionIDForm' : fields.Integer(description='Client\'s transaction ID.'),
                                    'ServerTransactionID'     : fields.Integer(description='Server\'s transaction ID.'),
                                    'Method'                  : fields.String(description='Name of the calling method.'),
                                    'ErrorNumber'             : fields.Integer(description='Error number from device.'),
                                    'ErrorMessage'            : fields.String(description='Error message description from device.')
                                })

# --------------
# MethodResponse
# --------------
#
class MethodResponse(dict):
    def __init__(self, method, clitransid):
        global svrtransid
        svrtransid += 1
        self.ClientTransactionIDForm = clitransid
        self.ServerTransactionID = svrtransid
        self.Method = method
        self.ErrorNumber = 0
        self.ErrorMessage = ''
        self.DriverException = None

m_MethodResponse = api.model('MethodResponse', 
                                {   'ClientTransactionIDForm' : fields.Integer(description='Client\'s transaction ID.'),
                                    'ServerTransactionID'     : fields.Integer(description='Server\'s transaction ID.'),
                                    'Method'                  : fields.String(description='Name of the calling method.'),
                                    'ErrorNumber'             : fields.Integer(description='Error number from device.'),
                                    'ErrorMessage'            : fields.String(description='Error message description from device.')
                               })

# ==============================
# API ENDPOINTS (REST Resources)
# ==============================

# ----------
# CanReverse
# ----------
#
@api.route('/<int:DeviceNumber>/CanReverse', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
#@api.doc(description='This is a class test') #Probably shows in all methods
@api.response(400, 'Method or parameter value error, check error message', m_ErrorMessage)
@api.response(404, 'No such DeviceNumber or Endpoint', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class CanReverse(Resource):

    @api.doc(description='True if the Rotator supports the <b>Reverse</b> method.')
    @api.marshal_with(m_BoolResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            api.abort(404)
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = ScalarPropResponse(can_reverse, request.method, request.args.get('ClientTransactionID', 1))
        return vars(R)


# --------
# IsMoving
# --------
#
@api.route('/<int:DeviceNumber>/IsMoving', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
#@api.doc(description='This is a class test') #Probably shows in all methods
@api.response(400, 'Method or parameter value error, check error message', m_ErrorMessage)
@api.response(404, 'No such DeviceNumber or Endpoint', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class IsMoving(Resource):

    @api.doc(description='True if the Rotator is currently moving to a new position. False if the Rotator is stationary.')
    @api.marshal_with(m_BoolResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            api.abort(404)
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = ScalarPropResponse(is_moving, request.method, request.args.get('ClientTransactionID', 1))
        return vars(R)


# --------
# Position
# --------
#
@api.route('/<int:DeviceNumber>/Position', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
#@api.doc(description='This is a class test') #Probably shows in all methods
@api.response(400, 'Method or parameter value error, check error message', m_ErrorMessage)
@api.response(404, 'No such DeviceNumber or Endpoint', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class Position(Resource):

    @api.doc(description='Current instantaneous Rotator mechanical angle (degrees).')
    @api.marshal_with(m_BoolResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            api.abort(404)
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = ScalarPropResponse(position, request.method, request.args.get('ClientTransactionID', 1))
        return vars(R)


# -------
# Reverse
# -------
#

@api.route('/<int:DeviceNumber>/Reverse', methods=['GET','PUT'])
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
#@api.doc(description='This is a class test') #Probably shows in all methods
@api.response(400, 'Method or parameter value error, check error message', m_ErrorMessage)
@api.response(404, 'No such DeviceNumber or Endpoint', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class Reverse(Resource):

    m_ReverseValue = api.model('ReverseValue',
                    {'Reverse'               : fields.Boolean(False, description='True if the rotation and angular ' + 
                                                                        'direction must be reversed to match the optical ' +
                                                                        'characteristics', required=True),
                    'ClientID'               : fields.Integer(1, description='Client\'s unique ID'),
                    'ClientTransactionID'    : fields.Integer(1234, description='Client\'s transaction ID')
                    })
    
    @api.doc(description='Returns the Rotator\'s <b>Reverse</b> state.')
    @api.marshal_with(m_BoolResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            api.abort(404)
        devno = DeviceNumber
        cid = request.args.get('ClientID', 1234)
        R = ScalarPropResponse(reverse, request.method, request.args.get('ClientTransactionID', 1))
        return vars(R)

    @api.doc(description='Sets the Rotator\'s <b>Reverse</b> state.')
    @api.marshal_with(m_MethodResponse, description='Driver response')
    @api.expect(m_ReverseValue)
    def put(self, DeviceNumber):
        global reverse
        if (DeviceNumber != 0):
            api.abort(404)
        devno = DeviceNumber                            # Whatever this might be used for
        cid = api.payload['ClientID']                   # Ditto
        reverse = api.payload['Reverse']
        R = MethodResponse(request.method, api.payload['ClientTransactionID'])
        return vars(R)


# --------
# StepSize
# --------
#
@api.route('/<int:DeviceNumber>/StepSize', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
#@api.doc(description='This is a class test') #Probably shows in all methods
@api.response(400, 'Method or parameter value error, check error message', m_ErrorMessage)
@api.response(404, 'No such DeviceNumber or Endpoint', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class StepSize(Resource):

    @api.doc(description='The minimum angular step size (degrees).')
    @api.marshal_with(m_BoolResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            api.abort(404)
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = ScalarPropResponse(step_size, request.method, request.args.get('ClientTransactionID', 1))
        return vars(R)


# --------------
# TargetPosition
# --------------
#
@api.route('/<int:DeviceNumber>/TargetPosition', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
#@api.doc(description='This is a class test') #Probably shows in all methods
@api.response(400, 'Method or parameter value error, check error message', m_ErrorMessage)
@api.response(404, 'No such DeviceNumber or Endpoint', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class TargetPosition(Resource):

    @api.doc(description='The destination mechanical angle for <b>Move()</b> and <b>MoveAbsolute()</b>.')
    @api.marshal_with(m_BoolResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            api.abort(404)
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = ScalarPropResponse(target_position, request.method, request.args.get('ClientTransactionID', 1))
        return vars(R)


# ----
# Halt
# ----
#

@api.route('/<int:DeviceNumber>/Halt', methods=['PUT'])
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
#@api.doc(description='This is a class test') #Probably shows in all methods
@api.response(400, 'Method or parameter value error, check error message', m_ErrorMessage)
@api.response(404, 'No such DeviceNumber or Endpoint', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class Halt(Resource):

    @api.doc(description='Immediately stop any Rotator motion due to a previous <b>Move()</b> or <b>MoveAbsolute()</b>.')
    @api.marshal_with(m_MethodResponse, description='Driver response')
    def put(self, DeviceNumber):
        ##TODO## Implement halting the rotator
        if (DeviceNumber != 0):
            api.abort(404)
        devno = DeviceNumber                            # Whatever this might be used for
        cid = api.payload['ClientID']                   # Ditto
        R = MethodResponse(request.method, api.payload['ClientTransactionID'])
        return vars(R)


# ----
# Move
# ----
#

@api.route('/<int:DeviceNumber>/Move', methods=['PUT'])
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
#@api.doc(description='This is a class test') #Probably shows in all methods
@api.response(400, 'Method or parameter value error, check error message', m_ErrorMessage)
@api.response(404, 'No such DeviceNumber or Endpoint', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class Move(Resource):
    
    m_RelPosValue = api.model('RelPosValue',
                    {'Position'              : fields.Float(0.0, description='Angle to move in degrees relative to the current <b>Position</b>.', required=True),
                    'ClientID'               : fields.Integer(1, description='Client\'s unique ID'),
                    'ClientTransactionID'    : fields.Integer(1234, description='Client\'s transaction ID')
                    })
    
    @api.doc(description='Causes the rotator to move <b>Position</b> degrees relative to the current <b>Position</b>.')
    @api.marshal_with(m_MethodResponse, description='Driver response')
    @api.expect(m_RelPosValue)
    def put(self, DeviceNumber):
        global target_position
        if (DeviceNumber != 0):
            api.abort(404)
        target_position = position + float(api.payload['Position'])
        ##TODO## Implement relative moving the rotator
        devno = DeviceNumber                            # Whatever this might be used for
        cid = api.payload['ClientID']                   # Ditto
        R = MethodResponse(request.method, api.payload['ClientTransactionID'])
        return vars(R)


# ------------
# MoveAbsolute
# -------------
#

@api.route('/<int:DeviceNumber>/MoveAbsolute', methods=['PUT'])
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
@api.response(400, 'Method or parameter value error, check error message', m_ErrorMessage)
@api.response(404, 'No such DeviceNumber or Endpoint', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class MoveAbsolute(Resource):
    
    m_AbsPosValue = api.model('AbsPosValue',
                    {'Position'              : fields.Float(0.0, description='Destination mechanical angle to which the rotator will move (degrees).', required=True),
                    'ClientID'               : fields.Integer(1, description='Client\'s unique ID'),
                    'ClientTransactionID'    : fields.Integer(1234, description='Client\'s transaction ID')
                    })
    
    @api.doc(description='Causes the rotator to move the absolute position of <b>Position</b> degrees.')
    @api.marshal_with(m_MethodResponse, description='Driver response')
    @api.expect(m_AbsPosValue)
    def put(self, DeviceNumber):
        global target_position
        if (DeviceNumber != 0):
            api.abort(404)
        target_position = float(api.payload['Position'])
        ##TODO## Implement absolute moving the rotator
        devno = DeviceNumber                            # Whatever this might be used for
        cid = api.payload['ClientID']                   # Ditto
        R = MethodResponse(request.method, api.payload['ClientTransactionID'])
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
