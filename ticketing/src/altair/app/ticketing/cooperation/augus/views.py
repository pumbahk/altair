#-*- coding: utf-8 -*-
import csv
import time
import json
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
    AugusAccount,
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
                'upload_form': AugusVenueUploadForm(organization_id=self.context.organization.id),
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

    #@view_config(route_name='augus.venue.upload', request_method='POST')
    def _upload(self):
        form = AugusVenueUploadForm(self.request.params, organization_id=self.context.organization.id)
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

    @view_config(route_name='augus.venue.upload', request_method='POST')
    def upload(self):
        import csv
        from altair.app.ticketing.core.models import Venue, AugusSeat

        if not self.context.augus_account:
            raise HTTPBadRequest('augus account not found')

        venue_id = int(self.request.matchdict['venue_id'])
        try:
            fp = self.request.POST['augus_venue_file'].file
        except AttributeError as err:
            raise HTTPBadRequest('no file')
        else:
            logger.info('AUGUS VENUE: start creating augus venue')

            logger.info('AUGUS VENUE: parse csv')
            reader = csv.reader(fp)
            headers = reader.next()
            records = [record for record in reader]
            logger.info('AUGUS VENUE: creating target list')
            external_venue_code_name_version_list = filter(lambda code_version: code_version != ("", "", ""),
                                                           set([(record[6], record[7], record[23]) for record in records]))
            count = len(external_venue_code_name_version_list)
            if count == 0: # 対象すべてunlink
                raise HTTPBadRequest(body=json.dumps({
                    'message':u'連携を変更したい場合は外部会場ページを使用してください',
                }))
            elif count == 1:# 通常処理
                logger.info('AUGUS VENUE: search augus venues')
                ex_venue_code, ex_venue_name, ex_venue_version = external_venue_code_name_version_list[0]
                ex_venue_code = int(ex_venue_code)
                ex_venue_name = ex_venue_name.decode('cp932')
                ex_venue_verson = int(ex_venue_version)
                ex_venues = AugusVenue.query.filter(AugusVenue.code==ex_venue_code)\
                                            .filter(AugusVenue.version==ex_venue_version)\
                                            .all()

                if ex_venues:
                    raise HTTPBadRequest(body=json.dumps({
                        'message':u'この会場は既に登録されています',
                    }))

                logger.info('AUGUS VENUE: creating augus venues')
                venue = Venue.query.filter(Venue.id==venue_id).one()

                ex_venue = AugusVenue()
                ex_venue.code = ex_venue_code
                ex_venue.name = ex_venue_name
                ex_venue.version = ex_venue_version
                ex_venue.venue_id = venue.id
                ex_venue.augus_account_id = self.context.augus_account.id
                ex_venue.save()

                logger.info('AUGUS VENUE: creating augus seat target dict')
                seat_id__record = dict([(int(record[0]), record) for record in records if record[6].strip()])
                seat_ids = seat_id__record.keys()
                logger.info('AUGUS VENUE: creating target seat list')
                seats = filter(lambda seat: seat.id in seat_ids, venue.seats)

                def _create_ex_seat(seat):
                    record = seat_id__record[seat.id]
                    _str = lambda _col: _col.decode('cp932')
                    _int = lambda _col: int(_col) if _col.strip() else None
                    if record[6]: # create
                        ex_seat = AugusSeat()
                        ex_seat.area_name = _str(record[8])
                        ex_seat.info_name = _str(record[9])
                        ex_seat.doorway_name = _str(record[10])
                        ex_seat.priority = _int(record[11])
                        ex_seat.floor = _str(record[12])
                        ex_seat.column = _str(record[13])
                        ex_seat.num = _str(record[14])
                        ex_seat.block = _int(record[15])
                        ex_seat.coordy = _int(record[16])
                        ex_seat.coordx = _int(record[17])
                        ex_seat.coordy_whole = _int(record[18])
                        ex_seat.coordx_whole = _int(record[19])
                        ex_seat.area_code = _int(record[20])
                        ex_seat.info_code = _int(record[21])
                        ex_seat.doorway_code = _int(record[22])
                        ex_seat.version = _int(record[23])
                        # link
                        ex_seat.augus_venue_id = ex_venue.id
                        ex_seat.seat_id = seat.id
                        return ex_seat
                    else:
                        assert False, repr(record)
                logger.info('AUGUS VENUE: creating augus seats')
                ex_seats = map(_create_ex_seat, seats)
                logger.info('AUGUS VENUE: saving augus seats')
                for ex_seat in ex_seats:
                    ex_seat.save()
                logger.info('AUGUS VENUE: finished')

                url = self.request.route_path('augus.augus_venue.show',
                                              augus_venue_code=ex_venue.code,
                                              augus_venue_version=ex_venue.version,
                                              )
                return HTTPFound(url)
            else:
                raise HTTPBadRequest(body=json.dumps({
                    'message':u'複数の会場コードは受け付けられません',
                }))

