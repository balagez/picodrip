from machine import Timer
import micropython
import utime
import app.state
import app.pumps
import app.events

_already_run = set()

def _check_schedule():
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

def _cb_check_schedule(timer):
    micropython.schedule(lambda arg: _check_schedule(), None)
    
def _cb_logrotate_all(timer):
    micropython.schedule(lambda arg: app.events.logrotate_all(), None)
    
def start():
    # every 20 seconds
    Timer(period=20 * 1000, mode=Timer.PERIODIC, callback=_cb_check_schedule)

    # now and then once every day
    app.events.logrotate_all()
    Timer(period=7 * 3600 * 1000, mode=Timer.PERIODIC, callback=_cb_logrotate_all)
