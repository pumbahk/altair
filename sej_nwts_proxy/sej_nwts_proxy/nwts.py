# -*- coding: utf-8 -*-

import os
import cgi
import logging
import subprocess
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NWTS(object):
    def __init__(self, tmpdir, params):
        self.tmpdir = tmpdir
        self.params = params

    def generate_filename(self):
        # 前日の日付にする
        return '%s.zip' % (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

    def save_file(self, fs):
        if not fs.has_key('zipfile'):
            logger.warn('param "zipfile" not found')
            return False

        fileitem = fs['zipfile']
        if fileitem.file:
            zipfile = os.path.join(self.tmpdir, self.generate_filename())
            fout = open(zipfile, 'wb')
            try:
                while True:
                    chunk = fileitem.file.read(100000)
                    if not chunk: break
                    fout.write(chunk)
            finally:
                fout.close()
            logger.info('save file ok %s' % zipfile)
            return zipfile

        logger.warn('save file failed (fileitem=%r)' % fileitem)
        return False

    def send(self, fs, filename):
        command = ['nwtsUL.exe']
        for key, value in self.params.items():
            if fs.has_key(key):
                value = fs[key].value
                logger.info('%s=%s' % (key, value))
            command += [key, value]
        command += ['-o', filename]
        logger.info('sending sej file command => %s' % command)
        status_code = 0
        result = ''
        try:
            result = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            status_code = e.returncode
            result = e.output
        logger.info('sending sej file response => [%d] %s' % (status_code, result))
        return status_code, result

    def __call__(self, environ, start_response):
        fs = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
        filename = self.save_file(fs)
        response_body = ''
        if filename:
            status_code, result = self.send(fs, filename)
            if status_code != 0:
                status = '500 Internal Server Error'
            else:
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

