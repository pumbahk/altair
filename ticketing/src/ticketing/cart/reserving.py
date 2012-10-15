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


class InvalidSeatSelectionException(Exception):
    """ ユーザー選択座席が不正な場合 """

class Reserving(object):
    def __init__(self, request):
        self.request = request

    def reserve_selected_seats(self, stockstatus, performance_id, selected_seat_l0_ids):
        """ ユーザー選択座席予約 """
        logger.debug('user select seats %s, performance_id %s' % (selected_seat_l0_ids, performance_id))
        logger.debug('stock %s' % [s[0].stock_id for s in stockstatus])
        selected_seats = Seat.query.filter(
            Seat.l0_id.in_(selected_seat_l0_ids),
        ).filter(
            Venue.id==Seat.venue_id,
        ).filter(
            Performance.id==Venue.performance_id
        ).filter(
            Stock.id==Seat.stock_id
        ).filter(
            Stock.id.in_([s[0].stock_id for s in stockstatus])
        ).all()

        if len(selected_seats) != len(selected_seat_l0_ids):
            logger.debug("seats %s" % selected_seats)
            raise InvalidSeatSelectionException
        seat_statuses = SeatStatus.query.filter(
            SeatStatus.seat_id.in_([s.id for s in selected_seats])
        ).filter(
            SeatStatus.status==int(SeatStatusEnum.Vacant)
        ).with_lockmode('update').all()

        if len(seat_statuses) != len(selected_seat_l0_ids):
            logger.debug("seat_statuses %s" % seat_statuses)
            raise InvalidSeatSelectionException

        for s in seat_statuses:
            s.status = int(SeatStatusEnum.InCart)
        return selected_seats

    def reserve_seats(self, stock_id, quantity):
        seats = self.get_vacant_seats(stock_id, quantity)
        logger.debug('reserving %d seats for stock %s' % (len(seats), stock_id))
        self._reserve(seats)
        return seats

    def _reserve(self, seats):
        statuses = SeatStatus.query.filter(
            SeatStatus.seat_id.in_([s.id for s in seats])
        ).with_lockmode('update').all()
        for stat in statuses:
            stat.status = int(SeatStatusEnum.InCart)
        return statuses
        
    def get_default_seat_index_type_id(self, stock_id):
        """ Stock -> Performance -> Venue """

        seat_index_type = DBSession.query(SeatIndexType).filter(
            SeatIndexType.venue_id==Venue.id
        ).filter(
            Venue.performance_id==Stock.performance_id
        ).filter(
            Stock.id==stock_id
        ).order_by(SeatIndexType.id).first()

        if seat_index_type is None:
            return None

        return seat_index_type.id
        
    def _get_single_seat(self, stock_id, seat_index_type_id):
        return Seat.query.filter(
            Seat.stock_id==stock_id
        ).filter(
            SeatStatus.seat_id==Seat.id
        ).filter(
            SeatStatus.status==int(SeatStatusEnum.Vacant)
        ).filter(
            SeatIndex.seat_id==Seat.id
        ).filter(
            SeatIndex.seat_index_type_id==seat_index_type_id
        ).order_by(SeatIndex.index, Seat.l0_id)[:1]

    def get_vacant_seats(self, stock_id, quantity, seat_index_type_id=None):
        """ 空き席を取得 """

        if seat_index_type_id is None:
            seat_index_type_id = self.get_default_seat_index_type_id(stock_id)

        if quantity == 1:
            
            return self._get_single_seat(stock_id, seat_index_type_id)

        # すでに確保済みのSeatを持つ連席
        reserved_adjacencies = DBSession.query(SeatAdjacency.id).filter(
            # すでに確保済み
            SeatStatus.status != int(SeatStatusEnum.Vacant)
        ).filter(
            Seat_SeatAdjacency.seat_adjacency_id == SeatAdjacency.id
        ).filter(
            Seat_SeatAdjacency.seat_id == Seat.id
        ).filter(
            SeatAdjacencySet.seat_count==quantity,
        ).filter(
            Seat.stock_id==stock_id
        ).filter(
            SeatStatus.seat_id==Seat.id
        )

        adjacencies = SeatAdjacency.query.filter(
            SeatAdjacencySet.seat_count==quantity,
        ).filter(
            SeatAdjacencySet.id==SeatAdjacency.adjacency_set_id,
        ).filter(
            Seat.stock_id==stock_id
        ).filter(
            SeatAdjacency.id==Seat_SeatAdjacency.seat_adjacency_id
        ).filter(
            Seat.id==Seat_SeatAdjacency.seat_id
        ).filter(
            SeatIndex.seat_id==Seat.id
        ).filter(
            not_(SeatAdjacency.id.in_(reserved_adjacencies))
        ).filter(
            SeatIndex.seat_id==Seat.id
        ).filter(
            SeatIndex.seat_index_type_id==seat_index_type_id
        ).order_by(SeatIndex.index, Seat.l0_id).all()

        adjacency = None
        for adj in adjacencies:
            if [s for s in adj.seats if s.stock_id != stock_id]:
                continue
            adjacency = adj
            break

        if adjacency is None:
            raise NotEnoughAdjacencyException
        assert len(adjacency.seats) == quantity
        return adjacency.seats
