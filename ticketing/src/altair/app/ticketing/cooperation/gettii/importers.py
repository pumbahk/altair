#-*- coding: utf-8 -*-
import logging
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
logger = logging.getLogger(__name__)

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
    def _import_record(self, venue_id, record):
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

    def is_match(self, record, gettii_seat):
        record_data = {
            'l0_id': record.gettii_l0_id,
            'coodx': record.gettii_coodx,
            'coody': record.gettii_coody,
            'posx': record.gettii_posx,
            'posy': record.gettii_posy,
            'angle': record.gettii_angle,
            'floor': record.gettii_floor,
            'column': record.gettii_column,
            'num': record.gettii_num,
            'block': record.gettii_block,
            'gate': record.gettii_gate,
            #'priority': record.gettii_priority,
            #'area_code': record.gettii_area_code,
            'priority_block': record.gettii_priority_block,
            'priority_seat': record.gettii_priority_seat,
            'seat_flag': record.gettii_seat_flag,
            'seat_classif': record.gettii_seat_classif,
            'net_block': record.gettii_net_block,
            #'modifier': record.gettii_modifier,
            'modified_at': record.gettii_modified_at,
            }

        db_data = {
            'l0_id': gettii_seat.l0_id,
            'coodx': gettii_seat.coordx,
            'coody': gettii_seat.coordy,
            'posx': gettii_seat.posx,
            'posy': gettii_seat.posy,
            'angle': gettii_seat.angle,
            'floor': gettii_seat.floor,
            'column': gettii_seat.column,
            'num': gettii_seat.num,
            'block': gettii_seat.block,
            'gate': gettii_seat.gate,
            #'priority': gettii_seat.priority,
            #'area_code': gettii_seat.area_code,
            'priority_block': gettii_seat.priority_block,
            'priority_seat': gettii_seat.priority_seat,
            'seat_flag': gettii_seat.seat_flag,
            'seat_classif': gettii_seat.seat_classif,
            'net_block': gettii_seat.net_block,
            #'modifier': gettii_seat.modifier,
            'modified_at': gettii_seat.modified_at,
            }
        return record_data == db_data


    def update_gettii_seat_from_record(self, record, gettii_seat):
        gettii_seat.l0_id = record.gettii_l0_id
        gettii_seat.coordx = record.gettii_coodx
        gettii_seat.coordy = record.gettii_coody
        gettii_seat.posx = record.gettii_posx
        gettii_seat.posy = record.gettii_posy
        gettii_seat.angle = record.gettii_angle
        gettii_seat.floor = record.gettii_floor
        gettii_seat.column = record.gettii_column
        gettii_seat.num = record.gettii_num
        gettii_seat.block = record.gettii_block
        gettii_seat.gate = record.gettii_gate
        #gettii_seat.priority = record.gettii_priority
        #gettii_seat.area_code = record.gettii_area_code
        gettii_seat.priority_block = record.gettii_priority_block
        gettii_seat.priority_seat = record.gettii_priority_seat
        gettii_seat.seat_flag = record.gettii_seat_flag
        gettii_seat.seat_classif = record.gettii_seat_classif
        gettii_seat.net_block = record.gettii_net_block
        #gettii_seat.modifier = record.gettii_modifier
        gettii_seat.modified_at = record.gettii_modified_at

    def import_(self, venue_id, csvdata):
        logger.debug('GETTII VENUE SYNC: start import gettii venue: venue_id={}'.format(venue_id))
        records = [record for record in csvdata]

        venue = Venue.query.filter(Venue.id==venue_id).one()
        gettii_venue_codes = list(set([record.gettii_venue_code for record in records if record.gettii_venue_code]))
        if len(gettii_venue_codes) != 1:
            raise GettiiVenueImportError('GettiiVenue is multiple')
        gettii_venue_code = gettii_venue_codes[0]
        gettii_venue = get_or_create_gettii_venue(gettii_venue_code, venue_id)
        gettii_venue.save()

        logger.debug('GETTII VENUE SYNC: create temporaly data: id_seat')
        id_seat = dict([(seat.id, seat) for seat in venue.seats])

        logger.debug('GETTII VENUE SYNC: create temporaly data: ex_l0_id__gettii_seat')
        ex_l0_id__gettii_seat = dict([(gettii_seat.l0_id, gettii_seat) for gettii_seat in gettii_venue.gettii_seats])

        _find_seat = lambda rec: id_seat.get(rec.id_, None)
        _find_gettii_seat = lambda rec: ex_l0_id__gettii_seat.get(rec.gettii_l0_id, None)

        updates = set()

        logger.debug('GETTII VENUE SYNC: validation: record.id_')
        for record in records:
            if not record.id_:
                raise GettiiVenueImportError('Illegal format: {}'.format(repr(record)))

        logger.debug('GETTII IMPORT: clean up data')
        target_seat_ids = [record.id_ for record in records]
        for gettii_seat in gettii_venue.gettii_seats:
            if gettii_seat.seat_id in target_seat_ids:
                gettii_seat.seat_id = None
                updates.add(gettii_seat)

        logger.debug('GETTII VENUE SYNC: update gettii seats')
        for record in records:
            seat = _find_seat(record)
            if not seat:
                raise GettiiVenueImportError('Seat is not exist: {}'.format(record.id_))

            gettii_seat = _find_gettii_seat(record)
            if not gettii_seat:
                gettii_seat = GettiiSeat()
                gettii_seat.gettii_venue_id = gettii_venue.id

            if not self.is_match(record, gettii_seat):
                updates.add(gettii_seat)
                self.update_gettii_seat_from_record(record, gettii_seat)

            if gettii_seat.seat_id != seat.id:
                updates.add(gettii_seat)
                gettii_seat.seat_id = seat.id

        logger.debug('GETTII VENUE SYNC: save gettii seats')
        for gettii_seat in updates:
            gettii_seat.save()
