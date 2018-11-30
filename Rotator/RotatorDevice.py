#
# Implements a Rotator device
#

from threading import Timer
from threading import Lock

class RotatorDevice(object):
    """Implements a rotator device that runs in a separate thread"""
    #
    # Only override __init_()  and run() (pydoc 17.1.2)
    #
    def __init__(self):
        self._lock = Lock()
        self.name = 'device'
        #
        # Rotator device constants
        #
        self._can_reverse = True
        self._step_size = 1.0 
        self._steps_per_sec = 6
        #
        # Rotator device state variables
        #
        self._reverse = False
        self._position = 0.0 
        self._target_position = 0.0
        self._is_moving = False
        self._connected = False
        #
        # Rotator engine
        #
        self._timer = None
        self._interval = 1.0 / self._steps_per_sec
        self._stopped = True
        self.start()                        # SELF STARTING

    def start(self, from_run=False):
        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = Timer(self._interval, self._run)
            self._timer.start()
            self._lock.release()
        else:
            self._lock.release()


    def _run(self):
        self.start(from_run = True)
        self._lock.acquire()
        delta = self._target_position - self._position
        if delta >= 360.0:
            delta -= 360.0
        if delta < 0.0:
            delta += 360.0
        if abs(delta) > self._step_size:
            self._position = self._position + (self._step_size * [-1 if delta < 0 else 1])
            print('pos=' + _self.position)
        self._lock.release()

    def stop(self):
        self._lock.acquire()
        self.stopped = True
        self._timer.cancel()
        self._lock.release()
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
    def Move(self, pos):
        self._lock.acquire()
        self._target_position = self._position + pos
        if self.target_position >= 360.0:
            self.target_position -= 360.0
        if self.target_position < 0.0:
            self.target_position += 360.0
        self._lock.release()
        start()

    def MoveAbsolute(self, pos):
        self._lock.acquire()
        self._target_position = pos
        if self.target_position >= 360.0:
            self.target_position -= 360.0
        if self.target_position < 0.0:
            self.target_position += 360.0
        self._lock.release()
        start()

    def Halt(self):
        stop()

