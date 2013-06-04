# -*- coding: utf-8 -*-

import os
import cgi
import logging
import subprocess

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s"
)

def save_file(fs):
    if not fs.has_key('zipfile'):
        logger.warn('param "zipfile" not found')
        return False

    fileitem = fs['zipfile']
    if fileitem.file and fileitem.filename:
        zipfile = os.path.join('sej_nwts_proxy\\tmp', os.path.basename(fileitem.filename))
        fout = file(zipfile, 'wb')
        while True:
            chunk = fileitem.file.read(100000)
            if not chunk: break
            fout.write(chunk)
        fout.close()
        logger.info('save file ok %s' % zipfile)
        return zipfile

    logger.warn('save file failed')
    return False

def send(fs, filename):
    params = {
        '-s':'Inwts2.sej.co.jp',
        '-d':'/sdmt',
        '-t':'60022000',
        '-p':'60022a',
        '-f':'SEIT020U',  #'TEST010U'
        '-e':'tpayback.asp',
    }
    command = ['nwtsUL.exe']
    for key, value in params.items():
        if fs.has_key(key):
            value = fs[key].value
            logger.info('%s=%s' % (key, value))
        command += [key, value]
    command += ['-o', filename]
    logger.info('sending sej file command = %s' % command)
    result = subprocess.check_output(command, shell=True)
    logger.info('sending sej file response = %s' % result)
    return result

def nwts(environ, start_response):
    fs = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
    filename = save_file(fs)
    response_body = ''
    if filename:
        response_body = send(fs, filename)
        status = '200 OK'
    else:
        status = '400 Bad Request'

    response_headers = [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(response_body)))
    ]
    start_response(status, response_headers)

    logger.info('status = %s' % status)
    return [response_body]

