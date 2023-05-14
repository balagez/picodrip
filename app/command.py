import app.state
import app.pumps
from app.events import Logger

log = Logger('command')

class Errors:
    command = 'Expected: (state|pump|schedule) {args}'
    pump = 'Expected: pump {i} (on {duration_ms}|off)'
    schedule = 'Expected: schedule\\n{schedule1}\\n...'


def parse_and_run(args, clientIP):
    try:
        cmd, *data = args.split('\n')
        log.info(f'{cmd} client={clientIP}')
        cmd, *args = cmd.split()
    except:
        raise ValueError(Errors.command)
    
    if cmd == 'state':
        pass
    elif cmd == 'pump':
        _command_pump(args)
    elif cmd == 'schedule':
        app.state.set_schedule(data)
    else:
        raise ValueError(Errors.command)


def _command_pump(args):
    try:
        i, action,  *args = args
    except:
        raise ValueError(Errors.pump)
    
    try:
        i = int(i)
    except:
        raise ValueError(f'Invalid number: {i}')
    
    if action == 'on':
        try:
            duration_ms = int(args[0])
        except:
            raise ValueError('Invalid duration')
        
        if duration_ms < 100:
            raise ValueError('The minimum duration is 100ms')
            
        if duration_ms > 10000:
            raise ValueError('The maximum duration is 10s')
        
        app.pumps.blink(i, duration_ms)
    elif action == 'off':
        app.pumps.off(i)
    else:
        raise ValueError(Errors.pump)
