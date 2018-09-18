
import base64
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from six import text_type

from alertaclient.exceptions import AuthError

SUCCESS_MESSAGE = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>Alerta Login</title>
    </head>
    <body>
        <h1>Authorization success!</h1>
        <p>Please close the web browser and return to the terminal.</p>
    </body>
</html>
"""


class HTTPServerHandler(BaseHTTPRequestHandler):

    def __init__(self, request, address, server, xsrf_token):
        self.xsrf_token = xsrf_token
        self.access_token = None
        BaseHTTPRequestHandler.__init__(self, request, address, server)

    def do_GET(self):
        try:
            qp = parse_qs(urlparse(self.path).query)
        except Exception as e:
            raise AuthError(e)

        if 'state' in qp and qp['state'][0] != self.xsrf_token:
            raise AuthError('CSRF token is invalid. Please try again.')
        if 'code' in qp:
            self.server.access_token = qp['code'][0]
        elif 'error' in qp:
            raise AuthError(qp['error'])

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(SUCCESS_MESSAGE.encode('utf-8')))

    def log_message(self, format, *args):
        return


class TokenHandler:

    def get_access_token(self, xsrf_token):
        server_address = ('', 9004)
        httpd = HTTPServer(server_address, lambda request, address,
                           server: HTTPServerHandler(request, address, server, xsrf_token))
        httpd.handle_request()
        return httpd.access_token


class Jwt:

    def parse(self, jwt):
        payload = jwt.split('.')[1]
        if isinstance(payload, text_type):
            payload = payload.encode('ascii')
        padding = b'=' * (4 - (len(payload) % 4))
        decoded = base64.urlsafe_b64decode(payload + padding)
        return json.loads(decoded.decode('utf-8'))
