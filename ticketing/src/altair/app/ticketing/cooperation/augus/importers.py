#-*- coding: utf-8 -*-
import time
import datetime
import itertools
from sqlalchemy.orm.exc import (
    MultipleResultsFound,
    NoResultFound,
    )
from altair.app.ticketing.core.models import (
    Seat,
    Venue,
    Event,
    Performance,
    Stock,
    StockHolder,
    AugusPerformance,
    AugusVenue,
    AugusTicket,
    AugusSeat,
    AugusStockInfo,
    SeatStatusEnum,
    )
from .errors import (
    AugusDataImportError,
    NoSeatError,
    )

class AugusPerformanceImpoter(object):
    def import_record(self, record):
        ag_venue = None
        ag_performance = None
        try:
            ag_venue = AugusVenue\
                .query.filter(AugusVenue.code==record.venue_code)\
                      .filter(AugusVenue.version==record.venue_version)\
                      .first()
        except (NoResultFound, MultipleResultFound)as err:
            raise AugusDataImportError('Cannot import augus performance: '
                                       'no such AugusVenue: '
                                       'code={} version={}: {}'.format(record.venue_code, record.venue_version, repr(err))
                                       )

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
        ag_performance.save()
        return ag_performance

    def import_record_all(self, records):
        elms = []
        for record in records:
            elm = self.import_record(record)
            elms.append(elm)
        return elms

    def import_(self, protocol):
        return self.import_record_all(protocol)

class AugusTicketImpoter(object):
    def import_record(self, record):
        ag_ticket = AugusTicket.get(augus_event_code=record.event_code,
                                    augus_performance_code=record.performance_code,
                                    augus_seat_type_code=record.seat_type_code,
                                    )
        ag_performance = None
        if not ag_ticket:
            ag_ticket = AugusTicket()
            ag_performance = AugusPerformance.get(augus_event_code=record.event_code,
                                                  augus_performance_code=record.performance_code,
                                                  )
            if not ag_performance:
                raise AugusDataImportError('AugusPerformance not found: event_code={} performance_code={}'.format(
                    record.event_code, record.performance_code))
        else:
            ag_performance = ag_ticket.augus_performance
        ag_ticket.augus_venue_code = record.venue_code
        ag_ticket.augus_seat_type_code = record.seat_type_code
        ag_ticket.augus_seat_type_name = record.seat_type_name
        ag_ticket.unit_value_name = record.unit_value_name
        ag_ticket.augus_seat_type_classif = record.seat_type_classif
        ag_ticket.value = record.value
        ag_ticket.augus_performance_id = ag_performance.id
        ag_ticket.save()
        return ag_ticket


    def import_record_all(self, records):
        elms = []
        for record in records:
            elm = self.import_record(record)
            elms.append(elm)
        return elms

    def import_(self, protocol):
        return self.import_record_all(protocol)


class AugusDistributionImporter(object):
    def import_record(self, record, stock, ag_performance):
        ag_venue = AugusVenue.query.filter(AugusVenue.code==ag_performance.augus_venue_code)\
                                   .filter(AugusVenue.version==ag_performance.augus_venue_version)\
                                   .one()

        ag_seat = self.get_augus_seat(ag_venue=ag_venue,
                                      area_code=record.area_code,
                                      info_code=record.info_code,
                                      floor=record.floor,
                                      column=record.column,
                                      number=record.number,
                                      )
        seat = self.augus_seat_to_real_seat(ag_performance, ag_seat)
        old_stock = seat.stock

        if old_stock.stock_holder == None and seat.status in [SeatStatusEnum.NotOnSale.v, SeatStatusEnum.Vacant.v]:
            # 未割当 かつ 配席可能な状態

            # AugusStockInfo生成
            ag_stock_info = AugusStockInfo()
            ag_stock_info.augus_performance_id = ag_performance.id
            ag_stock_info.augus_distribution_code = record.distribution_code
            ag_stock_info.seat_type_classif = record.seat_type_classif
            ag_stock_info.distributed_at = datetime.datetime.now()
            ag_stock_info.augus_seat_id = ag_seat.id
            ag_stock_info.quantity = record.seat_count
            ag_stock_info.save()

            # seat の割当
            seat.stock_id = stock.id
            stock.quantity += 1
            old_stock.quantity -= 1
            stock.save()
            old_stock.save()
            seat.save()
            return seat
        else:
            raise AugusDataImportError('Cannot seat allocation: seat_id={} augus_seat_id={}'.format(
                seat.id, ag_seat.id))

    def _create_stock_holder(self, performance, name, account_id):
        stock_holder = StockHolder()
        stock_holder.name = name
        stock_holder.event_id = performance.event_id
        stock_holder.style = u'{"text": "\u8ffd", "text_color": "#a62020"}'
        stock_holder.account_id = account_id
        stock_holder.save()
        return stock_holder

    def import_record_all(self, records):
        success_records = []
        allocated_seats = []
        stock_holders = {}
        for augus_event_code, _records in itertools.groupby(records, lambda record: record.event_code):
            for record in records:
                ag_performance = AugusPerformance\
                    .query\
                    .filter(AugusPerformance.augus_event_code==record.event_code)\
                    .filter(AugusPerformance.augus_performance_code==record.performance_code)\
                    .one()

                # 新しいStockHolderを作成 (初回のみ実行される事を想定)
                stock_holder = stock_holders.get(ag_performance.performance.event, None)
                if not stock_holder:
                    name = u'オーガス連携:' + time.strftime('%Y-%m-%d-%H-%M-%S')
                    account_id = 97 # キョードー大阪
                    stock_holder = self._create_stock_holder(ag_performance.performance,
                                                             name, account_id)
                    stock_holders[ag_performance.performance.event] = stock_holder

                ag_ticket = AugusTicket.query.filter(AugusTicket.augus_performance_id==ag_performance.id)\
                                             .filter(AugusTicket.augus_seat_type_code==record.seat_type_code)\
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
                    if stock.stock_type_id == ag_ticket.stock_type.id:
                        break
                else: # 対象となるStockがない
                    raise AugusDataImportError(
                        'AugusTicket not linked to StockType: AugusTicket.id={}, '.format(ag_ticket.id))

                if stock:
                    seat = self.import_record(record, stock, ag_performance)
                    success_records.append(record)
                    allocated_seats.append(seat)
                    seat.save()
        return success_records

    def import_(self, protocol):
        return self.import_record_all(protocol)

    @staticmethod
    def get_augus_seat(ag_venue, area_code, info_code, floor, column, number):
        return AugusSeat.query.filter(AugusSeat.augus_venue_id==ag_venue.id)\
                              .filter(AugusSeat.area_code==area_code)\
                              .filter(AugusSeat.info_code==info_code)\
                              .filter(AugusSeat.floor==floor)\
                              .filter(AugusSeat.column==column)\
                              .filter(AugusSeat.num==number)\
                              .one()

    @staticmethod
    def augus_seat_to_real_seat(ag_performance, ag_seat):
        base_seat = ag_seat.seat
        performance = ag_performance.performance
        venue = Venue.query.filter(Venue.performance_id==performance.id).one()
        seat = Seat.query.filter(Seat.l0_id==base_seat.l0_id)\
                         .filter(Seat.venue_id==venue.id)\
                         .one()
        if seat:
            return seat
        else:
            raise NoSeatError()
