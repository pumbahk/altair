#-*- coding: utf-8 -*-
import os.path
import time
import collections
from abc import ABCMeta, abstractmethod
from zope.interface import Interface, Attribute, implementer
from sqlalchemy.orm.exc import NoResultFound
from pyramid.decorator import reify
from altair.app.ticketing.core.models import Venue, Seat, AugusVenue, AugusSeat


class SeatAugusSeatPairs(object):
    def __init__(self, venue_id):
        self._venue_id = venue_id
        self._seats = []
        self._augus_seats = []

    @property
    def venue_id(self):
        return self._venue_id
        

    def load(self):
        self._seats = Seat.query.filter(Seat.venue_id==self.venue_id)\
                                .order_by(Seat.id)\
                                .all()

        self._augus_seats = AugusSeat.query\
                                     .join(AugusVenue)\
                                     .filter(AugusVenue.id==AugusSeat.augus_venue_id)\
                                     .filter(AugusVenue.venue_id==self.venue_id)\
                                     .order_by(AugusSeat.seat_id)\
                                     .all()

    def next(self):
        return self.__iter__

    def __iter__(self):
        finder = self._find_augus_seat()
        finder.next() # ignore
        for seat in self._seats:
            augus_seat = finder.send(seat)
            yield seat, augus_seat
        finder.close()
        
    def _find_augus_seat(self): # co routine
        length = len(self._augus_seats)
        augus_seat = None
        seat = yield # first generate ignore
        ii = 0
        while ii < length:
            augus_seat = self._augus_seats[ii]
            if augus_seat.seat_id >= seat.id:
                if augus_seat.seat_id != seat.id:
                    augus_seat = None # return None if augus_seat no match
                seat = yield augus_seat
                ii += 1
            else: # augus_seat.seat_id < seat.id
                continue
        while True: # StopIterasion free
            yield None


    def find_pair(self, seat_id):
        for seat, augus_seat in self:
            if seat.id == seat_id:
                return seat, augus_seat
        raise ValueError('Not found pair: seat_id={0}'.format(seat_id))


def _sjis(unistr):
    try:
        return unistr.encode('sjis')
    except (UnicodeEncodeError, UnicodeDecodeError) as err:
        raise err.__class__(repr(unistr), *err.args[1:])

        
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
        ('augus_seat_area_code', lambda ag_seat: getattr(ag_seat, 'area_code', '')),
        ('augus_seat_info_code', lambda ag_seat: getattr(ag_seat, 'info_code', '')),
        ('augus_seat_floor', lambda ag_seat: getattr(ag_seat, 'floor', '')),
        ('augus_seat_column', lambda ag_seat: getattr(ag_seat, 'column', '')),
        ('augus_seat_num', lambda ag_seat: getattr(ag_seat, 'num', '')),
        ))

    def get_ext_entry(self, augus_seat, *args, **kwds):
        return [getter(augus_seat) for getter in self.EXT_HEADER_GETTER.values()]


class AbormalTimestampFormatError(Exception):
    pass


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
        self.seat_id = long(row[0])
        self.augus_venue_code = _long(row[6], '')
        self.augus_seat_area_code = _long(row[7], '')
        self.augus_seat_info_code = _long(row[8], '')
        self.augus_seat_floor = _sjis(row[9])
        self.augus_seat_column = _sjis(row[10])
        self.augus_seat_num = _sjis(row[11])

    def is_enable(self):
        return self.augus_venue_code != ''


class AugusSeatImportError(Exception):
    pass


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
        csvlike.next() # ignore header
        datas = filter(lambda data: data.is_enable(),
                       [EntryData(row) for row in csvlike])
        augus_venue_codes = set([data.augus_venue_code for data in datas])
        augus_venue_code = None
        try:
            augus_venue_code = augus_venue_codes.pop()
        except KeyError:
            AugusSeatImportError('No augus venue codes')
        if augus_venue_codes:
            AugusSeatImportError('mupliple augus venue codes: {0}'.format(
                [augus_venue_code] + list(augus_venue_codes)))

        augus_venue = get_or_create_augus_venue_from_code(augus_venue_code,
                                                          pairs.venue_id)
        for data in datas:
            seat, augus_seat = pairs.find_pair(data.seat_id)

            other_augus_seat = AugusSeat.get(seat_id=seat.id)
            if other_augus_seat and other_augus_seat.id != augus_seat.id: # remove link
                other_augus_seat.seat_id = None
                other_augus_seat.save()
            
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


class ImporterFactory(object):
    @classmethod
    def create(cls, type_):
        return AugusVenueImporter()
