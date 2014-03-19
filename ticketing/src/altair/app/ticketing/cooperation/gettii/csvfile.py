#-*- coding: utf-8 -*-
import collections
from altair.app.ticketing.core.models import (
    Venue,
    GettiiVenue,
    )

from ..utils import (
    RawType,
    UnicodeType,
    IntegerType,
    DateTimeType,
    Record,
    CSVData,
    )




class AltairGettiiVenueCSVRecord(Record):
    fields = collections.OrderedDict(
        [('id_', IntegerType),
         ('name', UnicodeType),
         ('seat_no', UnicodeType),
         ('l0_id', UnicodeType),
         ('group_l0_id', UnicodeType),
         ('row_l0_id', UnicodeType),
         ('gettii_venue_code', UnicodeType),
         ('gettii_l0_id', UnicodeType),
         ('gettii_coodx', UnicodeType),
         ('gettii_coody', UnicodeType),
         ('gettii_posx', UnicodeType),
         ('gettii_posy', UnicodeType),
         ('gettii_angle', UnicodeType),
         ('gettii_floor', UnicodeType),
         ('gettii_column', UnicodeType),
         ('gettii_num', UnicodeType),
         ('gettii_block', UnicodeType),
         ('gettii_gate', UnicodeType),
         ('gettii_priority', UnicodeType),
         ('gettii_area_code', UnicodeType),
         ('gettii_priority_block', UnicodeType),
         ('gettii_priority_seat', UnicodeType),
         ('gettii_seat_flag', UnicodeType),
         ('gettii_seat_classif', UnicodeType),
         ('gettii_net_block', UnicodeType),
         ('gettii_modifier', UnicodeType),
         ('gettii_modified_at', DateTimeType),
         ])

    def load(self, seat, gettii_seat):
        self.id_ = seat.id
        self.name = seat.name
        self.seat_no = seat.seat_no
        self.l0_id = seat.l0_id
        self.group_l0_id = seat.group_l0_id
        self.row_l0_id = seat.row_l0_id
        if gettii_seat:
            self.gettii_venue_code = gettii_seat.gettii_venue.code
            self.gettii_l0_id = gettii_seat.l0_id
            self.gettii_coodx = gettii_seat.coodx
            self.gettii_coody = gettii_seat.coody
            self.gettii_posx = gettii_seat.posx
            self.gettii_posy = gettii_seat.posy
            self.gettii_angle = gettii_seat.angle
            self.gettii_floor = gettii_seat.floor
            self.gettii_column = gettii_seat.column
            self.gettii_num = gettii_seat.num
            self.gettii_block = gettii_seat.block
            self.gettii_gate = gettii_seat.gate
            self.gettii_priority = gettii_seat.priority
            self.gettii_area_code = gettii_seat.area_code
            self.gettii_priority_block = gettii_seat.priority_block
            self.gettii_priority_seat = gettii_seat.priority_seat
            self.gettii_seat_flag = gettii_seat.seat_flag
            self.gettii_seat_classif = gettii_seat.seat_classif
            self.gettii_net_block = gettii_seat.net_block
            self.gettii_modifier = gettii_seat.modifier
            self.gettii_modified_at = gettii_seat.modified_at
        else:
            self.gettii_venue_code = ''
            self.gettii_l0_id = ''
            self.gettii_coodx = ''
            self.gettii_coody = ''
            self.gettii_posx = ''
            self.gettii_posy = ''
            self.gettii_angle = ''
            self.gettii_floor = ''
            self.gettii_column = ''
            self.gettii_num = ''
            self.gettii_block = ''
            self.gettii_gate = ''
            self.gettii_priority = ''
            self.gettii_area_code = ''
            self.gettii_priority_block = ''
            self.gettii_priority_seat = ''
            self.gettii_seat_flag = ''
            self.gettii_seat_classif = ''
            self.gettii_net_block = ''
            self.gettii_modifier = ''
            self.gettii_modified_at = ''

    def validate(self):
        return bool(self.id_)


