#-*- coding: utf-8 -*-
import csv
import time
import datetime
from sqlalchemy.orm.exc import (
    MultipleResultsFound,
    NoResultFound,
    )
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
    StockHolder,
    Performance,
    StockType,
    AugusVenue,
    AugusTicket,
    AugusPerformance,
    AugusPutback,
    AugusStockInfo,
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
        filename = 'AUGUS_VENUE_DONWLOAD_ALTAIR_{}_{}.csv'.format(self.context.venue.id, time.strftime('%Y%m%d%H%M%S'))
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
        filename = 'AUGUS_VENUE_DONWLOAD_AUGUS_{}_{}.csv'.format(augus_venue.id, time.strftime('%Y%m%d%H%M%S'))
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
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/stock_types/show2.html')
    def show(self):
        return dict(event=self.context.event,
                    stock_types=self.context.event.stock_types,
                    ag_tickets = self.context.ag_tickets,
                    select_prefix=self.select_prefix,
                    )

        # stocktypeid_agticket = dict([(ag_ticket.stock_type.id, ag_ticket)
        #                              for ag_ticket in self.context.ag_tickets
        #                              if ag_ticket.stock_type])
        # stocktype_agticket = [(stock_type, stocktypeid_agticket.get(stock_type.id, None))
        #                       for stock_type in self.context.event.stock_types
        #                       ]
        # return dict(stocktype_agticket=stocktype_agticket,
        #             event=self.context.event,
        #             select_prefix=self.select_prefix,
        #             )


    @view_config(route_name='augus.stock_type.edit', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/stock_types/edit2.html')
    def edit(self):
        # stocktypeid_agticket = dict([(ag_ticket.stock_type.id, ag_ticket)
        #                              for ag_ticket in self.context.ag_tickets
        #                              if ag_ticket.stock_type])
        # stocktype_agticket = [(stock_type, stocktypeid_agticket.get(stock_type.id, None))
        #                       for stock_type in self.context.event.stock_types
        #                       ]

        return dict(event=self.context.event,
                    stock_types=self.context.event.stock_types,
                    ag_tickets = self.context.ag_tickets,
                    select_prefix=self.select_prefix,
                    )

    @view_config(route_name='augus.stock_type.save', request_method='POST')
    def save(self):
        try:
            for ag_ticket_txt, stock_type_id in self.request.params.iteritems():
                if not ag_ticket_txt.startswith(self.select_prefix):
                    continue

                ag_ticket_id = int(ag_ticket_txt.replace(self.select_prefix, '').strip())
                stock_type_id = int(stock_type_id)
                stock_type = StockType.query.filter(StockType.id==stock_type_id).one()

                if ag_ticket_id:
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

@view_defaults(route_name='augus.putback', decorator=with_bootstrap, permission='event_editor')
class AugusPutbackView(_AugusBaseView):

    @view_config(route_name='augus.putback.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/putback/index.html')
    def index(self):
        putback_codes = set([putback.augus_putback_code for putback in AugusPutback.query.all()])
        return dict(event_id=self.context.event.id,
                    putback_codes=putback_codes,
                    )


    @view_config(route_name='augus.putback.new', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/putback/new.html')
    def new_get(self):
        stock_holders = filter(lambda stock_holder: stock_holder.is_putback_target, self.context.event.stock_holders)
        return dict(event_id=self.context.event.id,
                    performances=self.context.event.performances,
                    stock_holders=stock_holders,
                    )

    @view_config(route_name='augus.putback.new', request_method='POST')
    def new_post(self):
        # get new putback code
        putback_code = 1
        last_putback = AugusPutback.query.order_by(AugusPutback.augus_putback_code.desc()).first()
        if last_putback:
            putback_code = last_putback.augus_putback_code

        stock_holder_id = int(self.request.params.get('stock_holder'))
        performance_ids = map(int, self.request.params.getall('performance'))
        stock_holder = StockHolder.query.filter(StockHolder.id==stock_holder_id).one()
        if not stock_holder.is_putback_target:
            raise HTTPBadRequest(u'This stock holder is not putback target: {}'.format(stock_holder.id))

        performances = Performance.query.filter(Performance.id.in_(performance_ids)).all()
        if len(performance_ids) != len(performances):
            raise HTTPBadRequest(u'Unmatch performance count: len(performance_ids={} != len(performance)={}'.format(
                len(performance_ids), len(performances)))

        # 対象のseatを探す
        seats = [seat
                 for performance in performances
                 for stock in performance.stocks
                 if stock.stock_holder_id == stock_holder.id
                 for seat in stock.seats
                 ]
        if 0 == len(seats):
            raise HTTPBadRequest(u'not seat')

        now = datetime.datetime.now()
        seat = None
        try:
            for seat in seats:
                # 連携/配券できていないもが含まれていた場合エラーする
                ag_stock_info = AugusStockInfo.query.filter(AugusStockInfo.seat_id==seat.id).one()
                already = AugusPutback.query.filter(AugusPutback.augus_stock_info_id==ag_stock_info.id).all()
                if already:
                    codes = set([putback.augus_putback_code for putback in already])
                    raise HTTPBadRequest(u'augus stock info already putbacked: augus putback codes={}'.format(codes))
                ag_putback = AugusPutback()
                ag_putback.augus_putback_code = putback_code
                ag_putback.quantity = ag_stock_info.quantity # 席指定のみのためすべて(1)返しても良い/ 自由席の場合はここが問題になる
                ag_putback.augus_stock_info_id = ag_stock_info.id
                ag_putback.seat_id = seat.id
                ag_putback.save()
        except (MultipleResultsFound, NoResultFound) as err:
            seat_id = seat.id if seat else None
            raise HTTPBadRequest(u'cannot putback: seat.id={}: {}'.format(seat_id, repr(err)))
        return HTTPFound(self.request.route_url('augus.putback.show', event_id=self.context.event.id, putback_code=putback_code))

    @view_config(route_name='augus.putback.show', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/putback/show.html')
    def show(self):
        putback_code = int(self.request.matchdict['putback_code'])
        putbacks = AugusPutback.query.filter(AugusPutback.augus_putback_code==putback_code).all()
        if 0 == len(putbacks):
            raise HTTPBadRequest(u'putback not found')
        return dict(event_id=self.context.event.id,
                    putbacks=putbacks,
                    putback_code=putback_code,
                    )

    @view_config(route_name='augus.putback.reserve', request_method='POST')
    def reserve(self):
        now = datetime.datetime.now()
        putback_code = int(self.request.matchdict['putback_code'])
        putbacks = AugusPutback.query.filter(AugusPutback.augus_putback_code==putback_code)
        for putback in putbacks:
            if putback.reserved_at: # 既に返券予約済みのものが含まれていた場合エラーにする
                raise HTTPBadRequest(u'already putback: putback_code={} putback.id={}'.format(
                    putback.augus_putback_code, putback.id))
            putback.reserved_at = now
            putback.save()
        return HTTPFound(self.request.route_url('augus.putback.show', event_id=self.context.event.id, putback_code=putback_code))
