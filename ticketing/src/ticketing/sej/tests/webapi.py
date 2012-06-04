__author__ = 'aodag'
import webob
from wsgiref.simple_server import make_server
import threading

class DummyServer(object):
    def __init__(self, callback, host="", port=8000, status=200):
        self.callback = callback
        self.host = host
        self.port = port
        self.status = status

    def handler(self, environ, start_response):
        self.request = webob.Request(environ)
        response = webob.Response(self.callback(environ))
        response.status = self.status
        return response(environ, start_response)

    @property
    def called(self):
        return hasattr(self, 'th') and not self.th.is_alive

    def start(self):
        self.th = threading.Thread(target=self._run)
        self.th.start()

    def _run(self):
        httpd = make_server(self.host, self.port, self.handler)
        httpd.handle_request()

    def assert_called(self):
        assert self.called

    def assert_body(self, expected):
        assert self.request.body == expected

    def assert_content_type(self, expected):
        assert self.request.content_type == expected

    def assert_url(self, expected):
        assert self.request.url == expected

    def assert_method(self, expected):
        assert self.request.method == expected