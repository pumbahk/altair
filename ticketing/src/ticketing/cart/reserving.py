# -*- coding:utf-8 -*-

"""
席予約のロジック実装
"""

import logging
from ticketing.core.models import (
    DBSession,
    Performance,
    Venue,
    Stock,
    Seat,
    SeatStatus,
    SeatStatusEnum,
    SeatIndex,
    SeatIndexType,
    SeatAdjacency,
    SeatAdjacencySet,
    Seat_SeatAdjacency,
)
from sqlalchemy.sql import not_, or_
from sqlalchemy.orm import joinedload, aliased

logger = logging.getLogger(__name__)

class NotEnoughAdjacencyException(Exception):
    """ 必要な連席が存在しない場合 """


class InvalidSeatSelectionException(Exception):
    """ ユーザー選択座席が不正な場合 """

class Reserving(object):
    def __init__(self, request):
        self.request = request

    def reserve_selected_seats(self, stockstatus, performance_id, selected_seat_l0_ids, reserve_status=SeatStatusEnum.InCart):
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
            s.status = int(reserve_status)
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

        venue = Venue.query \
            .join(Performance, Venue.performance_id == Performance.id) \
            .join(Stock, Performance.id == Stock.performance_id) \
            .filter(Stock.id == stock_id).one()

        # すでに確保済みか、異なるstock_idのSeatを持つ連席
        def query_reserved_adjacencies(venue, stock_id, quantity):
            _SeatAdjacency = aliased(SeatAdjacency)
            _SeatAdjacencySet = aliased(SeatAdjacencySet)
            _Seat = aliased(Seat)
            _SeatStatus = aliased(SeatStatus)
            _Seat_SeatAdjacency = aliased(Seat_SeatAdjacency)
            _Venue = aliased(Venue)
            return DBSession.query(_SeatAdjacency.id).filter(
                    # すでに確保済み
                    or_(
                        _SeatStatus.status != int(SeatStatusEnum.Vacant),
                        _Seat.stock_id != stock_id)
                ).filter(
                    _Seat_SeatAdjacency.seat_adjacency_id == _SeatAdjacency.id
                ).filter(
                    _Seat_SeatAdjacency.l0_id == _Seat.l0_id
                ).filter(
                    _SeatAdjacencySet.id == _SeatAdjacency.adjacency_set_id
                ).filter(
                    _SeatAdjacencySet.seat_count==quantity,
                ).filter(
                    _SeatStatus.seat_id==_Seat.id
                ).filter(
                    _SeatAdjacencySet.site_id==venue.site_id
                ).filter(
                    _Seat.venue_id==venue.id
                )

        # 未確保の座席だけからなる SeatAdjacency を探す
        def query_adjacency(venue, stock_id, quantity, seat_index_type_id):
            _SeatAdjacency = aliased(SeatAdjacency)
            _SeatAdjacencySet = aliased(SeatAdjacencySet)
            _Seat = aliased(Seat)
            _SeatStatus = aliased(SeatStatus)
            _Seat_SeatAdjacency = aliased(Seat_SeatAdjacency)
            _SeatIndex = aliased(SeatIndex)
            _Venue = aliased(Venue)
            return DBSession.query(_SeatAdjacency.id).filter(
                    _SeatAdjacencySet.seat_count==quantity,
                ).filter(
                    _SeatAdjacencySet.id==_SeatAdjacency.adjacency_set_id,
                ).filter(
                    _SeatAdjacencySet.site_id==venue.site_id
                ).filter(
                    _SeatAdjacency.id==_Seat_SeatAdjacency.seat_adjacency_id
                ).filter(
                    _Seat.l0_id==_Seat_SeatAdjacency.l0_id
                ).filter(
                    _Seat.stock_id==stock_id
                ).filter(
                    _SeatIndex.seat_id==_Seat.id
                ).filter(
                    _SeatIndex.seat_index_type_id==seat_index_type_id
                ).filter(
                    not_(_SeatAdjacency.id.in_(query_reserved_adjacencies(venue, stock_id, quantity)))
                ).filter(
                    _Seat.venue_id==venue.id
                ).order_by(_SeatIndex.index, _Seat.l0_id)

        def query_selected_seats(venue, stock_id, quantity, seat_index_type_id):
            _Seat = Seat # aliased(Seat) # XXX: これをaliasedにするとSQLAlchemyが変なクエリ (余計な Seat へのテーブル参照) を生成する
            _Seat_SeatAdjacency = aliased(Seat_SeatAdjacency)
            _SeatIndex = aliased(SeatIndex)
            return DBSession.query(_Seat_SeatAdjacency.seat_adjacency_id, _Seat).options(
                    joinedload(_Seat.status_)
                ).filter(
                    _Seat.l0_id == _Seat_SeatAdjacency.l0_id
                ).filter(
                    _Seat_SeatAdjacency.seat_adjacency_id == query_adjacency(venue, stock_id, quantity, seat_index_type_id).limit(1)
                ).filter(
                    _Seat.venue_id == venue.id
                ).filter(
                    _SeatIndex.seat_id==_Seat.id
                ).filter(
                    _SeatIndex.seat_index_type_id==seat_index_type_id
                ).order_by(_SeatIndex.index, _Seat.l0_id)

        _selected_seats = query_selected_seats(venue, stock_id, quantity, seat_index_type_id).all()

        if not _selected_seats:
            raise NotEnoughAdjacencyException
        selected_seats = [seat for _, seat in _selected_seats]
        assert len(selected_seats) == quantity
        assert all(seat.status == SeatStatusEnum.Vacant.v for seat in selected_seats)
        return selected_seats
