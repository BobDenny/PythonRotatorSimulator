import ASCOMErrors

# --------------
# Driver Version
# --------------
m_DriverVersion = '0.6'                                 # Major.Minor only

# ------------------------------
# Common strings used throughout
# ------------------------------

#
# Common/shared field name strings
#
s_FldDevNum =   'DeviceNumber'
s_FldClId =     'ClientID'
s_FldValue =    'Value'
s_FldCtId =     'ClientTransactionID'
s_FldStId =     'ServerTransactionID'
s_FldErrNum =   'ErrorNumber'
s_FldErrMsg =   'ErrorMessage'

#
# Common/shared description strings
#
s_DescDevNum =  'Zero-based device number as set on the server'
s_DescClId =    'Client\'s unique ID. The client should choose a random value at startup and send this value with every transaction.'
s_DescCtId =    'Client\'s transaction ID as supplied by the client in the command request. The cleint should start this count at 1 and increment by 1 on each successive transaction.'
s_DescStId =    'Server\'s transaction ID; should be unique for each client transaction so that log messages on the client can be associated with logs on the device.'
s_DescErrNum =  'Zero for a successful transaction, or a 12-bit non-zero Alpaca error code if the device encountered an issue.'
s_DescErrMsg =  'Empty string for a successful transaction, or a message describing the issue that was encountered.'
s_DescMthRsp =  'Transaction complete or exception'

#
# Common/shared response strings
#
s_Resp400Missing =  'DeviceNumber, command, or parameter values, are missing or invalid'
s_Resp400NoDevNo =  'No such DeviceNumber'
s_Resp500SrvErr =   'Server internal error, check error message'

#
# Get query string data with case-insensitive name
#
def get_args_caseless(name, args, default):
    lcName = name.lower()
    for an in args:
        if an.lower() == lcName:
            return args.get(an, default)
    return None                                         # not in args, let caller punt

#
# Get form data with case-insensitive name
#
def get_form_caseless(name, form, default):
    lcName = name.lower()
    for fn in form:
        if fn.lower() == lcName:
            return form.get(fn, default)
    return None                                         # not in form, let caller punt

# ------------------
# PropertyResponse
# ------------------
# Construct the response for a property-get. Common to all
# of the properties in this driver. Models (see below) 
# differ to specify data type and documentation of Value.
# NOTE: the api.marshal_with(..., skip_none=True) stops missing fields from coming back with value null
#
class PropertyResponse(dict):
    def __init__(self, value, args, err = ASCOMErrors.Success):
        self.ServerTransactionID = getNextTransId()
        self.Value = value
        ctid = get_args_caseless(s_FldCtId, args, 1)
        if (not ctid is None):
            self.ClientTransactionID = ctid
        else:
            self.ClientTransactionID = 0        # Per Alpaca, Return a 0 if ClientTransactionId is not in the request
        self.ErrorNumber = err.Number
        self.ErrorMessage = err.Message

# --------------
# MethodResponse
# --------------
#
class MethodResponse(dict):
    def __init__(self, form, err = ASCOMErrors.Success):
        self.ServerTransactionID = getNextTransId()
        ctid = get_args_caseless(s_FldCtId, form, 1)
        if (not ctid is None):
            self.ClientTransactionID = ctid
        else:
            self.ClientTransactionID = 0        # Per Alpaca, Return a 0 if ClientTransactionId is not in the request
        self.ErrorNumber = err.Number
        self.ErrorMessage = err.Message


# -------------------------------
# Thread-safe ServerTransactionID
# -------------------------------
import os
from threading import Lock

def init():
    global _lock
    global _tid
    _lock = Lock()
    _tid = 0

def getNextTransId():
    global _tid
    global _lock
    _lock.acquire();
    _tid += 1
    _lock.release()
    return _tid 

