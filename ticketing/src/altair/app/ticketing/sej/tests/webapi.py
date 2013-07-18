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
        self.th = None

    def handler(self, environ, start_response):
        self.request = webob.Request(environ)
        response = webob.Response(self.callback(environ))
        response.status = self.status
        return response(environ, start_response)

    def start(self):
        self.httpd = make_server(self.host, self.port, self.handler)
        self.th = threading.Thread(target=self.httpd.handle_request)
        self.th.start()

    def stop(self):
        if self.th is not None and self.th.is_alive():
            import httplib
            conn = httplib.HTTPConnection(self.httpd.server_address[0], self.httpd.server_address[1])
            conn.request('GET', '/')
            self.poll()

    def poll(self):
        self.httpd.server_close()
        self.th.join()

