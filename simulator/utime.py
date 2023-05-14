import time as pytime

def time():
    return round(pytime.time())

def localtime(t = None):
    t = pytime.localtime(t)
    return [ t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, t.tm_wday, t.tm_yday ]

def sleep(t):
    pytime.sleep(t)
