from app.http import Router, ContentTypes, BadRequestError
import app.command
import app.state as state
from app.html import index_html
from app.events import Logger

router = Router()
log = Logger('routes')

@router.route('/')
def index(req, res):
    res.html(index_html())

@router.route('/favicon.ico')
def favicon(req, res):
    res.ttl(31536000) # 1 year
    res.file('static/favicon.ico', ContentTypes.ICO)

@router.route('/logo.svg')
def favicon(req, res):
    res.ttl(31536000) # 1 year
    res.file('static/logo.svg', ContentTypes.SVG)

@router.route('/style.css')
def favicon(req, res):
    res.ttl(3600)
    res.file('static/style.css', ContentTypes.CSS)

@router.route('/app.js')
def favicon(req, res):
    res.ttl(3600)
    res.file('static/app.js', ContentTypes.JAVASCRIPT)

@router.route('/events.log')
def favicon(req, res):
    res.ttl(5)
    res.file('events.log', ContentTypes.TEXT)

@router.route('/pumps.log')
def favicon(req, res):
    res.ttl(5)
    res.file('pumps.log', ContentTypes.TEXT)

@router.route('/api/command', methods=['POST'])
def api_command(req, res):
    try:
        app.command.parse_and_run(req.text(), req.clientIP)
        res.json(state.current())
    except ValueError as e:
        raise BadRequestError(e)
