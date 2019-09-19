#-*- coding: utf-8 -*-
import os
import time
import itertools
import collections
from abc import ABCMeta, abstractmethod
from pyramid.decorator import reify
from altair.app.ticketing.core.models import (
    Seat,
    Stock,
    StockHolder,
    SeatStatusEnum,
    AugusVenue,
    AugusSeat,
    AugusPerformance,
    AugusStockInfo,
    AugusPutback,
    )


class AugusError(Exception):
    pass


class NoSeatError(AugusError):
    pass


class AbnormalTimestampFormatError(AugusError):
    pass


class EntryFormatError(AugusError):
    pass


class SeatImportError(AugusError):
    pass


class CannotPutbackTicket(Exception):
    pass


class SeatAugusSeatPairs(object):
    def __init__(self, venue_id):
        self._venue_id = venue_id
        self._seats = []
        self._augus_seats = []

    @property
    def venue_id(self):
        return self._venue_id

    def load(self):
        self._seats = Seat.query.filter(Seat.venue_id == self.venue_id)\
            .order_by(Seat.id)\
            .all()

        self._augus_seats = AugusSeat.query\
            .join(AugusVenue)\
            .filter(AugusVenue.id == AugusSeat.augus_venue_id)\
            .filter(AugusVenue.venue_id == self.venue_id)\
            .order_by(AugusSeat.seat_id)\
            .all()

    def find_augus_seat(self, seat):
        for augus_seat in self._augus_seats:
            if seat.id == augus_seat.seat_id:
                return augus_seat
        return None

    def next(self):
        return self.__iter__

    def __iter__(self):
        for seat in self._seats:
            augus_seat = self.find_augus_seat(seat)
            yield seat, augus_seat

    def ___iter__(self):
        finder = self._find_augus_seat()
        finder.next()  # ignore
        for seat in self._seats:
            augus_seat = finder.send(seat)
            yield seat, augus_seat
        finder.close()

    def _find_augus_seat(self):  # co routine
        length = len(self._augus_seats)
        augus_seat = None
        seat = yield  # first generate ignore
        ii = 0
        while ii < length:
            augus_seat = self._augus_seats[ii]
            if augus_seat.seat_id >= seat.id:
                if augus_seat.seat_id != seat.id:
                    augus_seat = None  # return None if augus_seat no match
                seat = yield augus_seat
                ii += 1
            else:  # augus_seat.seat_id < seat.id
                continue
        while True:  # StopIterasion free
            yield None

    def get_seat(self, *args, **kwds):
        seats = [seat for seat in self._find_seat(*args, **kwds)]  # raise NoSeatError
        return seats[0]

    def _find_seat(self, seat_id):
        for seat in self._seats:
            if seat.id == seat_id:
                yield seat
                break
        else:
            raise NoSeatError('no seat: {0}'.format(seat_id))

    def find_pair(self, seat_id):
        seat = self.get_seat(seat_id)
        augus_seat = self.find_augus_seat(seat)
        return seat, augus_seat


def _sjis(unistr):
    try:
        return unistr.encode('sjis')
    except (UnicodeEncodeError, UnicodeDecodeError) as err:
        raise err.__class__(repr(unistr), *err.args[1:])
    except AttributeError as err:
        raise ValueError('The `unistr` should be unicode object: {0}'.format(repr(unistr)))


def _unsjis(msg):
    try:
        return msg.decode('sjis')
    except (UnicodeEncodeError, UnicodeDecodeError) as err:
        raise err.__class__(repr(msg), *err.args[1:])
    except AttributeError as err:
        raise ValueError('The `msg` should be encoded sjis string object: {0}'.format(repr(msg)))


class _TableBase(object):
    __metaclass__ = ABCMeta

    BASE_HEADER_GETTER = collections.OrderedDict((  # read only property
        ('id', lambda seat: seat.id),
        ('name', lambda seat: _sjis(seat.name)),
        ('seat_no', lambda seat: _sjis(seat.seat_no)),
        ('l0_id', lambda seat: _sjis(seat.l0_id)),
        ('group_l0_id', lambda seat: _sjis(seat.group_l0_id)),
        ('row_l0_id', lambda seat: _sjis(seat.row_l0_id)),
        ))

    EXT_HEADER_GETTER = collections.OrderedDict((  # read only property
        ))

    def get_header(self):
        return self.BASE_HEADER_GETTER.keys() + self.EXT_HEADER_GETTER.keys()

    def get_entry(self, seat, *args, **kwds):
        return self.get_base_entry(seat) + self.get_ext_entry(*args, **kwds)

    def get_base_entry(self, seat):
        return [getter(seat) for getter in self.BASE_HEADER_GETTER.values()]

    @abstractmethod
    def get_ext_entry(self, *args, **kwds):  # need override
        return []


