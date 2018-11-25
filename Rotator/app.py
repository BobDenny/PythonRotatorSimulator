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
blueprint = Blueprint('Rotator', __name__, url_prefix='/API/V1/Rotator')   # Create a URL prefix for the whole application
api = Api(default='Rotator', default_label='<h2>ASCOM REST V1 for Rotator Devices: Base URL = <tt>/API/V1/Rotator')
api.init_app(blueprint, 
                version = '1.0',
                title='ASCOM Rotator Simulator API', 
                description='<h2>This device is an ASCOM Rotator simulator that responds to the standard REST API for Rotator</h2>')
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
step_size = 0.1
target_position = 0.0
#
# Connection
#
svrtransid = 0                                           # Counts up

# ==========================
# Models and Wrapper Classes
# ==========================

m_ErrorMessage = api.model('ErrorMessage', {'Value' : fields.String(description='Error message', required=True)})

# ------------
# BoolResponse
# ------------
class BoolResponse(dict):
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

@api.route('/<int:DeviceNumber>/CanReverse', methods=['GET']) 
@api.param('DeviceNumber', 'Zero-based device number as set on the server', 'path', type='integer', default='0')
#@api.doc(description='This is a class test') #Probably shows in all methods
@api.response(400, 'Method or parameter value error, check error message', m_ErrorMessage)
@api.response(404, 'No such DeviceNumber or Endpoint', m_ErrorMessage)
@api.response(500, 'Server internal error, check error message', m_ErrorMessage)
class CanReverse(Resource):

    @api.doc(description='True if the Rotator supports the <b>Reverse</b> method')
    @api.marshal_with(m_BoolResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            api.abort(404)
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1234)
        R = BoolResponse(can_reverse, request.method, request.args.get('ClientTransactionID', 1))
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
    
    @api.doc(description='Returns the Rotator\'s <b>Reverse</b> state')
    @api.marshal_with(m_BoolResponse, description='Driver response')
    @api.param('ClientID', 'Client\'s unique ID', 'query', type='integer', default='1234')
    @api.param('ClientTransactionID', 'Client\'s transaction ID', 'query', type='integer', default='1')
    def get(self, DeviceNumber):
        if (DeviceNumber != 0):
            api.abort(404)
        devno = DeviceNumber
        cid = request.args.get('ClientID', 1234)
        R = BoolResponse(reverse, request.method, request.args.get('ClientTransactionID', 1))
        return vars(R)

    @api.doc(description='Sets the Rotator\'s <b>Reverse</b> state')
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
    app.run('127.0.0.1', 5555, debug=True)
