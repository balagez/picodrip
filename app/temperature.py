import machine

_sensor = machine.ADC(4)
_conversion_factor = 3.3 / 65535

def read():
    reading = _sensor.read_u16() * _conversion_factor
    return 27 - (reading - 0.706) / 0.001721
