#-*- coding: utf-8 -*-
from altair.app.ticketing.core.models import (
    Seat,
    AugusSeat,
    AugusVenue,
    )

from .errors import (
    NoSeatError,
    BadRequest,
    )
    
class SeatAugusSeatPairs(object):
    def __init__(self):
        self._venue = None
        self._augus_venue = None

    def load(self, venue, augus_venue=None):
        self._venue = venue
        self._augus_venue = augus_venue

    def load_augus_venue(self, augus_venue):
        self.load(augus_venue.venue, augus_venue)

    def get_seats(self):
        return sorted(self._venue.seats, key=lambda seat: seat.id)

    def get_augus_seats(self):
        if self._augus_venue:
            return sorted(self._augus_venue.augus_seats, key=lambda augus_seat: augus_seat.seat_id)
        else:
            return []

    @property
    def venue_id(self):
        return self._venue.id
    
    def find_augus_seat(self, seat):
        for augus_seat in self.get_augus_seats():
            if seat.id == augus_seat.seat_id:
                return augus_seat
        return None

    def next(self):
        return self.__iter__

    def __iter__(self):
        for seat in self.get_seats():
            augus_seat = self.find_augus_seat(seat)
            yield seat, augus_seat
        
    def _find_augus_seat(self): # co routine
        augus_seats = self.get_augus_seats()
        length = len(augus_seats)
        augus_seat = None
        seat = yield # first generate ignore
        ii = 0
        while ii < length:
            augus_seat = augus_seats[ii]
            if augus_seat.seat_id >= seat.id:
                if augus_seat.seat_id != seat.id:
                    augus_seat = None # return None if augus_seat no match
                seat = yield augus_seat
                ii += 1
            else: # augus_seat.seat_id < seat.id
                continue
        while True: # StopIterasion free
            yield None

    def get_seat(self, *args, **kwds):
        seats = [seat for seat in self._find_seat(*args, **kwds)] # raise NoSeatError
        return seats[0]

    def _find_seat(self, seat_id):
        for seat in self.get_seats():
            if seat.id == seat_id:
                yield seat
                break
        else:
            raise NoSeatError('no seat: {0}'.format(seat_id))
                         
    def find_pair(self, seat_id):
        seat = self.get_seat(seat_id)
        augus_seat = self.find_augus_seat(seat)        
        return seat, augus_seat
        
class _SeatAugusSeatPairs(object):
    def __init__(self, venue_id, augus_venue_code, augus_venue_version):
        self._venue_id = venue_id
        self._augus_venue_code = augus_venue_code
        self._augus_venue_version = augus_venue_version
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

    def get_seat(self, *args, **kwds):
        seats = [seat for seat in self._find_seat(*args, **kwds)] # raise NoSeatError
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

class RequestAccessor(object):
    in_params = {}
    in_matchdict = {}
    
    def __init__(self, request):
        self._request = request
        
    def _get_value(self, getter, key, type_=None):
        try:
            value = getter(key)
            if type_:
                value = type_(value)
            return value
        except KeyError as err:
            raise BadRequest('Should input parameter: {0}'.format(key))
        except (TypeError, ValueError) as err:
            raise BadRequest('Illegal type: {0} ({1})'.format(type_, key))
        assert False

    def _get_matchdict(self, key, *args, **kwds):
        getter = lambda _key: self._request.matchdict[_key]
        return self._get_value(getter, key, *args, **kwds)        

    def _get_params(self, key, *args, **kwds):
        getter = lambda _key: self._request.params.getall(_key)
        return self._get_value(getter, key, *args, **kwds)

    def __getattr__(self, name):
        if name in self.in_params:
            type_ = self.in_params[name]
            return self._get_params(name, type_)
        elif name in self.in_matchdict:
            type_ = self.in_matchdict[name]
            return self._get_matchdict(name, type_)
        else:
            raise AttributeError(name)

