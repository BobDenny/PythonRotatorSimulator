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

    def start(self, from_run=False):
        #print('[start] try to lock')
        self._lock.acquire()
        #print('[start] got lock')
        if from_run or self._stopped:
            self._stopped = False
            #print('[start] new timer')
            self._timer = Timer(self._interval, self._run)
            #print('[start] now start the timer')
            self._timer.start()
            #print('[start] timer started')
            self._lock.release()
            #print('[start] lock released')
        else:
            self._lock.release()
            #print('[start] lock released')


    def _run(self):
        #print('[_run] (tmr expired) get lock')
        self._lock.acquire()
        #print('[_run] got lock : tgtpos=' + str(self._target_position) + ' pos=' + str(self._position))
        delta = self._target_position - self._position
        #if delta >= 360.0:
        #    delta -= 360.0
        #if delta < 0.0:
        #    delta += 360.0
        #    print('[_run] final delta = ' + str(delta))
        if abs(delta) > (self._step_size / 2.0):
            self._is_moving = True
            if delta > 0:
                #print('[_run] delta > 0 go positive')
                self._position += self._step_size
                if self._position >= 360.0:
                    self._position -= 360.0
            else:
                #print('[_run] delta < 0 go negative')
                self._position -= self._step_size
                if self._position < 0.0:
                    self._position += 360.0
            print('[_run] new pos = ' + str(self._position))
        else:
            self._is_moving = False
            self._stopped = True
        self._lock.release()
        #print('[_run] lock released')
        if self._is_moving:
            #print('[_run] more motion needed, start another timer interval')
            self.start(from_run = True)

    def stop(self):
        self._lock.acquire()
        self._stopped = True
        self._is_moving = False
        self._timer.cancel()
        self._lock.release()

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
        self._isMoving = True
        self._target_position = self._position + pos
        if self.target_position >= 360.0:
            self.target_position -= 360.0
        if self.target_position < 0.0:
            self.target_position += 360.0
        self._lock.release()
        self.start()

    def MoveAbsolute(self, pos):
        self._lock.acquire()
        self._is_moving = True
        self._target_position = pos
        self._lock.release()
        self.start()

    def Halt(self):
        self.stop()
