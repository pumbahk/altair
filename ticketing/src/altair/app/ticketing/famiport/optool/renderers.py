# -*- coding: utf-8 -*-

import altair.app.ticketing.csvutils as csv
from StringIO import StringIO
from datetime import datetime

class CSVRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            content_type = response.content_type
            if content_type == response.default_content_type:
                response.content_type = 'application/octet-stream; charset=Windows-31J'
                response.content_disposition = 'attachment; filename=refund_tickets_{date}.csv'.format(date=datetime.now().strftime('%Y%m%d%H%M%S'))

        fout = StringIO()
        writer = csv.writer(fout, delimiter=',', quotechar=',')

        writer.writerow(value.get('header', []))
        writer.writerows(value.get('rows', []))

        return fout.getvalue()
