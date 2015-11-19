# -*- coding: utf-8 -*-

#
# altair.renderers にしたい
#

import json
import csv
from lxml import etree
import StringIO

def json_renderer_factory(info):
    def _render(value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            status = value.get('_status')
            if status is None:
                if value.get('success', True):
                    status = 200
                else:
                    status = 401
            else:
                del value['_status']
            response.status = int(status)
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = 'application/json'
        return json.dumps(value)
    return _render

def safe_encode(s, encoding='utf-8', errors='replace'):
    if s is None:
        return None
    elif isinstance(s, str):
        return s
    elif isinstance(s, unicode):
        return s.encode(encoding, errors=errors)
    else:
        raise TypeError

def stringize(s):
    if not isinstance(s, basestring):
        return unicode(s)
    else:
        return s

def csv_renderer_factory(info):
    default_encoding = 'cp932'

    def _value(value, encoding):
        if isinstance(value, (list, tuple)):
            return safe_encode(stringize(value[1]), encoding)
        return safe_encode(stringize(value), encoding)
    
    def _render(value, system):
        encoding = value.get('encoding', default_encoding)
        request = system.get('request')
        if request is not None:
            response = request.response
            f = StringIO.StringIO()
            writer = csv.writer(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
            row_num = 0
            if value['data']:
                for line in value['data']:
                    if not line:
                        continue
                    if not row_num:
                        writer.writerow([safe_encode(stringize(s), encoding) for s in line.keys()])
                    row_num += 1
                    writer.writerow([_value(item, encoding) for item in line.items()])
            output = f.getvalue()
            f.close()
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_disposition = 'attachment; filename=%s' % (value['filename'])
            return output
    return _render

def lxml_renderer_factory(info):
    def _render(value, system):
        request = system.get('request')
        charset = 'UTF-8'
        if request is not None:
            response = request.response
            ct = response.content_type
            if response.charset:
                charset = response.charset
            if ct == response.default_content_type:
                response.content_type = 'text/xml'
                response.charset = charset
        return etree.tostring(value, xml_declaration=True, encoding=charset)
    return _render 

def includeme(config):
    config.add_renderer('json'  , 'altair.app.ticketing.renderers.json_renderer_factory')
    config.add_renderer('csv'   , 'altair.app.ticketing.renderers.csv_renderer_factory')
    config.add_renderer('lxml'  , 'altair.app.ticketing.renderers.lxml_renderer_factory')
