# -*- coding: utf-8 -*-

import sys
import logging
import os
from wsgiref.simple_server import make_server
from .nwts import NWTS

logger = logging.getLogger(__name__)

def run():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s"
    )

    argv = sys.argv
    if (len(argv) != 3):
        logger.info('usage: python %s {host} {port}' % argv[0])
        quit()

    host = argv[1]
    port = int(argv[2])

    nwts = NWTS(
        tmpdir=os.path.join(os.path.dirname(__file__), 'tmp'),
        params={
            '-s':'ifile2.sej.co.jp',
            '-d':'/nwtsweb/ticket/upload',
            '-t':'60022000',
            '-p':'60022a',
            '-f':'SEIT020U',  #'TEST010U'
            '-e':'payback.seam',
            }
        )
    httpd = make_server(host, port, nwts)
    logger.info('start httpd %s:%s' % (host, port))
    httpd.serve_forever()


if __name__ == '__main__':
    run()
