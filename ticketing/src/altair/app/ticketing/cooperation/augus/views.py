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
    Performance,
    StockType,
    AugusVenue,
    AugusTicket,
    AugusPerformance,
    )
from altair.augus.protocols import VenueSyncResponse
from altair.augus.exporters import AugusExporter
from altair.augus.types import Status

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

CUSTOMER_ID = 1000001

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

    @view_config(route_name='augus.augus_venue.complete', request_method='GET')
    def complete(self):
        augus_venue = self.context.augus_venue
        res = Response()
        venue_response = VenueSyncResponse(customer_id=CUSTOMER_ID,
                                           venue_code=augus_venue.code)
        res.headers = [('Content-Type', 'application/octet-stream; charset=cp932'),
                       ('Content-Disposition', 'attachment; filename={0}'.format(venue_response.name)),
                       ]
        record = venue_response.record()
        record.venue_code = augus_venue.code
        record.venue_name = augus_venue.name
        record.status = Status.OK.value
        record.venue_version = augus_venue.version
        venue_response.append(record)
        AugusExporter.exportfp(venue_response, res)
        return res


@view_defaults(route_name='augus.events.show', decorator=with_bootstrap, permission='event_editor')
class AugusEventView(_AugusBaseView):
    @view_config(route_name='augus.event.show', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/show.html')
    def show(self):
        return dict(event=self.context.event)

@view_defaults(route_name='augus.performance', decorator=with_bootstrap, permission='event_editor')
class AugusPerformanceView(_AugusBaseView):
    select_prefix = 'performance-'


    @view_config(route_name='augus.performance.index', request_method='GET')
    def index(self):
        return HTTPFound(self.request.route_url('augus.performance.show', event_id=self.context.event.id))

    @view_config(route_name='augus.performance.show', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/performances/show.html')
    def show(self):
        return dict(performance_agperformance=self.context.performance_agperformance,
                    event=self.context.event)

    @view_config(route_name='augus.performance.edit', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/performances/edit.html')
    def edit(self):
        return dict(performance_agperformance=self.context.performance_agperformance,
                    augus_performance_all=self.context.augus_performance_all,
                    select_prefix=self.select_prefix,
                    event=self.context.event)


    @view_config(route_name='augus.performance.save', request_method='POST')
    def save(self):
        for performance_txt, ag_performance_id in self.request.params.iteritems():
            if not performance_txt.startswith(self.select_prefix):
                continue

            performance_id = None
            perforance_txt = performance_txt.strip()
            try:
                performance_id = performance_txt.split('-')[1]
            except IndexError as err:
                raise HTTPBadRequest('Illegal format performance id: {}: {}'.format(repr(performance_txt), repr(err)))

            try:
                performance_id = long(performance_id)
            except (ValueError, TypeError) as err:
                raise HTTPBadRequest('The performance id is invalid: {}: {}'.format(repr(performance_txt), repr(err)))

            performance = Performance.query.filter(Performance.id==performance_id).one()
            ag_performance_id = ag_performance_id.strip()
            if ag_performance_id: # do link
                try:
                    ag_performance_id = long(ag_performance_id)
                except (ValueError, TypeError) as err:
                    raise HTTPBadRequest('The augus performance id is invalid: {}: {}'.format(repr(ag_performance_id), repr(err)))

                ag_performance = AugusPerformance.get(ag_performance_id)
                if not ag_performance:
                    raise HTTPBadRequest('The augus performance not found: {}'.format(ag_performance_id))

                if ag_performance.performance_id != performance.id:
                    ag_performance.performance_id = performance.id;
                    ag_performance.save()
            else: # delete link
                ag_performance = AugusPerformance.get(performance_id=performance.id)
                if ag_performance:
                    ag_performance.performance_id = None
                    ag_performance.save()
        return HTTPFound(self.request.route_url('augus.performance.show', event_id=self.context.event.id))

@view_defaults(route_name='augus.stock_type', decorator=with_bootstrap, permission='event_editor')
class AugusTicketView(_AugusBaseView):
    select_prefix = 'stock_type-'

    @view_config(route_name='augus.stock_type.show', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/stock_types/show.html')
    def show(self):
        stocktypeid_agticket = dict([(ag_ticket.stock_type.id, ag_ticket)
                                     for ag_ticket in self.context.ag_tickets
                                     if ag_ticket.stock_type])
        stocktype_agticket = [(stock_type, stocktypeid_agticket.get(stock_type.id, None))
                              for stock_type in self.context.event.stock_types
                              ]
        return dict(stocktype_agticket=stocktype_agticket,
                    event=self.context.event,
                    select_prefix=self.select_prefix,
                    )


    @view_config(route_name='augus.stock_type.edit', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/stock_types/edit.html')
    def edit(self):
        stocktypeid_agticket = dict([(ag_ticket.stock_type.id, ag_ticket)
                                     for ag_ticket in self.context.ag_tickets
                                     if ag_ticket.stock_type])
        stocktype_agticket = [(stock_type, stocktypeid_agticket.get(stock_type.id, None))
                              for stock_type in self.context.event.stock_types
                              ]

        return dict(stocktype_agticket=stocktype_agticket,
                    event=self.context.event,
                    ag_tickets=self.context.ag_tickets,
                    select_prefix=self.select_prefix,
                    )

    @view_config(route_name='augus.stock_type.save', request_method='POST')
    def save(self):
        try:
            for stock_type_txt, ag_ticket_id in self.request.params.iteritems():
                if not stock_type_txt.startswith(self.select_prefix):
                    continue
                stock_type_id = stock_type_txt.replace(self.select_prefix, '').strip()
                stock_type_id = int(stock_type_id)
                stock_type = StockType.query.filter(StockType.id==stock_type_id).one()

                ag_ticket_id = ag_ticket_id.strip()
                if ag_ticket_id:
                    ag_ticket_id = int(ag_ticket_id)
                    ag_ticket = AugusTicket.query.filter(AugusTicket.id==ag_ticket_id).one()
                    ag_ticket.link_stock_type(stock_type)
                    ag_ticket.save()
                else: # delete link
                    ag_ticket = AugusTicket.query.filter(AugusTicket.stock_type_id==stock_type_id).first()
                    if ag_ticket:
                        ag_ticket.delete_link()
                        ag_ticket.save()

        except ValueError as err:
            raise HTTPBadRequest('invalid save data: {}'.format(repr(err)))
        return HTTPFound(self.request.route_url('augus.stock_type.show', event_id=self.context.event.id))
