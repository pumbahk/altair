# -*- coding: utf-8 -*-
from __future__ import absolute_import
import six
import csv
from io import BytesIO

def safe_encode(s, encoding='utf-8', errors='replace'):
    if s is None:
        return None
    elif isinstance(s, six.binary_type):
        return s
    elif isinstance(s, six.text_type):
        return s.encode(encoding, errors=errors)
    else:
        raise TypeError

def stringize(s):
    if not isinstance(s, six.text_type):
        return six.text_type(s)
    else:
        return s

class CSV(object):
    def __init__(self, default_encoding='cp932'):
        self.default_encoding = default_encoding

    def __call__(self, info):
        def _value(value, encoding):
            if isinstance(value, (list, tuple)):
                return safe_encode(stringize(value[1]), encoding)
            return safe_encode(stringize(value), encoding)
        
        def _render(value, system):
            encoding = value.get('encoding', self.default_encoding)
            request = system.get('request')
            if request is not None:
                response = request.response
                f = BytesIO()
                writer = csv.writer(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
                row_num = 0
                for line in value['data']:
                    if not row_num:
                        writer.writerow([safe_encode(stringize(s), encoding) for s in line.keys()])
                    row_num += 1
                    writer.writerow([_value(item, encoding) for item in line.items()])
                output = f.getvalue()
                ct = response.content_type
                if ct == response.default_content_type:
                    response.content_disposition = 'attachment; filename=%s' % (value['filename'])
                return output
        return _render
