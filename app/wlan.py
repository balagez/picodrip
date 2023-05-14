import network
import utime
import app.ddns
from app.events import Logger

_SSID = ''
_PASSWORD = ''

_wlan = network.WLAN(network.STA_IF)
_wlan.active(True)

log = Logger('wlan')

def _connect():
    _wlan.connect(_SSID, _PASSWORD)

def _wait_and_reconnect(error):
    log.error(error)
    utime.sleep(5)
    _connect()
    
def connect():
    log.info(f'Connecting to {_SSID}...')
    _connect()
    while _wlan.isconnected() == False:
        status = _wlan.status()
        
        if status == network.STAT_NO_AP_FOUND:
            _wait_and_reconnect(f'AP {_SSID} not found')
        elif status == network.STAT_WRONG_PASSWORD:
            _wait_and_reconnect(f'Wrong password for {_SSID}')
        elif status == network.STAT_CONNECT_FAIL:
            _wait_and_reconnect(f'Failed to connect to {_SSID}')
        else:
            log.info(f'Waiting for connection...')
            utime.sleep(1)

    ip = _wlan.ifconfig()[0]
    log.info(f'Connected on {ip}')
    app.ddns.update_ddns(ip)
    return ip

def ensure_connected():
    if not _wlan.isconnected():
        log.error(f'Lost connection to {_SSID}')
        _wlan.disconnect()
        connect()
