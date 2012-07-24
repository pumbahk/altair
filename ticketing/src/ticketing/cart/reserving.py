# -*- coding:utf-8 -*-

"""
席予約のロジック実装
"""

import logging
from ticketing.core.models import *
from sqlalchemy.sql import not_

logger = logging.getLogger(__name__)

class NotEnoughAdjacencyException(Exception):
    """ 必要な連席が存在しない場合 """

class Reserving(object):
    def __init__(self, request):
        self.request = request

    def reserve_seats(self, stock_id, quantity):
        seats = self.get_vacant_seats(stock_id, quantity)
        logger.debug('reserving %d seats' % len(seats))
        self._reserve(seats)
        return seats

    def _reserve(self, seats):
        statuses = SeatStatus.query.filter(
            SeatStatus.seat_id.in_([s.id for s in seats])
        ).all()
        for stat in statuses:
            stat.status = int(SeatStatusEnum.InCart)
        return statuses
        
    def get_vacant_seats(self, stock_id, quantity):
        """ 空き席を取得 """

        if quantity == 1:
            return
        # すでに確保済みのSeatを持つ連席
        reserved_adjacencies = DBSession.query(SeatAdjacency.id).filter(
            # すでに確保済み
            SeatStatus.status != int(SeatStatusEnum.Vacant)
        ).filter(
            seat_seat_adjacency_table.c.seat_adjacency_id == SeatAdjacency.id
        ).filter(
            seat_seat_adjacency_table.c.seat_id == Seat.id
        ).filter(
            SeatAdjacencySet.seat_count==quantity,
        ).filter(
            Seat.stock_id==stock_id
        ).filter(
            SeatStatus.seat_id==Seat.id
        )

        adjacency = SeatAdjacency.query.filter(
            SeatAdjacencySet.seat_count==quantity,
        ).filter(
            SeatAdjacencySet.id==SeatAdjacency.adjacency_set_id,
        ).filter(
            Seat.stock_id==stock_id
        ).filter(
            SeatAdjacency.id==seat_seat_adjacency_table.c.seat_adjacency_id
        ).filter(
            Seat.id==seat_seat_adjacency_table.c.seat_id
        ).filter(
            SeatIndex.seat_id==Seat.id
        ).filter(
            not_(SeatAdjacency.id.in_(reserved_adjacencies))
        ).filter(
            SeatIndex.seat_id==Seat.id
        ).order_by(SeatIndex.index).first()

        if adjacency is None:
            raise NotEnoughAdjacencyException
        assert len(adjacency.seats) == quantity
        return adjacency.seats
