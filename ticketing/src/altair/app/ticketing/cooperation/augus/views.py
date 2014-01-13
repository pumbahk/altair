#-*- coding: utf-8 -*-
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap

@view_config(route_name='augus.test')
def test(*args, **kwds):
    return ValueError()

class _AugusBaseView(BaseView):
    pass

@view_defaults(route_name='augus.venue', decorator=with_bootstrap, permission='event_editor')
class AugusVenueView(_AugusBaseView):
    
    @view_config(route_name='augus.venue.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/venue.html')
    def index(self):
        return {'venue': self.context.venue}

    @view_config(route_name='augus.venue.download', request_method='GET')
    def download(self):
        res = Response()
        filename = 'AUGUS_VENUE_DONWLOAD.csv'
        res.headers = [('Content-Type', 'application/octet-stream; charset=cp932'),
                       ('Content-Disposition', 'attachment; filename={0}'.format(filename)),
                       ]
        res.write('a'*40)
        return res
    
    @view_config(route_name='augus.venue.upload', request_method='POST')                
    def upload(self):
        return {'venue': self.context.venue}
