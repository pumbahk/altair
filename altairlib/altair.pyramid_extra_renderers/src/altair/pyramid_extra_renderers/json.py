# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import date
from decimal import Decimal
import json

class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, Decimal):
            return unicode(o.quantize(0))
        else:
            return super(MyJSONEncoder, self).default(o)


class JSON(object):
    def __init__(self, status_handler=None, ensure_ascii=False):
        self.status_handler = status_handler
        self.encoder = MyJSONEncoder(ensure_ascii=ensure_ascii)

    def __call__(self, info):
        def _render(value, system):
            request = system.get('request')
            if request is not None:
                response = request.response
                if self.status_handler is not None:
                    status = self.status_handler(request, value)
                    if status is not None:
                        response.status = status
                ct = response.content_type
                if ct == response.default_content_type:
                    response.content_type = 'application/json'
            return self.encoder.encode(value)
        return _render
