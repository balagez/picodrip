import os
import utime
from app.files import EVENT_LOG, PUMP_LOG

def _timestamp():
    return str(utime.time())

def _event(kind, message):
    line = f'{_timestamp()} {kind} {message}'
    print(line)
    with open(EVENT_LOG, 'a') as f:
        f.write(line + '\n')

def logrotate(logfile, older_than=604800):
    cutoff = utime.time() - older_than
    new_logfile = logfile + '.new'
    with open(logfile, 'r') as f:
        with open(new_logfile, 'w') as n:
            for line in f.readlines():
                ts = int(line.split( )[0])
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
        _event(self.kind, f'[info] {message}')
    
    def warn(self, message):
        _event(self.kind, f'[warn] {message}')
    
    def error(self, message):
        _event(self.kind, f'[error] {message}')
    
    def pump(self, i, on, caller):
        with open(PUMP_LOG, 'a') as f:
            line = f'{_timestamp()} {i} {on} {caller or ""}'
            f.write(line + '\n')
