#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import logging
import transaction
from datetime import datetime, timedelta

from pyramid.paster import bootstrap
from sqlalchemy import func, or_, and_
from sqlalchemy.sql.expression import not_

from altair.app.ticketing.core import models as c

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    config_file = argv[1]
    log_file = os.path.abspath(argv[2])
    bootstrap(config_file)
    logging.config.fileConfig(log_file)

    logger.info('start copy_seat_adjacency batch')

    now = datetime.now() - timedelta(days=1)
    venues_to_skip = set()
    venues_to_commit = set()

    while True:
        try:
            # 1日以内に更新された、SeatAdjacencySetが1件もないVenueを抽出
            query = c.Venue.query.filter(c.Venue.updated_at>now)
            query = query.outerjoin(c.SeatAdjacencySet)
            if venues_to_skip:
                query = query.filter(not_(c.Venue.id.in_(venues_to_skip)))
            query = query.group_by(c.Venue.id).having(func.count(c.SeatAdjacencySet.id)==0)

            venue = query.with_lockmode('update').first()
            if venue is None:
                logging.info('venue not found')
                break
            logger.info('copy from=%s, to=%s, %s, %s' % (venue.original_venue_id, venue.id, venue.name, venue.updated_at))

            org_venue = c.Venue.get(venue.original_venue_id)
            if org_venue is None or not org_venue.adjacency_sets:
                logging.info('skip')
                venues_to_skip.add(venue.id)
                continue

            # copy SeatAdjacencySet - SeatAdjacency
            seat_adjacency_map = {}
            for org_adjacency_set in org_venue.adjacency_sets:
                seat_adjacency_map.update(
                    c.SeatAdjacencySet.create_from_template(
                        template=org_adjacency_set,
                        venue_id=venue.id
                    )
                )

            # copy Seat_SeatAdjacency
            seats = dict([(seat.l0_id, seat.id) for seat in venue.seats])
            for org_seat in org_venue.seats:
                if org_seat.adjacencies:
                    seat_seat_adjacencies = []
                    for org_adjacency in org_seat.adjacencies:
                        seat_seat_adjacencies.append({
                            'seat_adjacency_id':seat_adjacency_map[org_adjacency.id],
                            'seat_id':seats[org_seat.l0_id],
                        })
                    c.DBSession.execute(c.Seat_SeatAdjacency.__table__.insert(), seat_seat_adjacencies)

            venues_to_commit.add(venue.id)
            venue.save()
            transaction.commit()

            # 最大10件処理したら終了
            if len(venues_to_commit) > 10:
                break
        except Exception, e:
            logger.error(e.message)
            transaction.abort()
            break

    logger.info('end copy_seat_adjacency batch')


if __name__ == '__main__':
    main()