class AugusTable(_TableBase):
    EXT_HEADER_GETTER = collections.OrderedDict((
        ('augus_venue_code', lambda ag_seat: getattr(getattr(ag_seat, 'augus_venue', ''), 'code', '')),
        ('augus_seat_area_code', lambda ag_seat: getattr(ag_seat, 'area_code', '')),
        ('augus_seat_info_code', lambda ag_seat: getattr(ag_seat, 'info_code', '')),
        ('augus_seat_floor', lambda ag_seat: _sjis(getattr(ag_seat, 'floor', ''))),
        ('augus_seat_column', lambda ag_seat: _sjis(getattr(ag_seat, 'column', ''))),
        ('augus_seat_num', lambda ag_seat: _sjis(getattr(ag_seat, 'num', ''))),
        ))

    def get_ext_entry(self, augus_seat, *args, **kwds):
        return [getter(augus_seat) for getter in self.EXT_HEADER_GETTER.values()]


class _CSVEditorBase(object):
    __metaclass__ = ABCMeta

    NAME = 'cooperation.csv'
    TIMESTAMP_FORMAT = '-%Y%m%d%H%M%S'

    @reify
    def name(self, name=None, timestamp=False, fmt=None):
        fmt = fmt if fmt is not None else self.TIMESTAMP_FORMAT
        filename = name if name is not None else self.NAME
        stamp = ''
        try:
            stamp = time.strftime(fmt)
        except TypeError:
            raise AbnormalTimestampFormatError(
                'Illigal timestamp format: {0}'.format(repr(fmt)))
        name, ext = os.path.splitext(filename)
        filename = name + stamp + ext
        return filename

    @abstractmethod
    def write(self, csvlike, pairs):
        pass


class AugusCSVEditor(_CSVEditorBase):
    _table = AugusTable

    def write(self, csvlike, pairs):
        table = self._table()
        header = table.get_header()
        csvlike.writerow(header)

        for seat, external_seat in pairs:
            entry = table.get_entry(seat, external_seat)
            csvlike.writerow(entry)


class CSVEditorFactory(object):
    @classmethod
    def create(cls, type_):
        return AugusCSVEditor()


def _long(word, default=None):
    try:
        return long(word)
    except ValueError:
        if default is None:
            raise
        else:
            return default


class EntryData(object):
    def __init__(self, row):
        try:
            self.seat_id = long(row[0])
            self.augus_venue_code = _long(row[6], '')
            self.augus_seat_area_code = _long(row[7], '')
            self.augus_seat_info_code = _long(row[8], '')
            self.augus_seat_floor = _unsjis(row[9])
            self.augus_seat_column = _unsjis(row[10])
            self.augus_seat_num = _unsjis(row[11])
        except (ValueError, TypeError, IndexError,
                UnicodeDecodeError, UnicodeEncodeError) as err:
            raise EntryFormatError('Illegal format entry: {0}: {1}'.format(repr(row), repr(err)))

    def is_enable(self):
        return self.augus_venue_code != ''


def get_or_create_augus_venue_from_code(code, venue_id):
    augus_venue = AugusVenue.get(code=code)
    if augus_venue is None:
        augus_venue = AugusVenue()
        augus_venue.code = code
        augus_venue.venue_id = venue_id
        augus_venue.save()
    elif augus_venue.venue_id != venue_id:
        augus_venue.venue_id = venue_id
        augus_venue.save()
    return AugusVenue.get(code=code)


