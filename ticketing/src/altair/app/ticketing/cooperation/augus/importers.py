#-*- coding: utf-8 -*-
import time
import datetime
import itertools
import logging
from sqlalchemy import (
    tuple_,
)
from sqlalchemy.orm.exc import (
    MultipleResultsFound,
    NoResultFound,
    )
from sqlalchemy.orm import contains_eager
from pyramid.threadlocal import get_current_request
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import (
    Seat,
    SeatStatus,
    Venue,
    Event,
    Performance,
    Stock,
    StockHolder,
    StockStatus,
    AugusAccount,
    AugusPerformance,
    AugusVenue,
    AugusTicket,
    AugusSeat,
    AugusPutback,
    AugusStockInfo,
    AugusStockDetail,
    SeatStatusEnum,
    AugusPutbackStatus,
    )
from altair.augus.types import (
    SeatTypeClassif,
)
from .errors import (
    AugusIntegrityError,
    AugusDataImportError,
    NoSeatError,
    IllegalImportDataError,
    AugusPerformanceNotFound,
    )

logger = logging.getLogger(__name__)

def get_or_create_augus_stock_info(seat):
    try:
        return AugusStockInfo\
          .query\
          .filter(AugusStockInfo.seat_id==seat.id)\
          .one()
    except NoResultFound as err:
        return AugusStockInfo()

def get_augus_stock_detail(augus_stock_info, record):
    return AugusStockDetail.query.filter(AugusStockDetail.augus_stock_info_id==augus_stock_info.id)\
                                 .filter(AugusStockDetail.augus_seat_type_code==record.seat_type_code)\
                                 .filter(AugusStockDetail.augus_unit_value_code==record.unit_value_code)\
                                 .filter(AugusStockDetail.augus_putback_id==None)\
                                 .first()

def get_enable_stock_info(seat):
    stock_infos = AugusStockInfo.query.filter(AugusStockInfo.seat_id==seat.id).all()
    enables = []
    for info in stock_infos:
        for detail in info.augus_stock_details:
            if not detail.augus_putback_id:
                return info

class AugusPerformanceImpoter(object):
    def import_record(self, record, augus_account):
        ag_venue = None
        ag_performance = None
        try:
            ag_venue = AugusVenue\
                .query.filter(AugusVenue.code == record.venue_code)\
                      .filter(AugusVenue.version == record.venue_version)\
                      .filter(AugusVenue.augus_account_id == augus_account.id)\
                      .one()
        except (NoResultFound, MultipleResultsFound) as err:
            logger.error(
                'Cannot import augus performance: '
                'no such AugusVenue: '
                'code={} version={}: {}'.format(record.venue_code, record.venue_version, repr(err))
            )
            raise AugusDataImportError()

        try:
            ag_performance = AugusPerformance\
                .query\
                .filter(AugusPerformance.augus_event_code==record.event_code)\
                .filter(AugusPerformance.augus_performance_code==record.performance_code)\
                .one()
        except MultipleResultsFound as err:
            raise # erorr
        except NoResultFound as err:
            ag_performance = AugusPerformance()
            ag_performance.augus_event_code = record.event_code,
            ag_performance.augus_performance_code = record.performance_code

        ag_performance.augus_venue_code = record.venue_code
        ag_performance.augus_venue_name = record.venue_name
        ag_performance.augus_event_name = record.event_name
        ag_performance.augus_performance_name = record.performance_name

        ag_performance.open_on = record.open_on_datetime
        ag_performance.start_on = record.start_on_datetime
        ag_performance.augus_venue_version = record.venue_version
        ag_performance.augus_account_id = augus_account.id
        ag_performance.save()
        return ag_performance

    def import_record_all(self, records, augus_account):
        elms = []
        for record in records:
            elm = self.import_record(record, augus_account)
            elms.append(elm)
        return elms

    def import_(self, protocol, augus_account):
        return self.import_record_all(protocol, augus_account)

