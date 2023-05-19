import socket
from micropython import const
import app.http
from app.events import Logger

_HOST = const('freedns.afraid.org')
_PATH = const('/dynamic/update.php?V0t3RkJlMjZ0bk1IY1dCUEdybUE3SERjOjIxNDY5OTcz')

log = Logger('ddns')

_enabled = True

def disable_ddns():
    global _enabled
    _enabled = False

def update_ddns(ip):
    if not _enabled:
        log.info('DDNS is disabled')
        return

    log.info(f'Updating DDNS with {_HOST}')
    status, body = app.http.get(_HOST, _PATH)
    log.info(status + ' ' + body)
