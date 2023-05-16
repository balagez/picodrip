from machine import Pin, Timer
import micropython
from app.events import Logger

_OFF = 1
_ON = 0

_pins = {
    1: Pin(18, mode=Pin.OUT, value=_OFF),
    2: Pin(19, mode=Pin.OUT, value=_OFF),
    3: Pin(20, mode=Pin.OUT, value=_OFF),
    4: Pin(21, mode=Pin.OUT, value=_OFF),
}

_keys = sorted(_pins.keys())

log = Logger('pump')

def assert_exists(i):
    if i not in _pins:
        raise ValueError(f'Invalid pump: {i}')

def keys():
    return _keys

def on(i, caller='manual'):
    assert_exists(i)
    log.info(f'{i} ON caller={caller}')
    log.pump(i, 1, caller)
    _pins[i].value(_ON)

def off(i, caller='manual'):
    assert_exists(i)
    log.info(f'{i} OFF caller={caller}')
    log.pump(i, 0, caller)
    _pins[i].value(_OFF)

def _cb_scheduled_off(i, caller):        
    return lambda timer: micropython.schedule(lambda arg: off(i, caller), None)

def blink(i, duration_ms, caller='manual'):
    assert_exists(i)
    on(i, caller)
    Timer(period=duration_ms, mode=Timer.ONE_SHOT, callback=_cb_scheduled_off(i, caller))

def is_on(i):
    assert_exists(i)
    return _pins[i].value() == _ON
