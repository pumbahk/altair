#-*- coding: utf-8 -*-
import datetime
import itertools
from sqlalchemy.orm.exc import (
    MultipleResultsFound,
    NoResultFound,
    )
from altair.app.ticketing.core.models import (
    Event,
    Performance,
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
            ag_performance = ag_ticket.ag_performance
        ag_ticket.augus_venue_code = record.venue_code
        ag_ticket.seat_type_code = record.seat_type_code
        ag_ticket.seat_type_name = record.seat_type_name
        ag_ticket.unit_value_name = record.unit_value_name
        ag_ticket.augus_seat_type_classif = record.seat_type_classif
        ag_ticket.avlue = record.value
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


class AugusDistributionImpoter(object):
    def import_record(self, record, stock, ag_performance):
        ag_seat = ge_augus_seat(ag_venue=ag_performance.augus_venue,
                                area_code=record.area_code,
                                info_code=record.info_code,
                                floor=record.floor,
                                column=record.column,
                                number=record.number,
                                )
        seat = augus_seat_to_real_seat(ag_performance, ag_seat)
        old_stock = seat.stock

        if old_stock.stock_holder == None and seat.status not in [SeatStatusEnum.NotOnSale.v, SeatStatusEnum.Vacant.v]:
            # 未割当 かつ 配席可能な状態

            # AugusStockInfo生成
            ag_stock_info = AugusStockInfo()
            ag_stock_info.augus_performance_id = ag_performance.id
            ag_stock_info.augus_distribution_code = record.distribution_code
            ag_stock_info.seat_type_classif = record.seat_type_classif
            ag_stock_info.distributed_at = datetime.datetime.now()
            ag_stock_info.augus_seat_id = ag_seat.id
            ag_stock_info.save()

            # seat の割当
            seat.stock_id = stock.id
            old_stock.quantity -= 1
            seat.save()

            return seat
        else:
            raise AugusDataImportError('Cannot seat allocation: seat_id={}'.format(seat.id))

    def _create_stock_holder(self, event):
        stock_holder = StockHolder()
        stock_holder.name = u'オーガス連携:' + time.strftime('%Y-%m-%d-%H-%M-%S')
        stock_holder.event_id = event.id
        stock_holder.stype = u'{"text": "\u8ffd", "text_color": "#a62020"}'
        stock_holder.save()
        return stock_holder

    def import_record_all(self, records):
        allcated_seats = []
        for augus_event_code, _records in itertools.groupby(records, lambda record: record.augus_event_code):
            ag_performance = AugusPerformance\
                .query.filter(AugusPerformance.augus_event_code==augus_event_code)\
                      .first()
            if not ag_performance:
                raise AugusDataImportError(
                    'AugusPerformance not found: event_code={}'.format(
                        record.event_code))
            if not  ag_performance.performance:
                raise AugusDataImportError(
                    'AugusPerformance not linked to Performance: AugusPerformance.id={}, '.format(
                        ag_performance.id))
            stock_holder = self._create_stock_holder(ag_performance.performance.event)
            stocks = filter(lambda stock: stock.performance_id==ag_performance.performance.id, stock_holder.stocks)

            for augus_performance_code, _n_records in itertools.groupby(_records, lambda record: record.performance_code):
                ag_performance = AugusPerformance.get(augus_event_code=augus_event_code,
                                                      augus_performance_code=augus_performance_code,
                                                      )
                if not  ag_performance:
                    raise AugusDataImportError(
                        'AugusPerformance not found: event_code={} performance_code={}'.format(
                            augus_event_code, augus_performance_code))

                if not  ag_performance.performance:
                    raise AugusDataImportError(
                        'AugusPerformance not linked to Performance: AugusPerformance.id={}, '.format(
                            ag_performance.id))

                for augus_seat_type_code, _p_records in itertools.groupby(_n_records, lambda record: record.seat_type_code):
                    ag_ticket = None
                    try:
                        ag_ticket = AugusTicket.query.filter(AugusTicket.augus_performance_id==ag_performance.performance.id)\
                                                     .filter(AugusTicket.augus_seat_type_code==augus_seat_type_code)\
                                                     .one()
                    except:
                        raise
                    if not ag_ticket.stock_type:
                        raise AugusDataImportError(
                            'AugusTicket not linked to StockType: AugusTicket.id={}, '.format(
                                ag_ticket.id))

                    stock = None
                    for stock in stocks:
                        if stock.stock_type_id == ag_ticket.stock_type.id:
                            break
                    else:
                        raise AugusDataImportError(
                            'AugusTicket not linked to StockType: AugusTicket.id={}, '.format(
                                ag_ticket.id))

                    for record in _p_records:
                        seat = self.import_record(record, stock, ag_performance)
                        allocated_seats.append(seat)
                    if stock:
                        stock.save()
        return allocated_seats

    def import_(self, protocol):
        return self.import_record_all(protocol)

    @staticmethod
    def get_augus_seat(ag_venue, area_code, info_code, floor, column, number):
        return AugusSeat.query.filter(AugusSeat.augus_venue_id==ag_venue.id)\
                              .filter(AugusSeat.area_code==area_code)\
                              .filter(AugusSeat.info_code==info_code)\
                              .filter(AugusSeat.floor==floor)\
                              .filter(AugusSeat.column==column)\
                              .filter(AugusSeat.number==number)\
                              .one()

    @staticmethod
    def augus_seat_to_real_seat(ag_performance, ag_seat):
        base_seat = ag_seat.seat
        performance = ag_performance.performance
        seat = Seat.get(l0_id=base_seat.l0_id,
                        venue_id=performance.venue_id,
                        )
        if seat:
            return seat
        else:
            raise NoSeatError()
