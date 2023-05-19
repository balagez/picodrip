import os
import utime
import ntptime
from micropython import const
from app.files import EVENT_LOG, PUMP_LOG

_zone_offset = -4
_time_set = False
_KIND = const('events')
_INFO = const('info')
_WARN = const('warn')
_ERROR = const('error')

def start():
    global _time_set
    try:
        _event(_KIND, _INFO, 'Getting time from NTP')
        ntptime.settime()
        _event(_KIND, _INFO, 'Got time from NTP')
        _time_set = True
    except Exception as e:
        _event(_KIND, _ERROR, f'Failed get time from NTP: {e}')

def localtime():
    now = utime.time() + 3600 * _zone_offset
    return utime.localtime(now)

def _timestamp():
    if not _time_set:
        return str(utime.time()) + '?'
    return str(utime.time())

def _event(kind, level, message):
    line = f'{_timestamp()} {kind} [{level}] {message}'
    print(line)
    with open(EVENT_LOG, 'a') as f:
        f.write(line + '\n')

def logrotate(logfile, older_than=604800):
    cutoff = utime.time() - older_than
    new_logfile = logfile + '.new'
    with open(logfile, 'r') as f:
        with open(new_logfile, 'w') as n:
            for line in f.readlines():
                ts = int(line[0:10])
                if ts > cutoff:
                    n.write(line)
    os.remove(logfile)
    os.rename(new_logfile, logfile)

def logrotate_all():
    logrotate(EVENT_LOG)
    logrotate(PUMP_LOG)

class Logger:
    
    def __init__(self, kind):
        self.kind = kind
        
    def info(self, message):
        _event(self.kind, _INFO, message)
    
    def warn(self, message):
        _event(self.kind, _WARN, message)
    
    def error(self, message):
        _event(self.kind, _ERROR, message)
    
    def pump(self, i, on, caller):
        with open(PUMP_LOG, 'a') as f:
            line = f'{_timestamp()} {i} {on} {caller or ""}'
            f.write(line + '\n')
