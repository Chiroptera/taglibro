import taglibro
from gevent import wsgi

server = wsgi.WSGIServer(('0.0.0.0', 5000), taglibro.app)
server.serve_forever()
