# -*- coding:utf-8 -*-

"""
席予約のロジック実装
"""

from ticketing.core.models import *
from sqlalchemy.sql import not_

class Reserving(object):
    def __init__(self, request):
        self.request = request

    def get_vacant_seats(self, stock_id, quantity):
        """ 空き席を取得 """

        if quantity == 1:
            return
        # 対象になる stock
        Stock.id == stock_id

        # stockに属するSeat
        Seat.stock_id == Stock.id

        # quantityに対応する連席
        SeatAdjacencySet.seat_count == quantity
        SeatAdjacency.adjacency_set_id == SeatAdjacencySet.id
        
        # 連席に属する席
        seat_seat_adjacency_table.c.seat_adjacency_id == SeatAdjacency.id
        seat_seat_adjacency_table.c.seat_id == Seat.id

        # 席状況
        SeatStatus.seat_id == seat_seat_adjacency_table.c.seat_id



        # すでに確保済みのSeatを持つ連席
        reserved_adjacencies = DBSession.query(SeatAdjacency.id).filter(
            # すでに確保済み
            SeatStatus.status != int(SeatStatusEnum.Vacant)
        ).filter(
            seat_seat_adjacency_table.c.seat_adjacency_id == SeatAdjacency.id
        ).filter(
            seat_seat_adjacency_table.c.seat_id == SeatStatus.seat_id
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
        ).first()

        return adjacency.seats
