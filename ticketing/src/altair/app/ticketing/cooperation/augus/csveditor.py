#-*- coding: utf-8 -*-
import time
import itertools
from altair.app.ticketing.core.models import (
    Seat,
    Stock,
    StockHolder,
    SeatStatusEnum,
    )
from altair.augus.protocols.putback import (
    PutbackResponse,
    PutbackResponseRecord,
    )

import os.path
import time
import itertools
import collections
from abc import ABCMeta, abstractmethod
from zope.interface import Interface, Attribute, implementer
from sqlalchemy.orm.exc import NoResultFound
from pyramid.decorator import reify
from altair.app.ticketing.core.models import (
    Venue,
    Seat,
    AugusVenue,
    AugusSeat,
    AugusPerformance,
    )
from .errors import (
    NoSeatError,
    SeatImportError,
    EntryFormatError,
    AbnormalTimestampFormatError,
    )





def _sjis(unistr):
    try:
        return unistr.encode('sjis')
    except (UnicodeEncodeError, UnicodeDecodeError) as err:
        raise err.__class__(repr(unistr), *err.args[1:])
    except AttributeError as err:
        raise ValueError('The `unistr` should be unicode object: {0}'\
                        .format(repr(unistr)))                        

def _unsjis(msg, default=None):
    try:
        return msg.decode('sjis')
    except (UnicodeEncodeError, UnicodeDecodeError) as err:
        raise err.__class__(repr(msg), *err.args[1:])
    except AttributeError as err:
        raise ValueError('The `msg` should be encoded sjis string object: {0}'\
                         .format(repr(msg)))


class _TableBase(object):
    __metaclass__ = ABCMeta
    
    BASE_HEADER_GETTER = collections.OrderedDict(( # read only property
        ('id', lambda seat: seat.id),
        ('name', lambda seat: _sjis(seat.name)),
        ('seat_no', lambda seat: _sjis(seat.seat_no)),
        ('l0_id', lambda seat: _sjis(seat.l0_id)),
        ('group_l0_id', lambda seat: _sjis(seat.group_l0_id)),
        ('row_l0_id', lambda seat: _sjis(seat.row_l0_id)),
        ))

    EXT_HEADER_GETTER = collections.OrderedDict(( # read only property
        ))

    def get_header(self):
        return self.BASE_HEADER_GETTER.keys() + self.EXT_HEADER_GETTER.keys()

    def get_entry(self, seat, *args, **kwds):
        return self.get_base_entry(seat) + self.get_ext_entry(*args, **kwds)

    def get_base_entry(self, seat):
        return [getter(seat) for getter in self.BASE_HEADER_GETTER.values()]

    @abstractmethod
    def get_ext_entry(self, *args, **kwds): # need override
        return []


