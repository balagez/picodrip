from log import info
import threading

_timer = None

def _start_timer(t):
    global _timer
    _timer = t
    _timer.start()

def reset():
    global _timer
    info(f'[machine] Reset')
    if _timer:
        _timer.cancel()

class Pin():

    OUT=0
    IN=1
    
    def __init__(self, num, mode=None, value=None):
        self._num = num
        self._value = value

    def value(self, v=None):
        if v is not None:
            if self._num != 'LED':
                info(f'[machine] Pin {self._num} set to {v}')
            self._value = v
        return self._value
    
    def on(self):
        return self.value(1)

    def off(self):
        return self.value(0)

class ADC():

    def __init__(self, num):
        self._num = num

    def read_u16(self):
        return 13942

class Timer():
    
    ONE_SHOT=0
    PERIODIC=1

    def __init__(self, period, mode, callback):
        period = period / 1000
        if mode == Timer.ONE_SHOT:
            _start_timer(threading.Timer(period, callback))
        elif mode == Timer.PERIODIC:
            def period_fn():
                callback()
                _start_timer(threading.Timer(period, period_fn))
            _start_timer(threading.Timer(period, period_fn))
