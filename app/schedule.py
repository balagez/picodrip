# Sat 12:00 3s
# Mon,Wed-Fri 12:00 10s
# Mon-Sun 15:00 5s

_day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

def parse(s):
    try:
        [pump, days, time, duration] = s.split()
    except:
        raise ValueError(f'Invalid schedule: {s}')

    try:
        pump = int(pump)
    except:
        raise ValueError(f'Invalid pump: {pump}')

    try:
        weekdays = set()
        for d in days.lower().split(','):
            ds = d.split('-')
            d1 = _day_names.index(_capitalize(ds[0]))
            d2 = _day_names.index(_capitalize(ds[1])) if len(ds) > 1 else d1
            for weekday in range(min(d1, d2), max(d1, d2) + 1):
                weekdays.add(weekday)
    except Exception as e:
        raise ValueError(f'Invalid days: {days}. Expected format is Tue-Wed,Fri')

    try:
        [hour, minute] = time.split(':')
        hour = int(hour)
        minute = int(minute)
    except:
        raise ValueError(f'Invalid time: {time}. Expected format is 17:35')
    
    if hour < 0 or hour > 23:
        raise ValueError(f'Invalid hour: {hour}')

    if minute < 0 or minute > 59:
        raise ValueError(f'Invalid minute: {minute}')
        
    try:
        duration = int(duration.strip('s'))
    except:
        raise ValueError(f'Invalid duration: {duration}. Expected format is 15s')

    if duration < 0 or duration > 120:
        raise ValueError(f'Duration must be between 1s and 120s')

    return {
        'pump': pump,
        'weekdays': weekdays,
        'hour': hour,
        'minute': minute,
        'duration': duration
    }

def serialize(schedule):
    if not schedule:
        return None
    pump = schedule['pump']
    weekdays = _collapse(list(schedule['weekdays']))
    hour = schedule['hour']
    minute = schedule['minute']
    duration = schedule['duration']
    return f'{pump} {weekdays} {hour}:{minute:02d} {duration}s'

def _capitalize(s):
    if not s:
        return s
    return s[0].upper() + s[1:]

def _collapse(arr):
    if not arr:
        return []

    arr = sorted(arr)
    
    ranges = []
    start = arr[0]
    end = arr[0]
    
    for i in range(1, len(arr)):
        if arr[i] == end + 1:
            end = arr[i]
        else:
            if start == end:
                ranges.append([_day_names[start]])
            else:
                ranges.append([_day_names[start], _day_names[end]])
            start = arr[i]
            end = arr[i]
    
    if start == end:
        ranges.append([_day_names[start]])
    else:
        ranges.append([_day_names[start], _day_names[end]])

    return ','.join(map(lambda r: '-'.join(r), ranges))
