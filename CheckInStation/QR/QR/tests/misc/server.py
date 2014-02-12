# -*- coding:utf-8 -*-
import SimpleHTTPServer
import SocketServer
import logging
import cgi
import time
PORT = 8000

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        logging.info(self.headers)
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        logging.info(self.headers)
        import time
        time.sleep(0.2)
        # form = cgi.FieldStorage(
        #     fp=self.rfile,
        #     headers=self.headers,
        #     environ={'REQUEST_METHOD':'POST',
        #              'CONTENT_TYPE':self.headers['Content-Type'],
        #              })
        # for item in form.list:
        #     logging.error(item)
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

Handler = ServerHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()
