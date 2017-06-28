#! /usr/bin/env python
#-*- coding: utf-8 -*-
import logging
import argparse
from sqlalchemy.orm.exc import NoResultFound
from altair.app.ticketing.core.models import (
    Seat,
    AugusStockInfo,
)

logger = logging.getLogger(__name__)

def get_seat(venue_id):
    return Seat.query.filte_by(venue_id=venue_id)

def main(augus_performance_id, correct_venue_id, incorrect_venue_id):
    correct_seats = get_seat(correct_venue_id)
    incorrect_seats = get_seat(incorrect_venue_id)

    augus_stock_infos = AugusStockInfo.query.filter_by(augus_performance_id=augus_performance_id).all()

    for augus_stock_info in augus_stock_infos:
        try:
            incorrect_seat = incorrect_seats.filter_by(id=augus_stock_info.seat_id).one()
        except NoResultFound:
            continue
        correct_seat = correct_seats.filter_by(l0_id=incorrect_seat.l0_id).one()

        logger.info('update seat_id of AugusStockInfo(id={augus_stock_info_id}) \
        from incorrect seat(id={incorrect_seat_id}) to correct seat(id={correct_seat_id})'.format(
            augus_stock_info_id=augus_stock_info.id,
            incorrect_seat_id=augus_stock_info.seat_id,
            correct_seat_id=correct_seat.id
        ))
        augus_stock_info.seat_id = correct_seat.id
        augus_stock_info.save()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fix Augus Seats Connection')
    parser.add_argument('--augus_performance_id')
    parser.add_argument('--correct_venue_id')
    parser.add_argument('--incorrect_venue_id')
    args = parser.parse_args()
    main(args.augus_performance_id, args.correct_venue_id, args.incorrect_venue_id)