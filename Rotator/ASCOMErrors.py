#
# Common ASCOM Exceptions - Only those for the Rotator
#
# See ASCOM Platform Developer Help > ASCOM Namespaces > ASCOM > Error Codes Class
#
DriverBase = 0x80040500             # Starting value for driver-specific exceptions
DriverMax = 0x80040FFF              # Maximum value for driver-specific excptions

class Success(object):
    Number = 0
    Message = ''

class ActionNotImplementedException(object):
    Number = 0x8004040C
    Message = 'The requested action is not implemented in this driver.'

class InvalidOperationException(object):
    Number = 0x8004040B
    Message = 'The requested operation cannot be undertaken at this time.'

class InvalidValue(object):
    Number = 0x80040401
    Message = 'Invalid value.'

class NotConnected(object):
    Number = 0x80040407
    Message = 'The communications channel is not connected'

class NotImplemented(object):
    Number = 0x80040400
    Message = 'Property or method not implemented'

class UnspecifiedError(object):
    Number = 0x800404FF
    Message = 'Unspecified error in device or driver.'

class ValueNotSet(object):
    Number = 0x80040402
    Message = 'The value has not yet been set.'

#
# Specific errors for Rotator
#