class AugusTicketImpoter(object):
    def import_record(self, record, augus_account):
        ag_ticket = AugusTicket.get(augus_event_code=record.event_code,
                                    augus_performance_code=record.performance_code,
                                    augus_seat_type_code=record.seat_type_code,
                                    unit_value_code=record.unit_value_code,
                                    )
        ag_performance = None
        if not ag_ticket:
            ag_ticket = AugusTicket()
            ag_performance = AugusPerformance.get(augus_event_code=record.event_code,
                                                  augus_performance_code=record.performance_code,
                                                  )
            if not ag_performance:
                logger.error('AugusPerformance not found: event_code={} performance_code={}'.format(
                    record.event_code, record.performance_code))
                raise AugusPerformanceNotFound()
        else:
            ag_performance = ag_ticket.augus_performance
        ag_ticket.augus_venue_code = record.venue_code
        ag_ticket.augus_seat_type_code = record.seat_type_code
        ag_ticket.augus_seat_type_name = record.seat_type_name
        ag_ticket.unit_value_name = record.unit_value_name
        ag_ticket.unit_value_code = record.unit_value_code
        ag_ticket.augus_seat_type_classif = record.seat_type_classif
        ag_ticket.value = record.value
        ag_ticket.augus_performance_id = ag_performance.id
        ag_ticket.augus_account_id = augus_account.id
        ag_ticket.save()
        return ag_ticket


    def import_record_all(self, records, augus_account):
        elms = []
        for record in records:
            elm = self.import_record(record, augus_account)
            elms.append(elm)
        return elms

    def import_(self, protocol, augus_account):
        return self.import_record_all(protocol, augus_account)