CUSTOMER_ID = 1000001

@view_defaults(route_name='augus.augus_venue', decorator=with_bootstrap, permission='event_editor')
class AugusVenueView(_AugusBaseView):

    @view_config(route_name='augus.augus_venue.list', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/augus_venues/list.html')
    def list_(self):
        augus_venues = AugusVenue.query.all()
        return dict(augus_venues=augus_venues)

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
                    upload_form=AugusVenueUploadForm(organization_id=self.context.organization.id),
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
        form = AugusVenueUploadForm(self.request.params, organization_id=self.context.organization.id)
        if not (form.validate() and hasattr(form.augus_venue_file.data, 'file')):
            raise HTTPBadRequest('validation error')

        import csv
        from altair.app.ticketing.core.models import Venue, AugusSeat

        if not self.context.augus_account:
            raise HTTPBadRequest('augus account not found')

        try:
            fp = self.request.POST['augus_venue_file'].file
        except AttributeError as err:
            raise HTTPBadRequest('no file')
        else:
            updates = set()

            logger.info('AUGUS VENUE: start creating augus venue')
            ex_venue = self.context.augus_venue
            ex_venue.augus_account_id = self.context.augus_account.id
            venue = ex_venue.venue
            venue_id = venue.id



            logger.info('AUGUS VENUE: load augus venue')
            # pairs = SeatAugusSeatPairs()
            # pairs.load_augus_venue(ex_venue)
            # pairs = [pair for pair in pairs]
            logger.info('AUGUS VENUE: parse csv')
            reader = csv.reader(fp)
            headers = reader.next()
            records = [record for record in reader]
            logger.info('AUGUS VENUE: creating target list')
            external_venue_code_name_version_list = filter(lambda code_name_version: code_name_version != ("", "", ""),
                                                           set([(record[6], record[7], record[23]) for record in records]))
            count = len(external_venue_code_name_version_list)

            # 変更がないrecordは除外
            logger.info('AUGUS VENUE: creating augus seat name dict')
            seat_id__ex_seat = dict([(ex_seat.seat_id, ex_seat) for ex_seat in ex_venue.augus_seats if ex_seat.seat_id])
            _str = lambda _col: _col.decode('cp932')
            _int = lambda _col: int(_col) if _col.strip() else None

            def _is_modified(record):
                seat_id = int(record[0])
                ex_seat = seat_id__ex_seat.get(seat_id, None)
                if not ex_seat:
                    word = list(set(map(lambda _ss: _ss.strip(), record[6:])))[0]
                    if word != '':
                        return True
                    else:
                        return False
                else:
                    status = ex_seat.augus_venue.code == _int(record[6])\
                        and ex_seat.area_name == _str(record[8])\
                        and ex_seat.info_name == _str(record[9]) \
                        and ex_seat.doorway_name == _str(record[10])\
                        and ex_seat.priority == _int(record[11])\
                        and ex_seat.floor == _str(record[12])\
                        and ex_seat.column == _str(record[13])\
                        and ex_seat.num == _str(record[14])\
                        and ex_seat.block == _int(record[15])\
                        and ex_seat.coordy == _int(record[16])\
                        and ex_seat.coordx == _int(record[17])\
                        and ex_seat.coordy_whole == _int(record[18])\
                        and ex_seat.coordx_whole == _int(record[19])\
                        and ex_seat.area_code == _int(record[20])\
                        and ex_seat.info_code == _int(record[21])\
                        and ex_seat.doorway_code == _int(record[22])\
                        and ex_seat.version == _int(record[23])\
                        and ex_seat.seat_id == seat_id

                    return not status
            logger.info('AUGUS VENUE: filtering modify records')
            length = len(records)
            records = filter(_is_modified, records)
            logger.info('AUGUS VENUE: filtered by modify records: {} -> {}'.format(length, len(records)))

            logger.info('AUGUS VENUE: create name ex_seat dict')
            name__ex_seat = dict([((ex_seat.floor, ex_seat.column, ex_seat.num, ex_seat.area_code, ex_seat.info_code), ex_seat)
                                  for ex_seat in ex_venue.augus_seats])
            _name = lambda _record: (_str(_record[12]), _str(_record[13]), _str(_record[14]), int(_record[20]), int(_record[21]))

            # とりあえずtargetとなるseatのlinkは削除しておく
            logger.info('AUGUS VENUE: creating seat id list')
            seat_ids = [int(record[0]) for record in records]

            logger.info('AUGUS VENUE: deleting all link')
            for ex_seat in ex_venue.augus_seats:
                if ex_seat.seat_id in seat_ids:
                    ex_seat.seat_id = None
                    updates.add(ex_seat)
            logger.info('AUGUS VENUE: saving augus seats by delete link: record count={}'.format(len(records)))
            for ex_seat in updates:
                logger.info('AUGUS VENUE: save AugusSeat.id={}'.format(ex_seat.id))
                ex_seat.save()


            updates = set()
            logger.info('AUGUS VENUE: filtering')
            try:
                records = [record for record in records if record[6] and (record[12], record[13], record[14]) != (u'', u'', u'')]
            except IndexError:
                raise ValueError(repr(record))

            if count == 1:# 通常処理
                if ex_venue.name != external_venue_code_name_version_list[0][1]:
                    try:
                        ex_venue.name = _str(external_venue_code_name_version_list[0][1])
                    except UnicodeDecodeError as err:
                        raise HTTPBadRequest(body=json.dumps({
                            'message':u'会場名に使用できない文字が入っています: {}'.format(repr(external_venue_code_name_version_list[0][1])),
                        }))
                ex_venue.reserved_at = None

                logger.info('AUGUS VENUE: creating augus seat target dict')
                seat_id__seat = dict([(seat.id, seat) for seat in venue.seats if seat.id in seat_ids])

                logger.info('AUGUS VENUE: update augus seats: length={}'.format(len(records)))
                for record in records:
                    if int(record[6]) != ex_venue.code or int(record[23]) != ex_venue.version:
                        raise HTTPBadRequest(body=json.dumps({
                                    'message':u'会場コード、会場バージョンが異なっています: {}'.format(record),
                                    }))

                    name = _name(record) #(_str(record[12]), _str(record[13]), _str(record[14]), int(record[20]), int(record[21]))
                    seat = seat_id__seat[int(record[0])]
                    ex_seat = name__ex_seat.get(name, None)
                    if not ex_seat:
                        ex_seat = AugusSeat()
                        ex_seat.augus_venue_id = ex_venue.id

                    # update external seat
                    ex_seat.area_name = _str(record[8])
                    ex_seat.info_name = _str(record[9])
                    ex_seat.doorway_name = _str(record[10])
                    ex_seat.priority = _int(record[11])
                    ex_seat.floor = _str(record[12])
                    ex_seat.column = _str(record[13])
                    ex_seat.num = _str(record[14])
                    ex_seat.block = _int(record[15])
                    ex_seat.coordy = _int(record[16])
                    ex_seat.coordx = _int(record[17])
                    ex_seat.coordy_whole = _int(record[18])
                    ex_seat.coordx_whole = _int(record[19])
                    ex_seat.area_code = _int(record[20])
                    ex_seat.info_code = _int(record[21])
                    ex_seat.doorway_code = _int(record[22])
                    ex_seat.version = _int(record[23])
                    # link
                    ex_seat.seat_id = seat.id
                    updates.add(ex_seat)
            elif count == 0:
                raise HTTPBadRequest(body=json.dumps({
                    'message':u'レコードがありません',
                }))
            else:
                raise HTTPBadRequest(body=json.dumps({
                    'message':u'複数の会場コードは受け付けられません: {}'.format(repr(external_venue_code_name_version_list)),
                }))

            logger.info('AUGUS VENUE: saving augus seats')
            for ex_seat in updates:
                ex_seat.save()
            ex_venue.save()
            logger.info('AUGUS VENUE: finished update augus seats')
            url = self.request.route_path('augus.augus_venue.show',
                                          augus_venue_code=ex_venue.code,
                                          augus_venue_version=ex_venue.version,
                                          )
            self.request.session.flash(u'オーガス用会場データを更新しました')
            return HTTPFound(url)


    @view_config(route_name='augus.augus_venue.complete_download', request_method='GET')
    def complete_download(self):
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

    @view_config(route_name='augus.augus_venue.complete', request_method='GET')
    def complete(self):
        augus_venue = self.context.augus_venue
        augus_venue.reserved_at = datetime.datetime.now()
        augus_venue.save()
        self.request.session.flash(u'オーガス会場の連携完了通知を予約しました')
        url = self.request.route_path('augus.augus_venue.show',
                                      augus_venue_code=self.context.augus_venue_code,
                                      augus_venue_version=self.context.augus_venue_version,
        )
        return HTTPFound(url)


@view_defaults(route_name='augus.events', decorator=with_bootstrap, permission='event_editor')
class AugusEventView(_AugusBaseView):

    @view_config(route_name='augus.events.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/events/index.html')
    def index(self):
        res = {
            'augus_performances': [],
            }
        if self.request.context.organization.setting.augus_use:
            augus_performances = AugusPerformance.query.all() # WA: refs #8818 対応したら修正が必要
            res['augus_performances'] = augus_performances
        return res

    @view_config(route_name='augus.events.show', request_method='GET',
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
