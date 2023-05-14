import json
import app.state as state

def _escape(s):
    return s.replace('"', '&quot;')

def index_html():
    return f"""<!doctype html>
<html lang="en">
<head>
  <title>Pico</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <link rel="stylesheet" type="text/css" href="style.css" />
  <script src="app.js"></script>
</head>
<body><div id="react-root" data-state="{_escape(json.dumps(state.current()))}"></div></body>
</hmtl>"""