class AugusDistributionImporter(object):
    def __init__(self):
        self.__slave_session = get_db_session(get_current_request(), name="slave")

    def import_record(self, record, stock, ag_performance):
        ag_venue = AugusVenue.query.filter(AugusVenue.code==ag_performance.augus_venue_code)\
                                   .filter(AugusVenue.version==ag_performance.augus_venue_version)\
                                   .first()
        if not ag_venue:
            raise IllegalImportDataError('Not found augus venue by augus_performance: augus_performance_id={}'
                                         .format(ag_performance.id))

        ag_seat = self.get_augus_seat(ag_venue=ag_venue,
                                      area_code=record.area_code,
                                      info_code=record.info_code,
                                      floor=record.floor,
                                      column=record.column,
                                      number=record.number,
                                      ticket_number=record.ticket_number if hasattr(record, 'ticket_number') else None
                                      )
        if not ag_seat:
            raise IllegalImportDataError('Not found augus seat: venue={}/area={}/info={}/floor={}/column={}/num={}'.format(
                    ag_venue.id, record.area_code, record.info_code, record.floor, record.column, record.number))

        try:
            ag_ticket = AugusTicket\
                .query\
                .filter(AugusTicket.augus_performance_id == ag_performance.id)\
                .filter(AugusTicket.augus_seat_type_code == record.seat_type_code)\
                .filter(AugusTicket.unit_value_code == record.unit_value_code)\
                .one()
        except (MultipleResultsFound, NoResultFound) as err:
            raise IllegalImportDataError('no such augus ticket: {}: augus performance id={}, augus seat type code={}, augus unit value code={}'
                                       .format(repr(err), ag_performance.id, record.seat_type_code, record.unit_value_code))

        seat = self.augus_seat_to_real_seat(ag_performance, ag_seat)
        stock_info = get_enable_stock_info(seat)
        if stock_info:
            raise IllegalImportDataError('already exit stock info: AugusStockInfo.id={}'
                                         .format(stock_info.id))

        old_stock = seat.stock
        if seat.status in [SeatStatusEnum.NotOnSale.v, SeatStatusEnum.Vacant.v, SeatStatusEnum.Canceled.v]:
            # 未割当 かつ 配席可能な状態

            # 今回移動した座席に関しては枠移動の必要がないため許容する
            # ただし席種は一致していなければならない
            if old_stock.stock_holder != None and old_stock != stock:
                raise IllegalImportDataError('Cannot seat move: seat_id={}'.format(seat.id))

            ag_stock_info = get_or_create_augus_stock_info(seat)
            ag_stock_info.augus_account_id = ag_performance.augus_account_id
            ag_stock_info.augus_performance_id = ag_performance.id
            ag_stock_info.augus_distribution_code = record.distribution_code
            ag_stock_info.seat_type_classif = record.seat_type_classif
            ag_stock_info.distributed_at = datetime.datetime.now()
            ag_stock_info.augus_seat_id = ag_seat.id
            ag_stock_info.seat_id = seat.id
            ag_stock_info.augus_ticket_id = ag_ticket.id
            ag_stock_info.quantity = record.seat_count
            ag_stock_info.save()

            ag_detail = get_augus_stock_detail(ag_stock_info, record)
            if ag_detail:  # 既に同じ席に対して同じ席種コード、同じ単価コードの配券があった場合はエラーする
                raise IllegalImportDataError('already exit AugusStockDetail: id={}'.format(ag_detail))
            else:
                # 新規の配券
                # 1つの席に席種コードや単価コードが違う複数の配券はありえるのでそれは許容する
                ag_detail = AugusStockDetail()
                ag_detail.augus_distribution_code = record.distribution_code
                ag_detail.seat_type_classif = record.seat_type_classif
                ag_detail.distributed_at = datetime.datetime.now()
                ag_detail.augus_seat_type_code = record.seat_type_code
                ag_detail.augus_unit_value_code = record.unit_value_code
                ag_detail.start_on = record.start_on_datetime
                ag_detail.quantity = ag_stock_info.quantity
                ag_detail.augus_stock_info_id = ag_stock_info.id
                ag_detail.augus_ticket_id = ag_ticket.id
                ag_detail.save()

                # seat の割当
                if old_stock != stock: # stockが同じなら移動の必要はない
                    seat.stock_id = stock.id
                    stock.quantity += 1
                    old_stock.quantity -= 1
                    stock.save()
                    old_stock.save()
                    seat.save()
                return seat
        else:
            raise IllegalImportDataError('Cannot seat allocation: seat_id={} augus_seat_id={}'.format(
                seat.id, ag_seat.id))

    def import_record_of_unreserved_seat(self, record, stock, ag_performance):
        ag_ticket = self.__get_augus_ticket_of_unreserved_seat(record, ag_performance)
        ag_stock_info = self.__get_augus_stock_info_of_unreserved_seat(record, ag_performance, ag_ticket)
        if not ag_stock_info:
            ag_stock_info = AugusStockInfo()  # なければ新規作成
            ag_stock_info.quantity = 0
            ag_stock_info.augus_account_id = ag_performance.augus_account_id
            ag_stock_info.augus_performance_id = ag_performance.id
            ag_stock_info.seat_type_classif = record.seat_type_classif
            ag_stock_info.augus_ticket_id = ag_ticket.id

        ag_stock_info.augus_distribution_code = record.distribution_code
        ag_stock_info.distributed_at = datetime.datetime.now()
        ag_stock_info.quantity += int(record.seat_count)
        ag_stock_info.save()

        ag_detail = AugusStockDetail()
        ag_detail.augus_distribution_code = record.distribution_code
        ag_detail.seat_type_classif = record.seat_type_classif
        ag_detail.distributed_at = datetime.datetime.now()
        ag_detail.augus_seat_type_code = record.seat_type_code
        ag_detail.augus_unit_value_code = record.unit_value_code
        ag_detail.start_on = record.start_on_datetime
        ag_detail.quantity = int(record.seat_count)
        ag_detail.augus_stock_info_id = ag_stock_info.id
        ag_detail.augus_ticket_id = ag_ticket.id
        ag_detail.save()

        stock.quantity += int(record.seat_count)
        stock.save()

    def _create_stock_holder(self, performance, name, account_id):
        stock_holder = StockHolder()
        stock_holder.name = name
        stock_holder.event_id = performance.event_id
        stock_holder.style = u'{"text": "\u8ffd", "text_color": "#a62020"}'
        stock_holder.account_id = account_id
        stock_holder.is_putback_target = True
        stock_holder.save()
        return stock_holder

    def import_record_all(self, records, augus_account):
        success_records = []
        allocated_seats = []
        stock_holders = {}
        for augus_event_code, _records in itertools.groupby(records, lambda record: record.event_code):
            for record in records:
                ag_performance = AugusPerformance\
                    .query\
                    .join(AugusAccount)\
                    .filter(AugusPerformance.augus_event_code==record.event_code)\
                    .filter(AugusPerformance.augus_performance_code==record.performance_code)\
                    .filter(AugusAccount.id==augus_account.id)\
                    .first()
                if not ag_performance:
                    raise AugusDataImportError(u'augus performance not found')
                elif not ag_performance.performance:
                    raise AugusDataImportError(u'This performance has not been cooperation: AugusPerformance.id={}'.format(ag_performance.id))

                if SeatTypeClassif.FREE == SeatTypeClassif.get(record.seat_type_classif) \
                        and not augus_account.enable_unreserved_seat:
                    raise IllegalImportDataError(
                        'distribution of unreserved seat is disabled in AugusAccount[{}]: {}'
                            .format(augus_account.id, vars(record)))

                # 新しいStockHolderを作成 (初回のみ実行される事を想定)
                stock_holder = stock_holders.get(ag_performance.performance.event, None)
                if not stock_holder:
                    if augus_account.enable_auto_distribution_to_own_stock_holder:
                        stock_holder = StockHolder.query.filter(
                            StockHolder.event_id == ag_performance.performance.event_id,
                            StockHolder.name == u'自社',
                            StockHolder.deleted_at.is_(None)
                        ).first()

                        if not stock_holder:
                            raise AugusDataImportError(u'Not found own stock holder: event_id={}, name={}'
                                                       .format(ag_performance.performance.event_id, u'自社'))
                    else:
                        name = u'オーガス連携:' + time.strftime('%Y-%m-%d-%H-%M-%S')
                        account_id = 35  # 楽天チケット　ううっ(直したい)
                        stock_holder = self._create_stock_holder(ag_performance.performance, name, account_id)
                    stock_holders[ag_performance.performance.event] = stock_holder

                ag_ticket = AugusTicket\
                    .query\
                    .join(AugusAccount)\
                    .filter(AugusTicket.augus_performance_id==ag_performance.id)\
                    .filter(AugusTicket.augus_seat_type_code==record.seat_type_code)\
                    .filter(AugusAccount.id==augus_account.id)\
                    .first()

                # validation
                if not ag_ticket:
                    raise AugusDataImportError(
                        'AugusTicket not found: perforance={}, augus_ticket.code={}'.format(
                            ag_performance.performance.id, record.seat_type_code))
                elif not ag_ticket.stock_type:
                    raise AugusDataImportError(
                        'AugusTicket not linked to StockType: AugusTicket.id={} '.format(ag_ticket.id))

                # 対象のStockを探す
                stock = None
                for stock in stock_holder.stocks:
                    # stockが持つstock_typeのidとaugus_ticketがもつstock_typeのidが同じものが対象
                    if stock.stock_type_id == ag_ticket.stock_type.id and\
                       stock.performance_id == ag_performance.performance_id:
                        break
                else: # 対象となるStockがない
                    raise AugusDataImportError(
                        'AugusTicket not linked to StockType: AugusTicket.id={}, '.format(ag_ticket.id))

                if stock:
                    if SeatTypeClassif.FREE == SeatTypeClassif.get(record.seat_type_classif):
                        self.import_record_of_unreserved_seat(record, stock, ag_performance)
                        success_records.append(record)
                    else:
                        seat = self.import_record(record, stock, ag_performance)
                        success_records.append(record)
                        allocated_seats.append(seat)
                        seat.save()
        return success_records

    def import_(self, records, augus_account):
        return self.import_record_all(records, augus_account)

    @staticmethod
    def get_augus_seat(ag_venue, area_code, info_code, floor, column, number, ticket_number):
        return AugusSeat.query.filter(AugusSeat.augus_venue_id == ag_venue.id)\
                              .filter(AugusSeat.area_code == area_code)\
                              .filter(AugusSeat.info_code == info_code)\
                              .filter(AugusSeat.floor == floor)\
                              .filter(AugusSeat.column == column)\
                              .filter(AugusSeat.num == number)\
                              .filter(AugusSeat.ticket_number == ticket_number)\
                              .first()

    @staticmethod
    def augus_seat_to_real_seat(ag_performance, ag_seat):
        base_seat = ag_seat.seat
        performance = ag_performance.performance
        venue = Venue.query.filter(Venue.performance_id==performance.id).one()
        seat = Seat.query.filter(Seat.l0_id==base_seat.l0_id)\
                         .filter(Seat.venue_id==venue.id)\
                         .first()
        if seat:
            return seat
        else:
            raise NoSeatError()

    def __get_augus_ticket_of_unreserved_seat(self, record, ag_performance):
        ag_ticket = self.__slave_session.query(AugusTicket)\
            .filter(AugusTicket.augus_performance_id == ag_performance.id,
                    AugusTicket.augus_seat_type_code == record.seat_type_code,
                    AugusTicket.unit_value_code == record.unit_value_code,
                    AugusTicket.augus_account_id == ag_performance.augus_account_id,
                    AugusTicket.augus_seat_type_classif == record.seat_type_classif,
                    AugusTicket.deleted_at.is_(None))\
            .first()
        if not ag_ticket:
            raise IllegalImportDataError(u'Not found augus ticket: ' +
                                         u'augus_perfomrance_id={}, '.format(ag_performance.id) +
                                         u'augus_account_id={}, '.format(ag_performance.augus_account_id) +
                                         u'record={}'.format(vars(record)))

        return ag_ticket

    @staticmethod
    def __get_augus_stock_info_of_unreserved_seat(record, ag_performance, ag_ticket):
        # 更新のためmasterから取得
        return AugusStockInfo.query\
            .filter(AugusStockInfo.augus_performance_id == ag_performance.id,
                    AugusStockInfo.seat_type_classif == record.seat_type_classif,
                    AugusStockInfo.augus_seat_id.is_(None),
                    AugusStockInfo.seat_id.is_(None),
                    AugusStockInfo.augus_ticket_id == ag_ticket.id,
                    AugusStockInfo.deleted_at.is_(None))\
            .first()


