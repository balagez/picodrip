import socket
import app.http
from app.events import Logger

HOST = 'freedns.afraid.org'
PORT = 80
PATH = '/dynamic/update.php?V0t3RkJlMjZ0bk1IY1dCUEdybUE3SERjOjIxNDY5OTcz'

log = Logger('ddns')

_enabled = True

def disable_ddns():
    global _enabled
    _enabled = False

def update_ddns(ip):
    if not _enabled:
        log.info('DDNS is disabled')
        return

    log.info(f'Updating DDNS with {HOST}')
    status, body = app.http.get(HOST, PATH)
    log.info(status + ' ' + body)
