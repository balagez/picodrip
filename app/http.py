import os
import utime
import uio
import json
from app.events import Logger
from app.files import ROOT_DIR

delim = '\r\n'
delim_byes = delim.encode()

SERVER = 'pico'

log = Logger('http')

class Status:
    OK                    = 200
    NOT_MODIFIED          = 304
    BAD_REQUEST           = 400
    NOT_FOUND             = 404
    INTERNAL_SERVER_ERROR = 500

class HeaderNames:
    CACHE_CONTROL      = 'cache-control'
    CONTENT_LENGTH     = 'content-length'
    CONTENT_TYPE       = 'content-type'
    DATE               = 'date'
    ETAG               = 'etag'
    IF_MODIFIED_SINCE  = 'if-modified-since'
    IF_NONE_MATCH      = 'if-none-match'
    LAST_MODIFIED      = 'last-modified'
    SERVER             = 'server'

class ContentTypes:
    TEXT       = 'text/plain; charset=utf-8'
    HTML       = 'text/html; charset=utf-8'
    JSON       = 'application/json'
    CSS        = 'text/css'
    SVG        = 'image/svg+xml'
    ICO        = 'image/x-icon'
    JAVASCRIPT = 'text/javascript'

STATUS_TEXTS = {
    Status.OK:                    'OK',
    Status.NOT_MODIFIED:          'Not Modified',
    Status.BAD_REQUEST:           'Bad Request',
    Status.NOT_FOUND:             'Not Found',
    Status.INTERNAL_SERVER_ERROR: 'Internal Server Error',
}

DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def httpTime(timestamp):
    year, month, mday, hour, minute, second, weekday, _ = utime.localtime(timestamp)
    dayAbbr = DAYS[weekday]
    monthAbbr = MONTHS[month-1]
    return '{}, {:02d} {} {:04d} {:02d}:{:02d}:{:02d} GMT'.format(dayAbbr, mday, monthAbbr, year, hour, minute, second)

def parseHttpTime(s):
    _, day, month, year, t, _ = s.split()
    hour, minute, second = t.split(':')
    month = MONTHS.index(month)+1
    return utime.mktime((int(year), month, int(day), int(hour), int(minute), int(second), 0, 0, 0))

def _emptyBody(writer):
    pass


class RequestError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message

class BadRequestError(RequestError):
    def __init__(self, message):
        super().__init__(Status.BAD_REQUEST, message)


class Request:
    
    @classmethod
    async def create(cls, reader, writer):
        try:
            self = Request()
            self._method = None
            self._url = None
            self._version = 'HTTP/2'
            self._headers = {}
            self._body = bytearray()
            self._clientIP = writer.get_extra_info('peername')[0]
        
            # parse request line
            request_line = await reader.readline()
            method, url, version = request_line.decode('ascii').strip().split()
            self._method = method
            self._url = url
            self._version = version
            
            # parse headers
            while True:
                header_line = await reader.readline()
                if header_line == b'\r\n':
                    break
                name, value = header_line.decode('ascii').strip().split(': ')
                self._headers[name.lower()] = value
            
            # read body
            bytes_to_read = 0
            if HeaderNames.CONTENT_LENGTH in self._headers:
                try:
                    bytes_to_read = int(self._headers[HeaderNames.CONTENT_LENGTH])
                except ValueError:
                    pass
            
            chunk_size = 1024
            while bytes_to_read > 0:
                bytes_read = min(chunk_size, bytes_to_read)
                self._body += await reader.read(bytes_read)
                bytes_to_read -= bytes_read
        except ValueError:
            log.error(f'Invalid request: {request_line}')
        except Exception as e:
            log.error(f'Error while parsing request: {e}')
        finally:
            return self
            
    @property
    def method(self):
        return self._method

    @property
    def version(self):
        return self._version
    
    @property
    def clientIP(self):
        return self._clientIP
    
    def header(self, name):
        lc_name = name.lower()
        return self._headers[lc_name] if lc_name in self._headers else None
    
    @property
    def url(self):
        return self._url
    
    def body(self):
        return bytes(self._body)
    
    def text(self):
        return self._body.decode('utf-8')
    
    def json(self):
        try:
            return json.loads(self._body.decode('utf-8'))
        except ValueError as e:
            raise RequestError(Status.BAD_REQUEST, str(e))
        

