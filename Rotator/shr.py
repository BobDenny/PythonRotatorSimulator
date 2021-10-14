# pylint: disable=C0301,C0103,C0111,W0603
# For W0603 'Using Global statement" I believe this is correct.
# Common strings and form functions
#
# 23-Jan-2021  rbd  V0.8 Common version strings for form footers, etc.
# 10-Oct-2021  rbd  V0.9 Python 3.7, updatated packages.
# 13-Oct-2021  rbd  0.9 Linting with some messages disabled, no docstrings
#
from threading import Lock
import ASCOMErrors

# -----------
# Driver Info
# -----------
m_DriverVersion = '0.9'                                 # Major.Minor only also used in form footers
m_DriverVerDate = '12-Oct-2021'                         # Form footers
m_DriverAPIVersions = [1]                               # Supported API Versions


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
s_DescClId =    'Client\'s unique ID (0 to 4294967295). The client should choose a value at start-up, e.g. a random value between 0 and 65535, and send this value on every transaction to help associate entries in device logs with this particular client'
s_DescCtId =    'Client\'s transaction ID (0 to 4294967295). The client should start this count at 1 and increment by one on each successive transaction. This will aid associating entries in device logs with corresponding entries in client side logs.'
s_DescStId =    'Server\'s transaction ID (0 to 4294967295), should be unique for each client transaction so that log messages on the client can be associated with logs on the device.'
s_DescErrNum =  'Zero for a successful transaction, or a non-zero integer (-2147483648 to 2147483647) if the device encountered an issue. Devices must use ASCOM reserved error numbers whenever appropriate so that clients can take informed actions. E.g. returning 0x401 (1025) to indicate that an invalid value was received (see Alpaca API definition and developer documentation for further information).'
s_DescErrMsg =  'Empty string for a successful transaction, or a message describing the issue that was encountered. If an error message is returned, a non zero error number must also be returned.'
s_DescGetRsp =  'Driver response'
s_DescMthRsp =  'Transaction complete or exception'

#
# Common/shared response strings
#
s_Resp400Missing =  'Method or parameter value error, check error message'
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
        #dict.__init__()
        self.ServerTransactionID = getNextTransId()
        self.Value = value
        ctid = get_args_caseless(s_FldCtId, args, 1)
        if not ctid is None:
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
        #dict.__init__()
        self.ServerTransactionID = getNextTransId()
        ctid = get_args_caseless(s_FldCtId, form, 1)
        if not ctid is None:
            self.ClientTransactionID = ctid
        else:
            self.ClientTransactionID = 0        # Per Alpaca, Return a 0 if ClientTransactionId is not in the request
        self.ErrorNumber = err.Number
        self.ErrorMessage = err.Message


# -------------------------------
# Thread-safe ServerTransactionID
# -------------------------------
_lock = Lock()
_tid = 0

# Pylint flags the use of global here but I think it is right
def getNextTransId():
    global _tid     # False lint "Using the global statement" ??
    _lock.acquire()
    _tid += 1
    _lock.release()
    return _tid