class AugusTable(_TableBase):
    EXT_HEADER_GETTER = collections.OrderedDict((
        ('augus_venue_code', lambda ag_seat: getattr(getattr(ag_seat, 'augus_venue', ''), 'code', '')),
        ('augus_venue_name', lambda ag_seat: getattr(getattr(ag_seat, 'augus_venue', ''), 'name', '')),
        ('augus_seat_area_name', lambda ag_seat: getattr(ag_seat, 'area_name', '')),
        ('augus_seat_info_name', lambda ag_seat: getattr(ag_seat, 'info_name', '')),
        ('augus_seat_doorway_name', lambda ag_seat: getattr(ag_seat, 'doorway_name', '')),
        ('augus_seat_priority', lambda ag_seat: getattr(ag_seat, 'priority', '')),
        ('augus_seat_floor', lambda ag_seat: _sjis(getattr(ag_seat, 'floor', ''))),
        ('augus_seat_column', lambda ag_seat: _sjis(getattr(ag_seat, 'column', ''))),
        ('augus_seat_num', lambda ag_seat: _sjis(getattr(ag_seat, 'num', ''))),
        ('augus_seat_block', lambda ag_seat: _sjis(getattr(ag_seat, 'block', ''))),
        ('augus_seat_coordy', lambda ag_seat: _sjis(getattr(ag_seat, 'coordy', ''))),
        ('augus_seat_coordx', lambda ag_seat: _sjis(getattr(ag_seat, 'coordx', ''))),
        ('augus_seat_coordy_whole', lambda ag_seat: _sjis(getattr(ag_seat, 'coordy_whole', ''))),
        ('augus_seat_coordx_whole', lambda ag_seat: _sjis(getattr(ag_seat, 'coordx_whole', ''))),
        ('augus_seat_area_code', lambda ag_seat: getattr(ag_seat, 'area_code', '')),
        ('augus_seat_info_code', lambda ag_seat: getattr(ag_seat, 'info_code', '')),
        ('augus_seat_doorway_code', lambda ag_seat: getattr(ag_seat, 'doorway_code', '')),
        ('augus_venue_version', lambda ag_seat: getattr(getattr(ag_seat, 'augus_venue', ''), 'version', '')),        
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
        except TypeError as err:
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
    except ValueError as err:
        if default is None:
            raise
        else:
            return default

class EntryData(object):
    def __init__(self, row):
        try:
            self.seat_id = long(row[0])
            self.augus_venue_code = _long(row[6], '')
            self.augus_venue_name = _unsjis(row[7], '')
            self.augus_seat_area_name = _unsjis(row[8], '')
            self.augus_seat_info_name = _unsjis(row[9], '')
            self.augus_seat_doorway_name = _unsjis(row[10], '')
            self.augus_seat_priority = _long(row[11], '')
            self.augus_seat_floor = _unsjis(row[12])
            self.augus_seat_column = _unsjis(row[13])
            self.augus_seat_num = _unsjis(row[14])
            self.augus_seat_block = _long(row[15], '')
            self.augus_seat_coordy = _long(row[16], '')
            self.augus_seat_coordx = _long(row[17], '')
            self.augus_seat_coordy_whole = _long(row[18], '')
            self.augus_seat_coordx_whole = _long(row[19], '')            
            self.augus_seat_area_code = _long(row[20], '')
            self.augus_seat_info_code = _long(row[21], '')
            self.augus_seat_doorway_code = _long(row[22], '')
            self.augus_venue_version = _long(row[23], '')
            
        except (ValueError, TypeError, IndexError,
                UnicodeDecodeError, UnicodeEncodeError) as err:
            raise EntryFormatError('Illegal format entry: {0}: {1}'\
                                   .format(repr(row), repr(err)))

    def is_enable(self):
        return self.augus_venue_code != ''


def get_or_create_augus_venue_from_code(code, version, name=u'', venue_id=None):
    augus_venue = AugusVenue.get(code=code, version=version)
    if augus_venue is None:
        augus_venue = AugusVenue()
        augus_venue.name = name
        augus_venue.version = version
        augus_venue.code = code
        augus_venue.venue_id = venue_id
        augus_venue.save()
    elif augus_venue.venue_id != venue_id:
        augus_venue.venue_id = venue_id
        augus_venue.save()        
    return AugusVenue.get(code=code, venue_id=venue_id, version=version)

class AugusVenueImporter(object):

    def import_(self, csvlike, pairs):
        csvlike.next() # ignore header
        datas = [EntryData(row) for row in csvlike] # raise EntryFormatError
        code_version_name = set([(data.augus_venue_code, data.augus_venue_version, data.augus_venue_name)
                                 for data in datas if data.augus_venue_code != ''])
        try:
            code, version, name = code_version_name.pop()
        except KeyError:
            raise SeatImportError('No augus venue codes')
        if code_version_name:
            raise SeatImportError('mupliple augus venue codes: {0}'.format(
                [(code, version, name)] + list(code_version_name)))

        augus_venue = get_or_create_augus_venue_from_code(code, version, name,
                                                          pairs.venue_id,
                                                          )

        for data in datas:
            seat, augus_seat = pairs.find_pair(data.seat_id)
            other_augus_seat = AugusSeat.get(seat_id=seat.id, augus_venue_id=augus_venue.id)
            if data.is_enable():
                # remove link
                if other_augus_seat and other_augus_seat.id != augus_seat.id:
                    other_augus_seat.seat_id = Nonen
                    other_augus_seat.save()
                
                # make link
                if augus_seat is None:
                    augus_seat = AugusSeat()
                augus_seat.augus_venue_id = augus_venue.id
                augus_seat.area_name = data.augus_seat_area_name
                augus_seat.info_name = data.augus_seat_info_name
                augus_seat.doorway_name = data.augus_seat_doorway_name
                augus_seat.priority = data.augus_seat_priority
                augus_seat.floor = data.augus_seat_floor
                augus_seat.column = data.augus_seat_column
                augus_seat.num = data.augus_seat_num
                augus_seat.block = data.augus_seat_block
                augus_seat.coordy = data.augus_seat_coordy
                augus_seat.coordy_whole = data.augus_seat_coordy_whole
                augus_seat.coordx = data.augus_seat_coordx
                augus_seat.coordx_whole = data.augus_seat_coordx_whole
                augus_seat.area_code = data.augus_seat_area_code
                augus_seat.info_code = data.augus_seat_info_code
                augus_seat.doorway_code = data.augus_seat_doorway_code
                augus_seat.version = data.augus_venue_version
                augus_seat.seat_id = seat.id
                augus_seat.save()
            elif augus_seat:
                # remove link
                augus_seat.seat_id = None
                augus_seat.save()
        return augus_venue

class ImporterFactory(object):
    @classmethod
    def create(cls, type_):
        return AugusVenueImporter()


class AugusPerformanceImpoter(object):
    def import_(self, csvlike):
        csvlike.next() # ignore header
        for row in csvlike:
            augus_event_code = int(row[0])
            augus_performance_code = int(row[1])
            ag_performance = AugusPerformance.get(code=augus_performance_code)
            if not ag_performance:
                ag_performance = AugusPerformance()
                ag_performance.code = augus_performance_code
                ag_performance.augus_event_code = augus_event_code
                ag_performance.save()
            else: # already exist
                pass
class CannotPutbackTicket(Exception):
    pass

def putback(stock_holder):

    if type(stock_holder) in (int, long):
        stock_holder = StockHolder.query\
                                  .filter(StockHolder.id==stock_holder)\
                                  .one()
    seats = Seat.query.filter(Seat.stock_id==Stock.id)\
                      .filter(Stock.stock_holder_id==stock_holder.id)\
                      .order_by(Stock.performance_id)

    can_putback_statuses = (SeatStatusEnum.NotOnSales,
                            SeatStatusEnum.Vacant,
                            )

    putback_code = unicode(time.strftime('%Y-%m-%d-%H-%M-%S'))
    for performance_id, seat_in_performance in itertools.groupby(seats, key=lambda seat: seat.stock.performance_id):
        unallocation_stock = Stock.query.filter(Stock.performance_id==performance_id)\
                                        .filter(Stock.stock_holder_id==None)\
                                        .one()
        ag_performance = AugusPerformance\
            .query\
            .filter(AugusPerformance.performance_id==performance_id)\
            .one()
        ag_venue = AugusVenue.query.filter(AugusVenue.code==ag_performance.augus_venue_code)\
                                   .filter(AugusVenue.version==ag_performance.augus_venue_version)\
                                   .one()
        for seat in sesat_in_performance:
            if seat.status not in can_putback_statuses:
                raise CannnotPutbackTicket()
            ag_seat = AugusSeat.query.filter(AugusSeat.augus_venue_id==AugusVenue.id)\
                                     .filter(AugusSeat.seat_id==Seat.id)\
                                     .filter(Seat.l0_id==seat.l0_id)\
                                     .one()
            ag_stock_info = AugusStockInfo.query\
                                          .filter(AugusStockInfo.augus_performance_id==ag_performance.id)\
                                          .filter(AugusStockInfo.augus_seat_id==ag_seat.id)\
                                          .one()
            ag_putback = AugusPutback()
            ag_putback.augus_putback_code = putback_code
            ag_putback.quantity = 1 # 指定席は1
            ag_putback.augus_stock_info_id = ag_stock_info.id

            seat.stock_id = unallocation_stock.id

            seat.save()
            ag_putback.save()
    return putback_code

