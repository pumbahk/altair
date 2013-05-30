# -*- coding: utf-8 -*-

import sys
import logging
from wsgiref.simple_server import make_server
from .nwts import nwts, logger

def run():
    argvs = sys.argv
    if (len(argvs) != 3):
        logger.info('usage: python %s {host} {port}' % argvs[0])
        quit()

    host = argvs[1]
    port = int(argvs[2])

    httpd = make_server(host, port, nwts)
    logger.info('start httpd %s:%s' % (host, port))
    httpd.serve_forever()


if __name__ == '__main__':
    run()
