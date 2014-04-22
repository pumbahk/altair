# -*- coding:utf-8 -*-
import SimpleHTTPServer
import BaseHTTPServer
import SocketServer
import logging
import cgi
import time
import shutil

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    unstable = False	
    def parse_request(self):
        """
        print("----------------------------------------")
        print(self.raw_requestline)
        """
        result = SimpleHTTPServer.SimpleHTTPRequestHandler.parse_request(self)
        """
        print(self.headers)
        print("----------------------------------------")
        """
        return result

    def do_GET(self):
        logging.info(self.headers)
        if self.unstable:
      	    import random
      	    N = random.random()
            print(N)
            if N > 0.5:
	             print("error")
	             return
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def copyfile(self, source, outputfile):
        #if "update." in source.name:
        #    time.sleep(10)
        return shutil.copyfileobj(source, outputfile)

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
        self.do_GET()
        #print("body:")
        print(self.rfile.read())

import sys
if len(sys.argv) >= 2:
    PORT = int(sys.argv[1])
else:
    PORT = 8000

try:
    unstable = bool(sys.argv[2])
    print("unstable error rate = 0.5")
except:
    unstable = False

Handler = ServerHandler
#Server = SocketServer.TCPServer
Server = BaseHTTPServer.HTTPServer

#xxx:
Handler.unstable = unstable
httpd = Server(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()
