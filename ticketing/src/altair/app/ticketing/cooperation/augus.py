#-*- coding: utf-8 -*-
import os.path
import time
import collections
from abc import ABCMeta, abstractmethod
from zope.interface import Interface, Attribute, implementer
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
            augus_seat = self._augus_seat[ii]
            if augus_seat.seat_id >= seat.id:
                if augus_seat.seat_id != seat.id:
                    augus_seat = None # return None if augus_seat no match
                seat = yield augus_seat
                ii += 1
            else: # augus_seat.seat_id < seat.id
                continue
        while True: # StopIterasion free
            yield None

class _TableBase(object):
    __metaclass__ = ABCMeta
    
    BASE_HEADER_GETTER = collections.OrderedDict(( # read only property
        ('id', lambda seat: seat.id),
        ('seat_no', lambda seat: seat.seat_no),
        ('l0_id', lambda seat: seat.l0_id),
        ('group_l0_id', lambda seat: seat.group_l0_id),
        ('row_l0_id', lambda seat: seat.row_l0_id),
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
        ('augus_seat_area_code', lambda ag_seat: getattr(ag_seat, 'area_code', '')),
        ('augus_seat_info_code', lambda ag_seat: getattr(ag_seat, 'info_code', '')),
        ('augus_seat_floor_code', lambda ag_seat: getattr(ag_seat, 'foor_code', '')),
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
