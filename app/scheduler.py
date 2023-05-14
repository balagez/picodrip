from machine import Timer
import utime
import app.state
import app.pumps

_already_run = set()

def _check_schedule(timer):
    global _already_run

    _, _, _, h, m, _, wd, _ = utime.localtime()

    for schedule in app.state.get_schedule():
        pump = schedule['pump']
        key = (wd, h, m, pump)

        if key in _already_run:
            continue

        if wd not in schedule['weekdays'] or h != schedule['hour'] or m != schedule['minute']:
            continue
        
        _already_run.add(key)
        app.pumps.blink(pump, schedule['duration'] * 1000, caller='scheduler')
    
    # make sure to clean up previous days from tracker, otherwise after a week nothing would run
    _already_run = set([k for k in _already_run if k[0] == wd])


def start():
    Timer(period=2000, mode=Timer.PERIODIC, callback=_check_schedule)
