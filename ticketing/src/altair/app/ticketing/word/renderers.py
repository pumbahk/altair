# -*- coding: utf-8 -*-
import csv
import io


class WordCSVRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            content_type = response.content_type
            if content_type == response.default_content_type:
                response.content_type = 'application/octet-stream; charset=UTF-16'
                response.content_disposition = 'attachment; filename=お気に入り登録者.csv'.format()

        file_out = io.BytesIO()
        writer = csv.writer(file_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(value.get(u'header', []))
        writer.writerows(value.get(u'rows', []))
        return file_out.getvalue()
