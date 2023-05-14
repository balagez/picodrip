from log import info
import threading

STA_IF = 0

STAT_IDLE = 0
STAT_CONNECTING = 1
STAT_WRONG_PASSWORD = 2
STAT_NO_AP_FOUND = 3
STAT_CONNECT_FAIL = 4
STAT_GOT_IP = 5

ip = '127.0.0.1'

class WLAN:
    
    def __init__(self, interface):
        self._interface = interface
        self._connecting = False
        self._connected = False
        pass

    def active(self, value):
        pass
    
    def connect(self, ssid, password):
        info(f'[network] Connect to {ssid}, password={password}')
        self._connecting = True
        self._connected = False

        def connected():
            self._connecting = False
            self._connected = True

        timer = threading.Timer(0.5, connected)
        timer.start()
    
    def disconnect(self):
        self._connecting = False
        self._connected = False

    def isconnected(self):
        return self._connected
    
    def status(self):
        if self._connected:
            return STAT_GOT_IP
        elif self._connecting:
            return STAT_CONNECTING
        return STAT_IDLE

    def ifconfig(self):
        if self._connected:
            return [ip]
        return ['0.0.0.0']