class Response:
    
    def __init__(self, req):
        self._req = req
        self._version = req.version or 'HTTP/2'
        self.status = Status.OK
        self._headers = []
        self._contentType = None
        self._contentLength = 0
        self._writeBody = _emptyBody
        self._writeBodyAsync = None
    
    @property
    def status(self):
        return self._status
        
    @status.setter
    def status(self, value):
        if value not in STATUS_TEXTS:
            raise ValueError(f'Unsupported status: {value}')
        self._status = value
        self._statusText = STATUS_TEXTS[value]

    @property
    def statusText(self):
        return self._statusText
        
    def header(self, name, value):
        self._headers.append((name, value))
    
    def etag(self, etag, weak):
        prefix = 'W/' if weak else ''
        self.header(HeaderNames.ETAG, f'{prefix}"{etag}"')
    
    def send(self, data, contentType):
        self._contentType = contentType
        self._contentLength = len(data)
        if not isinstance(data, bytes):
            data = str(data).encode()
        self._writeBody = lambda writer: writer.write(data)
        
    def text(self, data):
        self.send(data, ContentTypes.TEXT)
    
    def html(self, data):
        self.send(data, ContentTypes.HTML)
    
    def json(self, data):
        self.send(json.dumps(data), ContentTypes.JSON)
    
    def jsonError(self, status, error):
        self.status = status
        if isinstance(error, Exception):
            message = f'{error.__class__.__name__}: {error}'
        else:
            message = error
        self.json({'error': message})
        
    def notModified(self):
        self.status = Status.NOT_MODIFIED
        self._contentType = None
        self._contentLength = None
        self._writeBody = _emptyBody
    
    def ttl(self, value):
        self.header(HeaderNames.CACHE_CONTROL, f'max-age={value}')
        
    def preventCaching(self):
        self.header(HeaderNames.CACHE_CONTROL, f'no-store')
    
    def file(self, file, contentType):
        try:
            file = ROOT_DIR + '/' + file
            stat = os.stat(file)
            size = stat[6]
            mtime = stat[8]
            
            ifmsHeader = self._req.header(HeaderNames.IF_MODIFIED_SINCE)
            if ifmsHeader:
                try:
                    ifms = parseHttpTime(ifmsHeader)
                    if mtime <= ifms:
                        return self.notModified()
                except Exception:
                    pass
                
            etag = f'W/"{mtime}"'
            
            etagHeader = self._req.header(HeaderNames.IF_NONE_MATCH)
            if etagHeader and etagHeader == etag:
                return self.notModified()

            async def writeFile(writer):
                with uio.open(file, 'rb') as f:                    
                    chunk_size = 1024
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        writer.write(chunk)
                        await writer.drain()
        
            self.status = Status.OK
            self._contentType = contentType
            self._contentLength = size
            self.header(HeaderNames.LAST_MODIFIED, httpTime(mtime))
            self.header(HeaderNames.ETAG, etag)
            self._writeBodyAsync = writeFile
        except OSError:
            self.status = Status.NOT_FOUND
            self._contentType = None
            self._contentLength = 0
            self._writeBody = _emptyBody
    
    async def writeTo(self, writer):
        def writeHeader(name, value):
            value and writer.write(f'{name}: {value}{delim}'.encode())
        
        log.info(f'{self._req.method} {self._req.url} -- {self._status}')
        writer.write(f'{self._version} {self._status} {self._statusText}{delim}'.encode())
        writeHeader(HeaderNames.SERVER, SERVER)
        writeHeader(HeaderNames.DATE, httpTime(utime.time()))
        writeHeader(HeaderNames.CONTENT_TYPE, self._contentType)
        writeHeader(HeaderNames.CONTENT_LENGTH, self._contentLength)
        [writeHeader(name, value) for name, value in self._headers]
        writer.write(delim_byes)
        if self._writeBodyAsync:
            await self._writeBodyAsync(writer)
        else:
            self._writeBody(writer)

        await writer.drain()
        writer.close()
        await writer.wait_closed()

class Router:
    _routes = {}
    
    def route(self, path, methods=['GET']):
        def _route(f):
            for method in methods:
                self._routes[(method, path)] = f
            return f
        return _route
    
    async def handle(self, reader, writer):
        try:
            req = await Request.create(reader, writer)
            res = Response(req)
            
            key = (req.method, req.url)
            if key in self._routes:
                try:
                    self._routes[key](req, res)
                except RequestError as e:
                    res.jsonError(e.status, e.message)
                except Exception as e:
                    res.jsonError(Status.INTERNAL_SERVER_ERROR, e)
            else:
                res.jsonError(Status.NOT_FOUND, 'Route not found')
            
            await res.writeTo(writer)
        
        except Exception as e:
            log.error(f'Unhandled exception: {e}')
            writer.close()
