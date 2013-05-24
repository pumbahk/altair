# -*- coding: utf-8 -*-
import json
import csv
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

def csv_renderer_factory(info):
    def _value(value):
        if isinstance(value, list):
            return unicode(value[1]).encode('sjis')
        if isinstance(value, tuple):
            return unicode(value[1]).encode('sjis')
        return value
    
    def _render(value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            f = StringIO.StringIO()
            writer = csv.writer(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
            row_num = 0
            for line in value['data']:
                if not row_num:
                    writer.writerow(line.keys())
                row_num += 1
                writer.writerow([_value(item) for item in line.items()])
            output = f.getvalue()
            f.close()
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_disposition = 'attachment; filename=%s' % (value['filename'])
            return output
    return _render