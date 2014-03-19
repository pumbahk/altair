#-*- coding: utf-8 -*-
from sqlalchemy.orm.exc import (
    MultipleResultsFound,
    NoResultFound,
    )

from altair.app.ticketing.core.models import (
    GettiiVenue,
    GettiiSeat,
    Venue,
    Seat,
    )

class GettiiVenueImportError(Exception):
    pass

def get_or_create_gettii_venue(code, venue_id):
    """
    GVが複数ある -> エラー
    GVがある venue_idが一致 -> 更新
    GVがある venue_idが不一致 -> エラー
    GVがない venue_idをもったGVが存在 -> エラー
    GVがない venue_idをもったGVが存在しない -> 新規作成

    """
    gettii_venue = None
    try:
        gettii_venue = GettiiVenue.query.filter(GettiiVenue.code==code).one()
        if gettii_venue.venue_id is None:
            gettii_venue.venue_id = venue_id
        elif gettii_venue.venue_id != venue_id:
            raise GettiiVenueImportError('code={}, venue_id={}'.format(code, venue_id))
    except NoResultFound:
        other_gettii_venue = GettiiVenue.query.filter(GettiiVenue.code!=code)\
                                              .filter(GettiiVenue.venue_id==venue_id)\
                                              .all()
        if other_gettii_venue:
            raise GettiiVenueImportError('code={}, venue_id={}'.format(code, venue_id))
        else:
            gettii_venue = GettiiVenue()
            gettii_venue.venue_id = venue_id
            gettii_venue.code = code
    except MultipleResultsFound:
        raise GettiiVenueImportError('code={}, venue_id={}'.format(code, venue_id))
    return gettii_venue

def get_or_create_gettii_seat(external_venue, external_l0_id):
    try:
        external_seat = GettiiSeat.query.filter(GettiiSeat.gettii_venue_id==external_venue.id)\
                                        .filter(GettiiSeat.l0_id==external_l0_id)\
                                        .one()
    except NoResultFound:
        external_seat = GettiiSeat()
        external_seat.gettii_venue_id = external_venue.id
        external_seat.l0_id = external_l0_id
    return external_seat


class GettiiVenueImpoter(object):
    def import_record(self, venue_id, record):
        if not record.gettii_venue_code:
            return
        gettii_venue = get_or_create_gettii_venue(record.gettii_venue_code, venue_id)
        gettii_venue.save()
        try:
            seat = Seat.query.filter(Seat.id==record.id_).one()
        except NoResultFound:
            raise GettiiVenueImportError('Seat not found: Seat.id={}'.format(record.id_))

        if seat.venue_id != venue_id:
            raise GettiiVenueImportError('Venue id mistmatch: Venue.id{} != Seat.venue_id={}'.format(
                venue_id, seat.venue_id))

        if record.gettii_venue_code and record.gettii_l0_id:
            gettii_seat = get_or_create_gettii_seat(gettii_venue, record.gettii_l0_id)
            gettii_seat.l0_id = record.gettii_l0_id
            gettii_seat.coodx = record.gettii_coodx
            gettii_seat.coody = record.gettii_coody
            gettii_seat.posx = record.gettii_posx
            gettii_seat.posy = record.gettii_posy
            gettii_seat.angle = record.gettii_angle
            gettii_seat.floor = record.gettii_floor
            gettii_seat.column = record.gettii_column
            gettii_seat.num = record.gettii_num
            gettii_seat.block = record.gettii_block
            gettii_seat.gate = record.gettii_gate
            gettii_seat.priority = record.gettii_priority
            gettii_seat.area_code = record.gettii_area_code
            gettii_seat.priority_block = record.gettii_priority_block
            gettii_seat.priority_seat = record.gettii_priority_seat
            gettii_seat.seat_flag = record.gettii_seat_flag
            gettii_seat.seat_classif = record.gettii_seat_classif
            gettii_seat.net_block = record.gettii_net_block
            gettii_seat.modifier = record.gettii_modifier
            gettii_seat.modified_at = record.gettii_modified_at

            gettii_seat.gettii_venue_id = gettii_venue.id
            gettii_seat.seat_id = seat.id
        else:
            try:
                gettii_seat = GettiiSeat.query.filter(GettiiSeat.seat_id==seat.id).one()
                gettii_seat.seat_id = None
            except NoResultFound:
                return
            except MultipleResultsFound:
                raise GettiiVenueImportError('Venue id mistmatch: Venue.id{} != Seat.venue_id={}'.format(
                    venue_id, seat.venue_id))
        gettii_seat.save()

    def import_(self, venue_id, csvdata):
        venue = Venue.query.filter(Venue.id==venue_id).one()
        for record in csvdata:
            self.import_record(venue.id, record)
