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
#api = Api(validate=True, doc='/documentation')          # Validates input to Swagger documentation and moves Swagger off root
api = Api()
api.init_app(blueprint, 
                title='ASCOM Rotator API', 
                description='This implements a demo of the ASCOM Rest API for Rotator')
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

# ------------
# BoolResponse
# ------------
class BoolResponse(dict):
    def __init__(self, value, method, clitransid):
        self.Value = value
        self.ClientTransactionIDForm = 0
        self.ServerTransactionID = 0
        self.Method = method
        self.ErrorNumber = 0
        self.ErrorMessage = ''
        self.DriverException = None

m_BoolResponse = api.model('BoolResponse', 
                                {   'Value'                   : fields.Boolean('True or False value.'),
                                    'ClientTransactionIDForm' : fields.Integer('Client\'s transaction ID.'),
                                    'ServerTransactionID'     : fields.Integer('Server\s transaction ID.'),
                                    'Method'                  : fields.String('Name of the calling method.'),
                                    'ErrorNumber'             : fields.Integer('Error number from device.'),
                                    'ErrorMessage'            : fields.String('Error message description from device.')
                                })

# --------------
# MethodResponse
# --------------
class MethodResponse(dict):
    def __init__(self, method, clitransid):
        self.ClientTransactionIDForm = 0
        self.ServerTransactionID = 0
        self.Method = method
        self.ErrorNumber = 0
        self.ErrorMessage = ''
        self.DriverException = None

m_MethodResponse = api.model('MethodResponse', 
                                {   'ClientTransactionIDForm' : fields.Integer('Client\'s transaction ID.'),
                                    'ServerTransactionID'     : fields.Integer('Server\s transaction ID.'),
                                    'Method'                  : fields.String('Name of the calling method.'),
                                    'ErrorNumber'             : fields.Integer('Error number from device.'),
                                    'ErrorMessage'            : fields.String('Error message description from device.')
                               })

# ==============================
# API ENDPOINTS (REST Resources)
# ==============================

# --------
# language - List ([]) of 'Language' per the model above 
# --------
#
@api.route('/<int:DeviceNumber>/CanReverse') 
class CanReverse(Resource):

    def get(self, DeviceNumber):
        devno = DeviceNumber                    # Used later for multi-device (typ.)
        cid = request.args.get('ClientID', 1)
        R = BoolResponse(can_reverse, request.method, request.args.get('ClientTransactionID', 1234))
        return vars(R)


@api.route('/<int:DeviceNumber>/Reverse', methods=['GET','PUT'])
class Reverse(Resource):

    def get(self, DeviceNumber):
        devno = DeviceNumber
        cid = request.args.get('ClientID', 1)
        R = BoolResponse(reverse, request.method, request.args.get('ClientTransactionID', 1234))
        return vars(R)

    def post(self, DeviceNumber):
        devno = DeviceNumber
        cid = request.args.get('ClientID', 1)
        reverse = api.payload['Reverse']
        R = MethodResponse(request.method, request.args.get('ClientTransactionID', 1234))
        return vars(R)

# ==================
# SERVER APPLICATION
# ==================
#
# Start it this way to get  the automatic tab on Chrome
# with the right host/port.
#
if __name__ == '__main__':

    HOST = os.environ.get('SERVER_HOST', 'localhost')

    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
