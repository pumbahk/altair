# -*- coding: utf-8 -*-
import csv
import cStringIO


class WordCSVRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            content_type = response.content_type
            if content_type == response.default_content_type:
                response.content_type = 'application/octet-stream; charset=shift_jis'
                response.content_disposition = 'attachment; filename=お気に入り登録者.csv'.format()

        file_out = cStringIO.StringIO()
        writer = csv.writer(file_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([s.encode("shift_jis") for s in value.get(u'header', [])])
        for row in value.get(u'rows', []):
            writer.writerow([s.encode("shift_jis") for s in row])
        return file_out.getvalue()
