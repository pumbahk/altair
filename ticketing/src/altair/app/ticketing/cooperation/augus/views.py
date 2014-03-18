#-*- coding: utf-8 -*-
import csv
import time
import logging
import datetime
import itertools
import transaction
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
    SeatStatusEnum,
    Product,
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
from .exporters import AugusAchievementExporter
from .utils import SeatAugusSeatPairs
from .errors import (
    NoSeatError,
    EntryFormatError,
    SeatImportError,
    AlreadyExist,
    )
from .importers import get_enable_stock_info

logger = logging.getLogger(__name__)

@view_config(route_name='augus.test', permission='event_editor')
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


    @view_config(route_name='augus.performance.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/performances/index.html')
    def index(self):
        return dict(augus_performances=self.context.augus_performance_all,
                    event=self.context.event,
                    )

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
        error_url = self.request.route_path('augus.performance.edit', event_id=self.context.event.id)
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

                # AugusVenue.idとPerformance.venue.original_venue_idが違うものは連携できないようにする
                ag_venue = ag_performance.get_augus_venue()
                if not ag_venue:
                    self.request.session.flash(u'オーガス会場がありません: AugusPerformance.id={}, (augus_venue_code={}, augus_venue_version~{})'.format(
                        ag_performance.id, ag_performance.augus_venue_code, ag_performance.augus_venue_version))
                    transaction.abort()
                    raise HTTPFound(error_url)
                elif ag_venue.venue.site_id != performance.venue.site_id:
                    self.request.session.flash(u'会場の連携情報が不一致です: Performance.id={} AugusPerformance.id={}'.format(
                        performance.id, ag_performance.id))
                    transaction.abort()
                    raise HTTPFound(error_url)

                if ag_performance.performance_id != performance.id:
                    ag_performance.performance_id = performance.id
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

    @view_config(route_name='augus.stock_type.edit', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/stock_types/edit2.html')
    def edit(self):
        return dict(event=self.context.event,
                    stock_types=self.context.event.stock_types,
                    ag_tickets = self.context.ag_tickets,
                    select_prefix=self.select_prefix,
                    )

    @view_config(route_name='augus.stock_type.save', request_method='POST')
    def save(self):
        url = self.request.route_path('augus.product.show', event_id=self.context.event.id)
        try:
            for ag_ticket_txt, stock_type_id in self.request.params.iteritems():
                if not ag_ticket_txt.startswith(self.select_prefix):
                    continue

                ag_ticket_id = int(ag_ticket_txt.replace(self.select_prefix, '').strip())
                ag_ticket = AugusTicket.query.filter(AugusTicket.id==ag_ticket_id).one()
                if stock_type_id:
                    stock_type_id = int(stock_type_id)
                    stock_type = StockType.query.filter(StockType.id==stock_type_id).one()
                    ag_ticket.link_stock_type(stock_type)
                    ag_ticket.save()
                else: # delete link
                    ag_ticket.stock_type_id = None
                    ag_ticket.save()
        except ValueError as err:
            raise HTTPBadRequest('invalid save data: {}'.format(repr(err)))
        return HTTPFound(self.request.route_url('augus.stock_type.show', event_id=self.context.event.id))


@view_defaults(route_name='augus.product', decorator=with_bootstrap, permission='event_editor')
class ProductView(_AugusBaseView):
    select_prefix = 'product-'

    @view_config(route_name='augus.product.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/products/index.html')
    def index(self):
        url = self.request.route_path('augus.product.show', event_id=self.context.event.id)

        return HTTPFound(url)

    @view_config(route_name='augus.product.show', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/products/show.html')
    def show(self):
        performance_ids = [performance.id for performance in self.context.event.performances]
        augus_performances = AugusPerformance.query.filter(AugusPerformance.performance_id.in_(performance_ids)).all()
        return dict(event=self.context.event,
                    augus_performances=augus_performances,
                    select_prefix=self.select_prefix,
                    )

    @view_config(route_name='augus.product.edit', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/products/edit.html')
    def edit(self):
        performance_ids = [performance.id for performance in self.context.event.performances]
        augus_performances = AugusPerformance.query.filter(AugusPerformance.performance_id.in_(performance_ids)).all()
        return dict(event=self.context.event,
                    augus_performances=augus_performances,
                    select_prefix=self.select_prefix,
                    )

    @view_config(route_name='augus.product.save', request_method='POST')
    def save(self):
        url = self.request.route_path('augus.product.show', event_id=self.context.event.id)
        error_url = self.request.route_path('augus.product.edit', event_id=self.context.event.id)

        try:
            for product_txt, augus_ticket_id in self.request.params.iteritems():
                if not product_txt.startswith(self.select_prefix):
                    continue

                product_id = int(product_txt.replace(self.select_prefix, '').strip())
                product = Product.query.filter(Product.id==product_id).one()
                if augus_ticket_id:
                    augus_ticket_id = int(augus_ticket_id)
                    augus_ticket = AugusTicket.query.filter(AugusTicket.id==augus_ticket_id).one()
                    if product.seat_stock_type_id != augus_ticket.stock_type_id:
                        self.request.session.flash(u'席種が不一致です: Product.id={}, AugusTicket.id={}'.format(
                            product.id, augus_ticket_id))
                        transaction.abort()
                        raise HTTPFound(error_url)
                    product.augus_ticket_id = augus_ticket.id
                    product.save()
                else: # delete link
                    product.augus_ticket_id = None
                    product.save()
        except ValueError as err:
            raise HTTPBadRequest('invalid save data: {}'.format(repr(err)))
        return HTTPFound(url)

@view_defaults(route_name='augus.putback', decorator=with_bootstrap, permission='event_editor')
class AugusPutbackView(_AugusBaseView):

    @view_config(route_name='augus.putback.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/putback/index.html')
    def index(self):
        putbacks = AugusPutback.query.all()
        return dict(event=self.context.event,
                    putbacks=putbacks,
                    )


    @view_config(route_name='augus.putback.new', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/putback/new.html')
    def new_get(self):
        stock_holders = filter(lambda stock_holder: stock_holder.is_putback_target, self.context.event.stock_holders)
        return dict(event=self.context.event,
                    performances=self.context.event.performances,
                    stock_holders=stock_holders,
                    )


    @view_config(route_name='augus.putback.confirm', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/putback/confirm.html')
    def confirm(self):
        stock_holder_id = int(self.request.params.get('stock_holder'))
        performance_ids = map(int, self.request.params.getall('performance'))

        error_url = self.request.route_url('augus.putback.new', event_id=self.context.event.id)

        stock_holder = StockHolder.query.filter(StockHolder.id==stock_holder_id).one()
        if not stock_holder.is_putback_target:
            self.request.session.flash(u'この枠は返券できません(返券する為には外部返券利用をONにしてください): StockHolder.id={}'.format(stock_holder.id))
            raise HTTPFound(error_url)

        now = datetime.datetime.now()
        augus_stock_infos = []
        for performance_id in performance_ids:
            ag_performance = AugusPerformance.query.filter(AugusPerformance.performance_id==performance_id).first()
            if not ag_performance or not ag_performance.performance_id:
                self.request.session.flash(u'連携していないもしくは不正な公演が指定されました: Performance.id={}'.format(performance_id) )
                raise HTTPFound(error_url)

            seats = [seat
                     for stock in stock_holder.stocks
                     if stock.performance_id == performance_id
                     for seat in stock.seats
                     ]

            if 0 == len(seats):
                self.request.session.flash(u'対象になる座席がありません: Performance.id={}'.format(performance_id) )
                return HTTPFound(error_url)

            try:
                for seat in seats:
                    # 連携/配券できていないもが含まれていた場合エラーする
                    #ag_stock_info = AugusStockInfo.query.filter(AugusStockInfo.seat_id==seat.id).all()
                    ag_stock_info = get_enable_stock_info(seat)
                    if not ag_stock_info:
                        self.request.session.flash(u'配券がされていない座席は返券できません。もし席があるのであれば返券予約済みかもしれません: Seat.id={}'.format(seat.id))
                        raise HTTPFound(error_url)
                    augus_stock_infos.append(ag_stock_info)
            except (MultipleResultsFound, NoResultFound) as err:
                seat_id = seat.id if seat else None
                self.request.session.flash(u'返券できない座席がありました: Seat.id={}'.format(seat_id))
                raise  HTTPFound(error_url)
        self.request.session.flash(u'次の追券情報を使って返券を実行します。よろしければ確定を押してください')
        return dict(event=self.context.event,
                    augus_stock_infos=augus_stock_infos,
                    )


    @view_config(route_name='augus.putback.new', request_method='POST')
    def new_post(self):
        stock_holder_id = int(self.request.params.get('stock_holder'))
        performance_ids = map(int, self.request.params.getall('performance'))

        success_url = self.request.route_url('augus.putback.index', event_id=self.context.event.id)
        error_url = self.request.route_url('augus.putback.new', event_id=self.context.event.id)

        stock_holder = StockHolder.query.filter(StockHolder.id==stock_holder_id).one()
        if not stock_holder.is_putback_target:
            self.request.session.flash(u'この枠は返券できません(返券する為には外部返券利用をONにしてください): StockHolder.id={}'.format(stock_holder.id))
            return HTTPFound(error_url)

        putback_codes = []
        now = datetime.datetime.now()
        for performance_id in performance_ids:
            ag_performance = AugusPerformance.query.filter(AugusPerformance.performance_id==performance_id).first()
            if not ag_performance or not ag_performance.performance_id:
                self.request.session.flash(u'連携していないもしくは不正な公演が指定されました: Performance.id={}'.format(performance_id) )
                transaction.abort()
                return HTTPFound(error_url)

            seats = [seat
                     for stock in stock_holder.stocks
                     if stock.performance_id == performance_id
                     for seat in stock.seats
                     ]

            if 0 == len(seats):
                self.request.session.flash(u'対象になる座席がありません: Performance.id={}'.format(performance_id) )
                transaction.abort()
                return HTTPFound(error_url)

            # get new putback code
            putback_code = 1
            last_putback = AugusPutback.query.order_by(AugusPutback.augus_putback_code.desc()).first()
            if last_putback:
                putback_code = last_putback.augus_putback_code + 1

            try:
                for seat in seats:
                    # 連携/配券できていないもが含まれていた場合エラーする
                    #ag_stock_info = AugusStockInfo.query.filter(AugusStockInfo.seat_id==seat.id).all()
                    ag_stock_info = get_enable_stock_info(seat)
                    if not ag_stock_info:
                        self.request.session.flash(u'配券がされていない座席は返券できません。もし席があるのであれば返券予約済みかもしれません: Seat.id={}'.format(seat.id))
                        transaction.abort()
                        return HTTPFound(error_url)

                    ag_putback = AugusPutback()
                    ag_putback.augus_putback_code = putback_code
                    ag_putback.quantity = ag_stock_info.quantity # 席指定のみのためすべて(1)返しても良い/ 自由席の場合はここが問題になる
                    ag_putback.augus_stock_info_id = ag_stock_info.id
                    ag_putback.seat_id = seat.id
                    ag_putback.save()

                    ag_stock_info.putbacked_at = now
                    ag_stock_info.save()
                    putback_codes.append(putback_code)
            except (MultipleResultsFound, NoResultFound) as err:
                seat_id = seat.id if seat else None
                self.request.session.flash(u'返券できない座席がありました: Seat.id={}'.format(seat_id))
                transaction.abort()
                return HTTPFound(error_url)
        self.request.session.flash(u'次の返券コードで返券データを作成しました。実際に返券するには確定をしてください。: {}'.format(putback_codes))
        return HTTPFound(success_url)

    @view_config(route_name='augus.putback.show', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/putback/show.html')
    def show(self):
        putback_code = int(self.request.matchdict['putback_code'])
        putback = AugusPutback.query.filter(AugusPutback.augus_putback_code==putback_code).first()
        if not putback:
            self.request.session.flash(u'返券データがありません: augus_putback_code={}'.format(putback_code))
            return HTTPFound(self.request.route_path('augus.putback.index', event_id=self.context.event.id))
        return dict(event=self.context.event,
                    putback=putback,
                    putback_code=putback_code,
                    )
    def get_putback_code(self):
        putback_code = 1
        last_putback = AugusPutback.query.order_by(AugusPutback.augus_putback_code.desc()).first()
        if last_putback:
            putback_code = last_putback.augus_putback_code + 1
        return putback_code

    @view_config(route_name='augus.putback.reserve', request_method='POST')
    def reserve(self):
        url = self.request.route_path('augus.putback.index', event_id=self.context.event.id)
        augus_stock_info_ids = map(int, self.request.params.getall('augus_stock_info_id'))
        augus_stock_infos = AugusStockInfo.query.filter(
            AugusStockInfo.id.in_(augus_stock_info_ids)).all()

        can_putback = lambda seat: seat.status in [SeatStatusEnum.NotOnSale.v, SeatStatusEnum.Vacant.v, SeatStatusEnum.Canceled.v]

        cannot_putback_info_ids = [str(augus_stock_info.id) for augus_stock_info in augus_stock_infos if not can_putback(augus_stock_info.seat)]
        if cannot_putback_info_ids:
            self.request.session.flash(u'返券できない座席があるため返券できません')
            self.request.session.flash(u'AugusStockInfo.id: {}'.format(u''.join(cannot_putback_infos)))
            raise  HTTPFound(error_url)

        now = datetime.datetime.now()
        # Performanceごとにputbackを作成
        for augus_performance, asis in itertools.groupby(augus_stock_infos, key=lambda asi: asi.augus_performance):
            putback = AugusPutback()
            putback.reserved_at = now
            putback.augus_putback_code = self.get_putback_code()
            putback.augus_performance_id = augus_performance.id
            putback.save()

            for augus_stock_info in asis:
                for augus_stock_detail in augus_stock_info.augus_stock_details:
                    augus_stock_detail.augus_putback_id = putback.id
                    augus_stock_detail.save()
            self.request.session.flash(u'返券予約しました: AugusPerformance.id={}'.format(augus_performance.id))
        return HTTPFound(url)

@view_defaults(route_name='augus.achievement', decorator=with_bootstrap, permission='event_editor')
class AugusAchievementView(_AugusBaseView):
    @view_config(route_name='augus.achievement.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/achievement/index.html')
    def index(self):
        performance_ids = [performance.id for performance in self.context.event.performances]
        augus_performances = AugusPerformance.query.filter(AugusPerformance.performance_id.in_(performance_ids)).all()
        return dict(event=self.context.event,
                    augus_performances=augus_performances,
                    )

    @view_config(route_name='augus.achievement.get', request_method='GET')
    def achievement_get(self):
        augus_performance_id = int(self.request.matchdict.get('augus_performance_id'))
        augus_performance = AugusPerformance.query.filter(AugusPerformance.id==augus_performance_id).first()
        if not augus_performance:
            self.request.session.flash(u'連携していません')
            url = self.request.route_path('augus.achievement.index', event_id=self.context.event.id)
            return HTTPFound(url)
        res = Response()
        exporter = AugusAchievementExporter()
        res_proto = exporter.export_from_augus_performance(augus_performance)
        res_proto.event_code = augus_performance.augus_event_code
        res_proto.customer_id = CUSTOMER_ID
        AugusExporter.exportfp(res_proto, res)
        res.headers = [('Content-Type', 'application/octet-stream; charset=cp932'),
                       ('Content-Disposition', 'attachment; filename={0}'.format(res_proto.name)),
                       ]
        return res


    @view_config(route_name='augus.achievement.reserve', request_method='GET')
    def achievement_reserve(self):
        augus_performance_id = int(self.request.matchdict.get('augus_performance_id'))
        #performance_ids = [performance.id for performance in self.context.event.performances]
        augus_performance = AugusPerformance.query.filter(AugusPerformance.id==augus_performance_id).one()
        augus_performance.is_report_target = True
        augus_performance.save()
        self.request.session.flash(u'販売実績戻しを予約しました')
        url = self.request.route_path('augus.achievement.index', event_id=self.context.event.id)
        return HTTPFound(url)
