#-*- coding: utf-8 -*-
import time
from pyramid.response import Response
from pyramid.view import (
    view_config,
    view_defaults,
    )
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap

from . import csvfile

class _GettiiBaseView(BaseView):
    pass

@view_defaults(route_name='gettii.venue', decorator=with_bootstrap, permission='event_editor')
class VenueView(_GettiiBaseView):

    @view_config(route_name='gettii.venue.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/gettii/venues.html')
    def index(self):
        return {'venue': self.context.venue,
                'external_venues': self.context.external_venues,
                'upload_form': ExternalVenueUploadForm(),
                }

    @view_config(route_name='gettii.venue.download', request_method='GET')
    def download(self):
        res = Response()
        csvdata = csvfile.AltairGettiiVenueCSV()
        csvdata.load(self.context.venue)
        csvdata.write_csv(res)
        filename = 'GETTII_VENUE_DONWLOAD_ALTAIR_{}_{}.csv'.format(self.context.venue.id, time.strftime('%Y%m%d%H%M%S'))
        res.headers = [('Content-Type', 'application/octet-stream; charset=cp932'),
                       ('Content-Disposition', 'attachment; filename={0}'.format(filename)),
                       ]
        return res

    @view_config(route_name='gettii.venue.upload', request_method='GET')
    def upload(self):
        return {'venue': self.context.venue,
                'external_venues': self.context.external_venues,
                'upload_form': ExternalVenueUploadForm(),
                }
