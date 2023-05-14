import os
import json
import time
from app import temperature
import app.pumps
import app.schedule
from app.events import Logger
from app.files import CONFIG_FILE

_config = {}

log = Logger('state')

SCHEDULE_KEY = 'schedule'

try:
    with open(CONFIG_FILE, 'r') as f:
        _config = json.loads(f.read())

    schedules = []
    for s in _config[SCHEDULE_KEY] or []:
        try:
            schedules.append(app.schedule.parse(s))
        except Exception as e:
            log.error(f'Failed to parse scheudle "{s}": {e}')
    
    _config[SCHEDULE_KEY] = schedules
except Exception as e:
    log.error('Failed to parse config file: {e}')
    _config = {}

def _pump_state():
    return {f'pump{i}': app.pumps.is_on(i) for i in app.pumps.keys()}

def _serialize_schedule():
    return list(map(app.schedule.serialize, _config[SCHEDULE_KEY]))

def get_schedule():
    return _config[SCHEDULE_KEY]

def set_schedule(data):
    new_schedule = []
    for unparsed in data:
        parsed = app.schedule.parse(unparsed)
        app.pumps.assert_exists(parsed['pump'])
        new_schedule.append(parsed)
    _config[SCHEDULE_KEY] = new_schedule
    save()

def current():
    data = {
        'time': int(time.time()),
        'temp': temperature.read(),
        'schedule': _serialize_schedule(),
    }
    data.update(_pump_state())
    return data

def save():
    data = {
        'schedule': _serialize_schedule(),
    }
    with open(CONFIG_FILE, 'w') as f:
        f.write(json.dumps(data))
