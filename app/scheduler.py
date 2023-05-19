from machine import Timer
import micropython
import app.state
import app.pumps
import app.events

_already_run = set()
_previous_weekday = None

log = app.events.Logger('scheduler')

def _check_schedule():
    global _already_run
    global _previous_weekday
    global _logrotate_in_progress

    _, _, _, h, m, _, wd, _ = app.events.localtime()

    for schedule in app.state.get_schedule():
        pump = schedule['pump']
        key = (wd, h, m, pump)

        if key in _already_run:
            continue

        if wd not in schedule['weekdays'] or h != schedule['hour'] or m != schedule['minute']:
            continue
        
        log.info(f'Running schedule {schedule}')
        
        _already_run.add(key)
        app.pumps.blink(pump, schedule['duration'] * 1000, caller='scheduler')
    
    # make sure to clean up previous days from tracker, otherwise after a week nothing would run
    _already_run = set([k for k in _already_run if k[0] == wd])
    
    # log rotate once every day
    if wd != _previous_weekday:
        _previous_weekday = wd
        try:
            app.events.logrotate_all()
        except Exception as e:
            log.error(f'Rotating logs failed: {e}')
        

def _cb_check_schedule(timer):
    micropython.schedule(lambda arg: _check_schedule(), None)
    
def start():
    # every 20 seconds
    Timer(period=20 * 1000, mode=Timer.PERIODIC, callback=_cb_check_schedule)
