# pylint: disable=C0301,C0103,C0111
#
# Common ASCOM Exceptions
#
# See ASCOM Platform Developer Help > ASCOM Namespaces > ASCOM > Error Codes Class
# On Alpaca, the lowest 12 bits are used as the error. When interoperating with
# Windows, the OS bits #0x80040000 are OR-ed with the error to form the Windows
# OS-wide error codes per the Windows ASCOM spec.
# 12-Oct-2020   rbd     Add Exception to end of name to avoid built-ins
DriverBase = 0x400      # Starting value for driver-specific exceptions
DriverMax = 0xFFF       # Maximum value for driver-specific excptions

class Success(object):
    Number = 0
    Message = ''

class ActionNotImplementedException(object):
    Number = 0x40C
    Message = 'The requested action is not implemented in this driver.'

class InvalidOperationException(object):
    Number = 0x40B
    Message = 'The requested operation cannot be undertaken at this time.'

class InvalidValueException(object):
    Number = 0x401
    Message = 'Invalid value.'

class NotConnectedException(object):
    Number = 0x407
    Message = 'The communications channel is not connected'

class NotImplementedException(object):
    Number = 0x400
    Message = 'Property or method not implemented'

class UnspecifiedErrorException(object):
    Number = 0x4FF
    Message = 'Unspecified error in device or driver.'

class ValueNotSetException(object):
    Number = 0x402
    Message = 'The value has not yet been set.'
