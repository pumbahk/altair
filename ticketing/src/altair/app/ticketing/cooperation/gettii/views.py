#-*- coding: utf-8 -*-
import time
from pyramid.response import Response
from pyramid.view import (
    view_config,
    view_defaults,
    )
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPFound,
    )
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from ..forms import ExternalVenueUploadForm
from . import csvfile
from . import importers

class _GettiiBaseView(BaseView):
    pass

@view_defaults(route_name='gettii.venue', decorator=with_bootstrap, permission='event_editor')
class VenueView(_GettiiBaseView):

    @view_config(route_name='gettii.venue.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/gettii/venues/show.html')
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

    @view_config(route_name='gettii.venue.upload', request_method='POST')
    def upload(self):
        form = ExternalVenueUploadForm(self.request.params)
        if form.validate() and hasattr(form.csv_file.data, 'file'):
            fp = form.csv_file.data.file
            csvdata = csvfile.AltairGettiiVenueCSV()
            csvdata.read_csv(fp)
            importer = importers.GettiiVenueImpoter()
            try:
                importer.import_(self.context.venue.id, csvdata)
            except GettiiVenueImportError as err:
                raise HTTPBadRequest(repr(err))
            url = self.request.route_path('gettii.venue.index', venue_id=self.context.venue.id)
            self.request.session.flash(u'登録しました')
            return HTTPFound(url)
        raise HTTPBadRequest('error')


@view_defaults(route_name='gettii.test', decorator=with_bootstrap, permission='event_editor')
class TestView(_GettiiBaseView):

    @view_config(route_name='gettii.test.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/gettii/test.html')
    def index(self):
        from altair.app.ticketing.core.models import Performance
        performance = Performance.query.get(7278)
        return {'performance': performance,
                }
