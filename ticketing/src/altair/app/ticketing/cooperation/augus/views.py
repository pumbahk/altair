#-*- coding: utf-8 -*-
import csv

from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPFound,
    )
from pyramid.view import (
    view_config,
    view_defaults,
    )
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import (
    AugusVenue,
    )
    
from .forms import (
    AugusVenueUploadForm,
    )
from .csveditor import (
    AugusCSVEditor,
    AugusVenueImporter,
    )
from .utils import SeatAugusSeatPairs
from .errors import (
    NoSeatError,
    EntryFormatError,
    SeatImportError,
    AlreadyExist,
    )

@view_config(route_name='augus.test')
def test(*args, **kwds):
    return ValueError()

class _AugusBaseView(BaseView):
    pass

@view_defaults(route_name='augus.venue', decorator=with_bootstrap, permission='event_editor')
class VenueView(_AugusBaseView):
    @view_config(route_name='augus.venue.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/venues.html')
    def index(self):
        return {'venue': self.context.venue,
                'ag_venues': self.context.augus_venues,
                'upload_form': AugusVenueUploadForm(),
                }

    @view_config(route_name='augus.venue.download', request_method='GET')
    def download(self):
        res = Response()
        filename = 'AUGUS_VENUE_DONWLOAD.csv'
        res.headers = [('Content-Type', 'application/octet-stream; charset=cp932'),
                       ('Content-Disposition', 'attachment; filename={0}'.format(filename)),
                       ]
        writer = csv.writer(res, delimiter=',') 
        csveditor = AugusCSVEditor()
        pairs = SeatAugusSeatPairs()
        pairs.load(self.context.venue)
        try:
            csveditor.write(writer, pairs)
        except (NoSeatError, EntryFormatError, SeatImportError) as err:
            raise HTTPBadRequest(err)
        return res
        
    @view_config(route_name='augus.venue.upload', request_method='POST')                
    def upload(self):
        form = AugusVenueUploadForm(self.request.params)
        if form.validate() and hasattr(form.augus_venue_file.data, 'file'):
            reader = csv.reader(form.augus_venue_file.data.file)
            importer = AugusVenueImporter()
            pairs = SeatAugusSeatPairs()
            pairs.load(self.context.venue)
            try:
                ag_venue = importer.import_(reader, pairs, create_only=True)
                url = self.request.route_path('augus.augus_venue.show',
                                              augus_venue_code=ag_venue.code,
                                              augus_venue_version=ag_venue.version,
                                              )
                return HTTPFound(url)                
            except (NoSeatError, EntryFormatError, SeatImportError, AlreadyExist) as err:
                raise HTTPBadRequest(err)
        else:# validate error
            raise HTTPBadRequest('validation error')

@view_defaults(route_name='augus.augus_venue', decorator=with_bootstrap, permission='event_editor')
class AugusVenueView(_AugusBaseView):
    
    @view_config(route_name='augus.augus_venue.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/augus_venues/index.html')
    def index(self):
        augus_venue_code = self.context.augus_venue_code
        augus_venues = self.context.augus_venues
        return dict(augus_venues=augus_venues,
                    augus_venue_code=augus_venue_code)

    @view_config(route_name='augus.augus_venue.show', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/augus_venues/show.html')
    def show(self):
        return dict(augus_venue=self.context.augus_venue,
                    upload_form=AugusVenueUploadForm(),
                    )

    @view_config(route_name='augus.augus_venue.download', request_method='GET')
    def download(self):
        augus_venue = self.context.augus_venue
        res = Response()
        filename = 'AUGUS_VENUE_DONWLOAD.csv'
        res.headers = [('Content-Type', 'application/octet-stream; charset=cp932'),
                       ('Content-Disposition', 'attachment; filename={0}'.format(filename)),
                       ]
        writer = csv.writer(res, delimiter=',') 
        csveditor = AugusCSVEditor()
        pairs = SeatAugusSeatPairs()
        pairs.load_augus_venue(augus_venue)
        try:
            csveditor.write(writer, pairs)
        except (NoSeatError, EntryFormatError, SeatImportError) as err:
            raise HTTPBadRequest(err)
        return res

    @view_config(route_name='augus.augus_venue.upload', request_method='POST')                
    def upload(self):
        form = AugusVenueUploadForm(self.request.params)
        if form.validate() and hasattr(form.augus_venue_file.data, 'file'):
            reader = csv.reader(form.augus_venue_file.data.file)
            importer = AugusVenueImporter()
            pairs = SeatAugusSeatPairs()
            pairs.load_augus_venue(self.context.augus_venue)
            try:
                importer.import_(reader, pairs)
                url = self.request.route_path('augus.augus_venue.show',
                                              augus_venue_code=self.context.augus_venue_code,
                                              augus_venue_version=self.context.augus_venue_version,
                                              )
                return HTTPFound(url)                
            except (NoSeatError, EntryFormatError, SeatImportError) as err:
                raise HTTPBadRequest(err)
        else:# validate error
            raise HTTPBadRequest('validation error')