class AltairGettiiVenueCSV(CSVData):
    record_factory = AltairGettiiVenueCSVRecord

    def load(self, venue):
        gettii_venue = GettiiVenue\
            .query.filter(GettiiVenue.venue_id==venue.id).first()
        id_gettii_seat = {}
        if gettii_venue:
            id_gettii_seat = dict([(gettii_seat.seat_id, gettii_seat)
                                   for gettii_seat in gettii_venue.gettii_seats])

        for seat in venue.seats:
            gettii_seat = id_gettii_seat.get(seat.id, None)
            record = self.record_factory()
            record.load(seat, gettii_seat)
            if record.validate():
                self.append(record)
            else:
                print '????'


class GettiiSeatCSVRecord(Record):
    fields = collections.OrderedDict(
        [('customer_code', IntegerType),
         ('performance_code', UnicodeType),
         ('performance_name', UnicodeType),
         ('performance_nick_name', UnicodeType),
         ('start_day', UnicodeType),
         ('stage_code', UnicodeType),
         ('start_time', UnicodeType),
         ('venue_code', UnicodeType),
         ('l0_id', UnicodeType),
         ])

    def load(self, seat, gettii_seat):
        self.id_ = seat.id
        self.name = seat.name
        self.seat_no = seat.seat_no
        self.l0_id = seat.l0_id
        self.group_l0_id = seat.group_l0_id
        self.row_l0_id = seat.row_l0_id
        if gettii_seat:
            self.gettii_venue_code = gettii_seat.venue_code
            self.gettii_l0_id = gettii_seat.l0_id
            self.gettii_coodx = gettii_seat.coodx
            self.gettii_coody = gettii_seat.coody
            self.gettii_posx = gettii_seat.posx
            self.gettii_posy = gettii_seat.posy
            self.gettii_angle = gettii_seat.angle
            self.gettii_floor = gettii_seat.floor
            self.gettii_column = gettii_seat.column
            self.gettii_num = gettii_seat.num
            self.gettii_block = gettii_seat.block
            self.gettii_gate = gettii_seat.gate
            self.gettii_priority = gettii_seat.priority
            self.gettii_area_code = gettii_seat.area_code
            self.gettii_priority_block = gettii_seat.priority_block
            self.gettii_priority_seat = gettii_seat.priority_seat
            self.gettii_seat_flag = gettii_seat.seat_flag
            self.gettii_seat_classif = gettii_seat.seat_classif
            self.gettii_net_block = gettii_seat.net_block
            self.gettii_modifier = gettii_seat.modifier
            self.gettii_modified_at = gettii_seat.modified_at
        else:
            self.gettii_venue_code = ''
            self.gettii_l0_id = ''
            self.gettii_coodx = ''
            self.gettii_coody = ''
            self.gettii_posx = ''
            self.gettii_posy = ''
            self.gettii_angle = ''
            self.gettii_floor = ''
            self.gettii_column = ''
            self.gettii_num = ''
            self.gettii_block = ''
            self.gettii_gate = ''
            self.gettii_priority = ''
            self.gettii_area_code = ''
            self.gettii_priority_block = ''
            self.gettii_priority_seat = ''
            self.gettii_seat_flag = ''
            self.gettii_seat_classif = ''
            self.gettii_net_block = ''
            self.gettii_modifier = ''
            self.gettii_modified_at = ''

    def validate(self):
        return bool(self.id_)


class GettiiSeatCSV(CSVData):
    record_factory = GettiiSeatCSVRecord

    def load(self, venue):
        gettii_venue = GettiiVenue\
            .query.filter(GettiiVenue.venue_id==venue.id).first()
        id_gettii_seat = {}
        if gettii_venue:
            id_gettii_seat = dict([(gettii_seat.seat_id, gettii_seat)
                                   for gettii_seat in gettii_venue.gettii_seats])

        for seat in venue.seats:
            gettii_seat = id_gettii_seat.get(seat.id, None)
            record = self.record_factory()
            record.load(seat, gettii_seat)
            if record.validate():
                self.append(record)
            else:
                print '????'
