import utime
from app.files import EVENT_LOG, PUMP_LOG

TIMEZONE = '-'

def timestamp():
    y, m, d, h, i, s, _, _ = utime.localtime()
    return f'{y}-{m:02d}-{d:02d}T{h:02d}:{i:02d}:{s:02d}'

def _event(kind, message):
    line = f'{timestamp()} {kind} {message}'
    print(line)
    with open(EVENT_LOG, 'a') as f:
        f.write(line + '\n')

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
            line = f'{timestamp()} {i} {on} {caller or ""}'
            f.write(line + '\n')