class AugusPutbackImporter(object):
    def __init__(self):
        self._slave_session = get_db_session(get_current_request(), name="slave")

    def import_(self, records, augus_account):
        return self.__import_record_all(records, augus_account)

    def __import_record_all(self, records, augus_account):
        records_dict_group_by_augus_performance = self.__group_records_dict_by_augus_performance(augus_account, records)
        putback_code = self.__get_new_putback_code()
        putback_codes = []

        for augus_performance, records_group_by_performance in records_dict_group_by_augus_performance.items():
            self.__import_records_group_by_performance(records_group_by_performance,
                                                       augus_account, augus_performance, putback_code)
            putback_codes.append(putback_code)
            putback_code += 1

        return putback_codes

    def __import_records_group_by_performance(self, records_group_by_performance, augus_account,
                                              augus_performance, putback_code):
        putback_stock_holder = self.__create_stock_holder_for_auto_putback(augus_performance.performance.event_id)
        augus_putback = self.__create_augus_putback(augus_account, augus_performance, putback_code)

        records_of_unreserved_seat = []
        records_of_reserved_seat = []
        for record in records_group_by_performance:
            if SeatTypeClassif.FREE == SeatTypeClassif.get(record.seat_type_classif):
                records_of_unreserved_seat.append(record)
            else:
                records_of_reserved_seat.append(record)

        self.__import_records_of_reserved_seat(records_of_reserved_seat, augus_account, augus_performance,
                                               augus_putback, putback_stock_holder)
        self.__import_records_of_unreserved_seat(records_of_unreserved_seat, augus_account, augus_performance,
                                               augus_putback, putback_stock_holder)

    def __import_records_of_reserved_seat(self, records, augus_account, augus_performance
                                          , augus_putback, putback_stock_holder):
        augus_seat_and_record_list = \
            self.__get_augus_seat_and_record_list(augus_account, augus_performance, records)

        for augus_seat, record in augus_seat_and_record_list:
            augus_stock_info = self.__get_enable_augus_stock_info(augus_seat)
            putback_stock = self.__get_putback_stock(putback_stock_holder, augus_performance, augus_stock_info)

            self.__allocate_seat(augus_stock_info.seat.id, putback_stock, long(record.seat_count))
            for augus_stock_detail in augus_stock_info.augus_stock_details:
                augus_stock_detail.augus_putback_id = augus_putback.id
                augus_stock_detail.save()

    def __import_records_of_unreserved_seat(self, records, augus_account, augus_performance
                                          , augus_putback, putback_stock_holder):

        def move_stock_count(to_stock, from_stock, count):
            to_stock.quantity += count
            from_stock.quantity = from_stock.quantity - count
            to_stock.save()
            from_stock.save()

        for record in records:
            if SeatTypeClassif.FREE == SeatTypeClassif.get(record.seat_type_classif) \
                    and not augus_account.enable_unreserved_seat:
                raise AugusDataImportError(
                    'distribution of unreserved seat is disabled in AugusAccount[{}]: {}'
                        .format(augus_account.id, vars(record)))

            augus_stock_info = self.__get_augus_stock_info_of_unreserved_seat(augus_performance, record)
            putback_stock = self.__get_putback_stock(putback_stock_holder, augus_performance, augus_stock_info)
            own_stock = self.__get_own_stock(augus_performance, augus_stock_info)

            seat_count = long(record.seat_count)
            if own_stock.stock_status.quantity >= seat_count:
                #　全て返券可能な場合は、成功のAugusStockDetailのみ作る
                move_stock_count(putback_stock, own_stock, seat_count)
                self.__create_stock_detail(augus_stock_info, augus_putback, seat_count, AugusPutbackStatus.CANDO)
                # augus_stock_infoの在庫を更新
                augus_stock_info.quantity = augus_stock_info.quantity - seat_count
                augus_stock_info.save()
            elif own_stock.stock_status.quantity > 0:
                # 一部のみ返券可能の場合は、成功のAugusStockDetailと失敗のAugusStockDetailを作る
                putback_seat_count = own_stock.stock_status.quantity
                move_stock_count(putback_stock, own_stock, putback_seat_count)
                self.__create_stock_detail(augus_stock_info, augus_putback, putback_seat_count,
                                           AugusPutbackStatus.CANDO)
                self.__create_stock_detail(augus_stock_info, augus_putback, seat_count - putback_seat_count,
                                           AugusPutbackStatus.CANNOT)
                # augus_stock_infoの在庫を更新
                augus_stock_info.quantity = augus_stock_info.quantity - putback_seat_count
                augus_stock_info.save()
            else:
                # 全て返券不可能な場合は、失敗のAugusStockDetailのみ作る
                self.__create_stock_detail(augus_stock_info, augus_putback, seat_count,
                                           AugusPutbackStatus.CANNOT)

    @staticmethod
    def __create_stock_detail(augus_stock_info, augus_putback, seat_count, status):
        augus_stock_detail = AugusStockDetail()
        augus_stock_detail.augus_distribution_code = augus_stock_info.augus_distribution_code
        augus_stock_detail.augus_seat_type_code = augus_stock_info.augus_ticket.augus_seat_type_code
        augus_stock_detail.augus_unit_value_code = augus_stock_info.augus_ticket.unit_value_code
        augus_stock_detail.seat_type_classif = augus_stock_info.seat_type_classif
        augus_stock_detail.quantity = seat_count
        augus_stock_detail.augus_stock_info_id = augus_stock_info.id
        augus_stock_detail.augus_putback_id = augus_putback.id
        augus_stock_detail.augus_ticket_id = augus_stock_info.augus_ticket.id
        augus_stock_detail.start_on = 0  # 自由席返券用なのでダミー値にする
        augus_stock_detail.distributed_at = 0  # 自由席返券用なのでダミー値にする
        augus_stock_detail.augus_unreserved_putback_status = status
        augus_stock_detail.save()

    def __group_records_dict_by_augus_performance(self, augus_account, records):
        records_dict_group_by_augus_performance = dict()

        augus_performances = self.__get_augus_performances(augus_account, records)

        def to_tuple(ag_p):
            return u'{}_{}'.format(ag_p.augus_event_code, ag_p.augus_performance_code), ag_p

        # 必要十分確認用の中間データ
        augus_performance_dict_to_verify = dict(map(to_tuple, augus_performances)) if augus_performances else dict()

        for record in records:
            if not u'{}_{}'.format(record.event_code, record.performance_code) in augus_performance_dict_to_verify:
                # AugusPerformanceなし or ひもづくAugusVenue, Perfomrance, Venueがない
                raise AugusDataImportError(u'Not found AugusPerformance link to Performance: ' +
                                           u'augus_account_id={}, '.format(augus_account.id) +
                                           u'event_code={}, '.format(record.event_code) +
                                           u'performance_code={}'.format(record.performance_code))

            key = augus_performance_dict_to_verify[u'{}_{}'.format(record.event_code, record.performance_code)]
            if key in records_dict_group_by_augus_performance:
                records_dict_group_by_augus_performance[key].append(record)
            else:
                records_dict_group_by_augus_performance.update({key: [record]})

        return records_dict_group_by_augus_performance

    @staticmethod
    def __create_stock_holder_for_auto_putback(event_id):
        stock_holder = StockHolder()
        stock_holder.name = u'オーガス自動返券枠_{}'.format(time.strftime('%Y%m%d_%H%M%S'))
        stock_holder.event_id = event_id
        stock_holder.style = u'{"text": "\u8ffd", "text_color": "#a62020"}'
        stock_holder.account_id = 35 # 楽天チケット固定
        stock_holder.is_putback_target = True
        stock_holder.save()
        return stock_holder

    @staticmethod
    def __create_augus_putback(augus_account, augus_performance, putback_code):
        augus_putback = AugusPutback()
        augus_putback.augus_account_id = augus_account.id
        augus_putback.augus_performance_id = augus_performance.id
        augus_putback.augus_putback_code = putback_code
        augus_putback.reserved_at = datetime.datetime.now()
        augus_putback.save()
        return augus_putback

    def __get_augus_performances(self, augus_account, records):
        return self._slave_session.query(AugusPerformance)\
            .join(Performance,
                  Performance.id == AugusPerformance.performance_id) \
            .options(contains_eager(AugusPerformance.performance)) \
            .filter(AugusPerformance.augus_account_id == augus_account.id,
                    tuple_(AugusPerformance.augus_event_code, AugusPerformance.augus_performance_code)
                    .in_(map(lambda r: (r.event_code, r.performance_code), records)),
                    AugusPerformance.deleted_at.is_(None),
                    Performance.deleted_at.is_(None))\
            .all()

    def __get_new_putback_code(self):
        latest_augus_putback = self._slave_session.query(AugusPutback)\
            .order_by(AugusPutback.augus_putback_code.desc())\
            .first()
        return latest_augus_putback.augus_putback_code + 1 if latest_augus_putback is not None else 1

    def __get_augus_seat_and_record_list(self, augus_account, augus_performance, records):
        augus_venue = self._slave_session.query(AugusVenue)\
            .filter(AugusVenue.code == augus_performance.augus_venue_code,
                    AugusVenue.version == augus_performance.augus_venue_version,
                    AugusVenue.deleted_at.is_(None))\
            .first()
        if not augus_venue:
            raise AugusDataImportError(u'Not found AugusVenue: ' +
                                       u'augus_venue_code={}, '.format(augus_performance.augus_venue_code) +
                                       u'augus_venue_version={}, '.format(augus_performance.augus_venue_version))

        def to_tuple(data):
            # 整理券フォーマットでないときticket_numberをNoneにするとSQLのIN句にNULLを条件に検索しようとするが
            # IN句ではNULLが評価できないため検索結果なしとなる。このため固定値にし、クエリ生成でも同じ固定値で整理券を検索することで対策
            return (
                long(data.block),
                long(data.coordy),
                long(data.coordx),
                data.floor,
                data.column,
                data.number if hasattr(data, 'number') else data.num,
                long(data.area_code),
                long(data.info_code),
                long(data.ticket_number) if augus_account.use_numbered_ticket_format else 'not_care'
            )

        augus_seats = self._slave_session.query(AugusSeat)\
            .filter(AugusSeat.augus_venue_id == augus_venue.id,
                    tuple_(
                        AugusSeat.block,
                        AugusSeat.coordy,
                        AugusSeat.coordx,
                        AugusSeat.floor,
                        AugusSeat.column,
                        AugusSeat.num,
                        AugusSeat.area_code,
                        AugusSeat.info_code,
                        AugusSeat.ticket_number if augus_account.use_numbered_ticket_format else 'not_care'
                    ).in_(map(to_tuple, records)),
                    AugusSeat.deleted_at.is_(None))\
            .all()

        augus_seat_dicts_to_verify = dict(zip(map(to_tuple, augus_seats), augus_seats)) if augus_seats else dict()
        augus_seat_and_record_list = []
        for record in records:
            # 必要十分かチェック
            if to_tuple(record) not in augus_seat_dicts_to_verify:
                raise AugusDataImportError(u'Not found AugusSeat: ' +
                                           u'augus_venue_id={}, '.format(augus_venue.id) +
                                           u'record={}'.format(vars(record)))
            augus_seat = augus_seat_dicts_to_verify[to_tuple(record)]
            augus_seat_and_record_list.append((augus_seat, record))

        return augus_seat_and_record_list

    @staticmethod
    def __get_enable_augus_stock_info(augus_seat):
        valid_seat_status = [SeatStatusEnum.NotOnSale.v, SeatStatusEnum.Vacant.v, SeatStatusEnum.Canceled.v]

        augus_stock_info = AugusStockInfo.query\
            .join(AugusStockDetail,
                  AugusStockDetail.augus_stock_info_id == AugusStockInfo.id)\
            .join(AugusTicket,
                  AugusTicket.id == AugusStockInfo.augus_ticket_id)\
            .join(Seat,
                  AugusStockInfo.seat_id == Seat.id)\
            .join(SeatStatus,
                  SeatStatus.seat_id == Seat.id) \
            .options(contains_eager(AugusStockInfo.augus_stock_details)) \
            .options(contains_eager(AugusStockInfo.augus_ticket)) \
            .options(contains_eager(AugusStockInfo.seat)) \
            .filter(AugusStockInfo.augus_seat_id == augus_seat.id,
                    AugusStockInfo.deleted_at.is_(None),
                    AugusStockDetail.augus_putback_id.is_(None),
                    AugusTicket.deleted_at.is_(None),
                    Seat.deleted_at.is_(None),
                    SeatStatus.status.in_(valid_seat_status),
                    SeatStatus.deleted_at.is_(None))\
            .first()
        if not augus_stock_info:
            # 連携・配券できていないケース or データ不整合
            raise AugusDataImportError(u'Not found AugusStockInfo on seat status[{}]: '.format(valid_seat_status) +
                                       u'augus_seat_id={}, '.format(augus_seat.id))
        return augus_stock_info

    def __get_augus_stock_info_of_unreserved_seat(self, augus_performance, record):
        augus_stock_info_list = AugusStockInfo.query\
            .join(AugusTicket,
                  AugusTicket.id == AugusStockInfo.augus_ticket_id) \
            .options(contains_eager(AugusStockInfo.augus_ticket)) \
            .filter(AugusTicket.augus_performance_id == augus_performance.id,
                    AugusTicket.augus_seat_type_code == record.seat_type_code,
                    AugusTicket.unit_value_code == record.unit_value_code,
                    AugusStockInfo.deleted_at.is_(None),
                    AugusTicket.deleted_at.is_(None))\
            .all()
        if not augus_stock_info_list or len(augus_stock_info_list) != 1:
            # 連携・配券できていないケース or データ不整合 自由席だと一つのみのはず
            raise AugusDataImportError(u'Not found AugusStockInfo or some AugusStockInfo exist: ' +
                                       u'augus_performance_id={}, '.format(augus_performance.id) +
                                       u'record={}'.format(vars(record)))

        # 自由席では一つしかない想定
        return augus_stock_info_list[0]

    @staticmethod
    def __get_own_stock(augus_performance, augus_stock_info):
        own_stock = Stock.query\
            .join(StockHolder,
                  StockHolder.id == Stock.stock_holder_id) \
            .join(StockStatus,
                  StockStatus.stock_id == Stock.id) \
            .options(contains_eager(Stock.stock_status)) \
            .filter(Stock.performance_id == augus_performance.performance_id,
                    Stock.stock_type_id == augus_stock_info.augus_ticket.stock_type_id,
                    Stock.deleted_at.is_(None),
                    StockHolder.name == u'自社',
                    StockHolder.deleted_at.is_(None),
                    StockStatus.deleted_at.is_(None)) \
            .first()
        if not own_stock:
            raise AugusDataImportError(u'Not found own Stock: ' +
                                       u'performance_id={}, '.format(augus_performance.performance_id) +
                                       u'stock_type_id={}'.format(augus_stock_info.augus_ticket.stock_type_id))

        return own_stock

    @staticmethod
    def __get_putback_stock(putback_stock_holder, augus_perforamnce, augus_stock_info):
        for stock in putback_stock_holder.stocks:
            if stock.stock_type_id == augus_stock_info.augus_ticket.stock_type_id \
                    and stock.performance_id == augus_perforamnce.performance_id:
                return stock
        else:
            raise AugusDataImportError(u'Not found putback stock: ' +
                                       u'stock_type_id={}, '.format(augus_stock_info.augus_ticket.stock_type_id) +
                                       u'performance_id={}'.format(augus_perforamnce.performance_id))

    @staticmethod
    def __allocate_seat(seat_id, putback_stock, seat_count):
        seat = Seat.query.join(Stock)\
            .filter(Seat.id == seat_id,
                    Seat.deleted_at.is_(None))\
            .first() # get seat from master session
        if not seat:
            raise AugusDataImportError(u'Not found Seat: seat_id={}'.format(seat_id))
        old_stock = seat.stock
        if not old_stock:
            raise AugusDataImportError(u'Not found Stock allocated Seat: seat_id={}'.format(seat_id))

        putback_stock.quantity += seat_count
        old_stock.quantity = max(old_stock.quantity - seat_count, 0)
        seat.stock_id = putback_stock.id

        putback_stock.save()
        old_stock.save()
        seat.save()


