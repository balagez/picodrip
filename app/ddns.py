import socket
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
    
    request = f'GET {PATH} HTTP/1.1\r\nHost: {HOST}\r\n\r\n'.encode('ascii')
    sockaddr = socket.getaddrinfo(HOST, PORT)[0][-1]
    s = socket.socket()
    s.settimeout(10)
    s.connect(sockaddr)
    s.send(request)
    response = s.recv(4096).decode()
    s.close()
    
    status = None
    body = ''
    headers_done = False
    for line in response.split('\r\n'):
        if headers_done:
            body += line.strip() + ' '
        if not status:
            status = line
        if not line:
            headers_done = True
    
    log.info(status + ' ' + body)
