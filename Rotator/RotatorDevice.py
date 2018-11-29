#
# Implements a Rotator device
#

import threading
from threading import Thread

class RotatorDevice(threading.Thread):
    """Implements a rotator device that runs in a separate thread"""

    #
    # Rotator device constants
    #
    _can_reverse = True
    _step_size = 1.0 
    _steps_per_sec = 6

    #
    # Rotator device state variables
    #
    _reverse = False
    _position = 0.0 
    _target_position = 0.0
    _is_moving = False
    _connected = False
    _lock = None

    #
    # Only override __init_()  and run() (pydoc 17.1.2)
    #
    def __init__(self):
        self._lock = threading.Lock()
        Thread.__init__(self)
        self.name = 'device'
        self._position = 0.0 
        self._target_position = 0.0
        self._is_moving = False
        self._connected = False

    def run(self):
        pass

    #
    # Guarded properties
    # **TODO** Catch lock failures and raise error.
    #
    @property
    def can_reverse(self):
        self._lock.acquire()
        res =  self._can_reverse
        self._lock.release()
        return res

    @property
    def reverse(self):
        self._lock.acquire()
        res =  self._reverse
        self._lock.release()
        return res
    @reverse.setter
    def reverse (self, reverse):
        self._lock.acquire()
        self._reverse = reverse
        self._lock.release()

    @property
    def step_size(self):
        self._lock.acquire()
        res =  self._step_size
        self._lock.release()
        return res

    @property
    def position(self):
        self._lock.acquire()
        res = self._position
        self._lock.release()
        return res

    @property
    def target_position(self):
        self._lock.acquire()
        res =  self._target_position
        self._lock.release()
        return res

    @property
    def is_moving(self):
        self._lock.acquire()
        res =  self._is_moving
        self._lock.release()
        return res

    @property
    def connected(self):
        self._lock.acquire()
        res =  self._connected
        self._lock.release()
        return res
    @connected.setter
    def connected (self, connected):
        self._lock.acquire()
        self._connected = connected
        self._lock.release()

    #
    # Methods
    #
    def Move(self, position):
        pass

    def MoveAbsolute(self, position):
        pass

    def Halt(self):
        pass