class AugusAchieveImporter(object):
    def __init__(self):
        self.__slave_session = get_db_session(get_current_request(), name="slave")

    def import_(self, records, augus_account):
        return self.__import_record_all(records, augus_account)

    def __import_record_all(self, records, augus_account):
        if len(records) == 0:
            return []

        couple_of_event_and_performance_code = self.__get_unique_couple_of_event_and_performance_code(records)
        augus_performances = self.__get_augus_performances(augus_account.id, couple_of_event_and_performance_code)
        augus_performances_ids = map(lambda ag_performance: ag_performance.id, augus_performances)

        AugusPerformance.query.filter(AugusPerformance.id.in_(augus_performances_ids))\
             .update({AugusPerformance.is_report_target: True}, synchronize_session='fetch')

        return augus_performances_ids

    @staticmethod
    def __get_unique_couple_of_event_and_performance_code(records):
        couple_of_event_and_performance_code = []
        for record in records:
            if (record.event_code, record.performance_code) not in couple_of_event_and_performance_code:
                couple_of_event_and_performance_code.append((record.event_code, record.performance_code))
        return couple_of_event_and_performance_code

    def __get_augus_performances(self, augus_account_id, couple_of_event_and_performance_code):
        # tuple_はmysqlやpostgreSQLなどでのみ動くことに注意
        augus_performances = self.__slave_session.query(AugusPerformance).filter(
            tuple_(AugusPerformance.augus_event_code, AugusPerformance.augus_performance_code)
                .in_(couple_of_event_and_performance_code),
            AugusPerformance.augus_account_id == augus_account_id,
            AugusPerformance.deleted_at.is_(None)
        ).all()

        event_and_performance_code_from_augus_performance = \
            map(lambda ag_p: (ag_p.augus_event_code, ag_p.augus_performance_code), augus_performances) \
                if augus_performances else []

        # 取得したAugusPerformanceがリクエストと必要十分かチェック
        for event_code, performance_code in couple_of_event_and_performance_code:
            if (long(event_code), long(performance_code)) not in event_and_performance_code_from_augus_performance:
                # 一つでもなければ対象ファイルの処理を終了する
                raise AugusDataImportError(u'Not found augus_performance: ' +
                                           u'augus_account_id={}, '.format(augus_account_id) +
                                           u'event_code={}, '.format(event_code) +
                                           u'performance_code={}'.format(performance_code))
        return augus_performances

