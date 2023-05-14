SEP = '/'

def dirname(path):
    return SEP.join(path.split(SEP)[:-1])

def resolve(path):
    res = []
    skip_next = False
    for part in reversed(path.split(SEP)):
        if skip_next:
            skip_next = False
            continue
        elif part == '.':
            continue
        elif part == '..':
            skip_next = True
        else:
            res.insert(0, part)
    return SEP.join(res)

ROOT_DIR = resolve(dirname(__file__) + '/..')

EVENT_LOG = ROOT_DIR + '/events.log'
PUMP_LOG = ROOT_DIR + '/pumps.log'

CONFIG_FILE = ROOT_DIR + '/config.json'