class AugusVenueImporter(object):
    def import_(self, csvlike, pairs):
        csvlike.next()  # ignore header
        datas = [EntryData(row) for row in csvlike]  # raise EntryFormatError
        augus_venue_codes = set([data.augus_venue_code
                                 for data in datas if data.augus_venue_code != ''])
        augus_venue_code = None
        try:
            augus_venue_code = augus_venue_codes.pop()
        except KeyError:
            raise SeatImportError('No augus venue codes')
        if augus_venue_codes:
            raise SeatImportError('mupliple augus venue codes: {0}'.format(
                [augus_venue_code] + list(augus_venue_codes)))

        augus_venue = get_or_create_augus_venue_from_code(augus_venue_code,
                                                          pairs.venue_id)
        for data in datas:
            seat, augus_seat = pairs.find_pair(data.seat_id)
            other_augus_seat = AugusSeat.get(seat_id=seat.id)

            if data.is_enable():
                # remove link
                if other_augus_seat and other_augus_seat.id != augus_seat.id:
                    other_augus_seat.seat_id = None
                    other_augus_seat.save()
                # make link
                if augus_seat is None:
                    augus_seat = AugusSeat()
                augus_seat.augus_venue_id = augus_venue.id
                augus_seat.area_code = data.augus_seat_area_code
                augus_seat.info_code = data.augus_seat_info_code
                augus_seat.floor = data.augus_seat_floor
                augus_seat.column = data.augus_seat_column
                augus_seat.num = data.augus_seat_num
                augus_seat.seat_id = seat.id
                augus_seat.save()
            elif augus_seat:
                # remove link
                augus_seat.seat_id = None
                augus_seat.save()


class ImporterFactory(object):
    @classmethod
    def create(cls, type_):
        return AugusVenueImporter()


class AugusPerformanceImpoter(object):
    def import_(self, csvlike):
        csvlike.next()  # ignore header
        for row in csvlike:
            augus_event_code = int(row[0])
            augus_performance_code = int(row[1])
            ag_performance = AugusPerformance.get(code=augus_performance_code)
            if not ag_performance:
                ag_performance = AugusPerformance()
                ag_performance.code = augus_performance_code
                ag_performance.augus_event_code = augus_event_code
                ag_performance.save()
            else:  # already exist
                pass


def putback(stock_holder):
    if type(stock_holder) in (int, long):
        stock_holder = StockHolder.query\
            .filter(StockHolder.id == stock_holder)\
            .one()
    seats = Seat.query.filter(Seat.stock_id == Stock.id)\
        .filter(Stock.stock_holder_id == stock_holder.id)\
        .order_by(Stock.performance_id)

    can_putback_statuses = (SeatStatusEnum.NotOnSales,
                            SeatStatusEnum.Vacant,
                            )

    putback_code = unicode(time.strftime('%Y-%m-%d-%H-%M-%S'))
    for performance_id, seat_in_performance in itertools.groupby(seats, key=lambda seat: seat.stock.performance_id):
        unallocation_stock = Stock.query.filter(Stock.performance_id == performance_id)\
            .filter(Stock.stock_holder_id is None)\
            .one()
        ag_performance = AugusPerformance\
            .query\
            .filter(AugusPerformance.performance_id == performance_id)\
            .one()
        ag_venue = AugusVenue.query.filter(AugusVenue.code == ag_performance.augus_venue_code)\
                                   .filter(AugusVenue.version == ag_performance.augus_venue_version)\
                                   .filter(AugusVenue.augus_account_id == ag_performance.augus_account_id)\
                                   .one()

        for seat in seat_in_performance:
            if seat.status not in can_putback_statuses:
                raise CannotPutbackTicket()
            ag_seat = AugusSeat.query.filter(AugusSeat.augus_venue_id == AugusVenue.id)\
                                     .filter(AugusSeat.seat_id == Seat.id)\
                                     .filter(Seat.l0_id == seat.l0_id)\
                                     .one()
            ag_stock_info = AugusStockInfo.query\
                                          .filter(AugusStockInfo.augus_performance_id == ag_performance.id)\
                                          .filter(AugusStockInfo.augus_seat_id == ag_seat.id)\
                                          .one()
            ag_putback = AugusPutback()
            ag_putback.augus_putback_code = putback_code
            ag_putback.quantity = 1  # 指定席は1
            ag_putback.augus_stock_info_id = ag_stock_info.id

            seat.stock_id = unallocation_stock.id

            seat.save()
            ag_putback.save()
    return putback_code
