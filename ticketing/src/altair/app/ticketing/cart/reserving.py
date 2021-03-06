# -*- coding:utf-8 -*-

"""
席予約のロジック実装
"""

import logging
from altair.app.ticketing.core.models import (
    DBSession,
    Performance,
    Venue,
    Stock,
    Seat,
    SeatGroup,
    SeatStatus,
    SeatStatusEnum,
    SeatIndex,
    SeatIndexType,
    SeatAdjacency,
    SeatAdjacencySet,
    Seat_SeatAdjacency,
)
from sqlalchemy.sql import not_, or_, func, distinct
from sqlalchemy.orm import joinedload, aliased
from altair.sqlahelper import get_db_session

logger = logging.getLogger(__name__)

class NotEnoughAdjacencyException(Exception):
    """ 必要な連席が存在しない場合 """
    def __init__(self, stock_id=None, quantity=None, seat_index_type_id=None):
        super(NotEnoughAdjacencyException, self).__init__()
        self.stock_id = stock_id
        self.quantity = quantity
        self.seat_index_type_id = seat_index_type_id

class InvalidSeatSelectionException(Exception):
    """ ユーザー選択座席が不正な場合 """

class Reserving(object):
    def __init__(self, request, session):
        self.request = request
        self.session = session
        self.__slave_session = get_db_session(self.request, name="slave")

    def reserve_selected_seats(self, stockstatus, performance_id, selected_seat_l0_ids, reserve_status=SeatStatusEnum.InCart):
        """ ユーザー選択座席予約 """
        logger.debug('user select seats %s, performance_id %s' % (selected_seat_l0_ids, performance_id))
        logger.debug('stock %s' % [s[0].stock_id for s in stockstatus])

        selected_seats = self.session.query(Seat).filter(
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

        seat_group_ids = [
            t[0] for t in self.session.query(SeatGroup.id) \
                .join(Seat, SeatGroup.l0_id == Seat.row_l0_id) \
                .with_hint(Seat, 'USE INDEX (primary)') \
                .join(Venue, Seat.venue_id == Venue.id) \
                .filter(SeatGroup.site_id == Venue.site_id) \
                .filter(Seat.id.in_(seat.id for seat in selected_seats)) \
                .filter(Venue.performance_id == performance_id) \
                .union_all(
                    self.session.query(SeatGroup.id) \
                    .join(Seat, SeatGroup.l0_id == Seat.group_l0_id) \
                    .with_hint(Seat, 'USE INDEX (primary)') \
                    .join(Venue, Seat.venue_id == Venue.id) \
                    .filter(SeatGroup.site_id == Venue.site_id) \
                    .filter(Seat.id.in_(seat.id for seat in selected_seats)) \
                    .filter(Venue.performance_id == performance_id) \
                    ) \
                .distinct() \
            ]

        if len(seat_group_ids) > 0:
            logger.debug('seat_group_ids=%r' % seat_group_ids)
            seats_in_group = self.session.query(Seat) \
                .join(Venue, Seat.venue_id == Venue.id) \
                .join(SeatGroup, SeatGroup.l0_id == Seat.row_l0_id) \
                .filter(SeatGroup.site_id == Venue.site_id) \
                .filter(SeatGroup.id.in_(seat_group_ids)) \
                .filter(Venue.performance_id == performance_id) \
                .union(
                    self.session.query(Seat) \
                        .join(Venue, Seat.venue_id == Venue.id) \
                        .join(SeatGroup, SeatGroup.l0_id == Seat.group_l0_id) \
                        .filter(SeatGroup.site_id == Venue.site_id) \
                        .filter(SeatGroup.id.in_(seat_group_ids)) \
                        .filter(Venue.performance_id == performance_id) \
                    ) \
                .count()
            if seats_in_group != len(selected_seats):
                logger.debug("selected_seats (%d) != seats_in_group (%d)" % (len(selected_seats), seats_in_group))
                raise InvalidSeatSelectionException("selected_seats (%d) != seats_in_group (%d)" % (len(selected_seats), seats_in_group))

        if len(selected_seats) != len(selected_seat_l0_ids):
            logger.debug("seats %s" % selected_seats)
            raise InvalidSeatSelectionException('number of resolved seats (%d) is not equal to number of given l0_ids (%d)' % (len(selected_seats), len(selected_seat_l0_ids)))

        # although seat_id is the primary key, optimizer may wrongly choose other index
        # if IN predicate has many values, because of implicit "deleted_at IS NULL" (#11358)
        seat_statuses = self.session.query(SeatStatus).filter(
            SeatStatus.seat_id.in_([s.id for s in selected_seats])
        ).filter(
            SeatStatus.status==int(SeatStatusEnum.Vacant)
        ).with_hint(SeatStatus, 'USE INDEX (primary)').with_lockmode('update').all()

        if len(seat_statuses) != len(selected_seat_l0_ids):
            logger.debug("seat_statuses %s" % seat_statuses)
            raise InvalidSeatSelectionException("len(seat_statuses) (%d) != len(selected_seat_l0_ids) (%d)" % (len(seat_statuses), len(selected_seat_l0_ids)))

        for s in seat_statuses:
            s.status = int(reserve_status)
        return selected_seats

    def reserve_seats(self, stock_id, quantity, reserve_status=SeatStatusEnum.InCart, separate_seats=False):
        try:
            seats = self.get_vacant_seats(stock_id, quantity)
            logger.debug('reserving %d seats for stock %s' % (len(seats), stock_id))
            self._reserve(seats, reserve_status)
        except NotEnoughAdjacencyException as e:
            # 連席が必須なら例外を返す
            if not separate_seats:
                raise e
            # 連席でなくてよいならバラ席で確保して返す
            logger.debug('try to reserve %d seats' % quantity)
            seats = self._reserve_not_adjacent_seats(stock_id, quantity, reserve_status)
        return seats

    def _reserve_not_adjacent_seats(self, stock_id, quantity, reserve_status):
        retval = []
        skip_quantities = [quantity]
        divisor = 2
        while quantity > len(retval):
            rest = quantity - len(retval)
            reserve_quantity = (rest / divisor) + (rest % divisor)
            if reserve_quantity >= min(skip_quantities):
                reserve_quantity = min(skip_quantities) - 1
            logger.debug('total=%s, rest=%s, reserve_quantity=%s' % (quantity, rest, reserve_quantity))
            try:
                seats = self.get_vacant_seats(stock_id, reserve_quantity)
                logger.debug('reserving %d seats for stock %s' % (len(seats), stock_id))
                self._reserve(seats, reserve_status)
                retval.extend(seats)
                divisor = 1
            except NotEnoughAdjacencyException as e:
                logger.debug('Not enough adjacency')
                skip_quantities.append(reserve_quantity)
                divisor += 1
                if rest < divisor:
                    raise e
        return retval

    def _reserve(self, seats, reserve_status):
        # although seat_id is the primary key, optimizer may wrongly choose other index
        # if IN predicate has many values, because of implicit "deleted_at IS NULL" (#11358)
        statuses = self.session.query(SeatStatus).filter(
            SeatStatus.seat_id.in_([s.id for s in seats])
        ).with_hint(SeatStatus, 'USE INDEX (primary)').with_lockmode('update').all()
        for stat in statuses:
            stat.status = int(reserve_status)
        return statuses

    def get_default_seat_index_type_id(self, stock_id):
        """ Stock -> Performance -> Venue """

        seat_index_type = self.session.query(SeatIndexType).filter(
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
        return self.session.query(Seat).filter(
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

        venue = self.session.query(Venue) \
            .join(Performance, Venue.performance_id == Performance.id) \
            .join(Stock, Performance.id == Stock.performance_id) \
            .filter(Stock.id == stock_id).one()

        def query_selected_seats(venue, stock_id, quantity, seat_index_type_id):
            # 空きSeat取得Query(SeatIndexでソート)
            vacant_seat_query = self.session.query(Seat.l0_id)\
                .join(SeatStatus, Seat.id == SeatStatus.seat_id)\
                .join(SeatIndex, SeatIndex.seat_id == Seat.id)\
                .filter(Seat.stock_id == stock_id,
                        SeatStatus.status == SeatStatusEnum.Vacant.v,
                        SeatIndex.seat_index_type_id == seat_index_type_id)\
                .order_by(SeatIndex.index, Seat.l0_id)
            # SQLAlchemyはカラムが単一でもtupleのlistでreturnしてくるので、simpleなlistに変換
            sorted_vacant_l0_ids = [result.l0_id for result in vacant_seat_query]

            # 空き連席情報を取得 連席情報はマスタデータのためSlaveで負荷分散
            vacant_adjacency_query = \
                self.__slave_session.query(Seat_SeatAdjacency.seat_adjacency_id,
                                           func.group_concat(Seat_SeatAdjacency.l0_id))\
                    .join(SeatAdjacency, SeatAdjacency.id == Seat_SeatAdjacency.seat_adjacency_id)\
                    .join(SeatAdjacencySet, SeatAdjacency.adjacency_set_id == SeatAdjacencySet.id)\
                    .filter(SeatAdjacencySet.seat_count == quantity,
                            SeatAdjacencySet.site_id == venue.site_id,
                            Seat_SeatAdjacency.l0_id.in_(sorted_vacant_l0_ids))\
                    .group_by(Seat_SeatAdjacency.seat_adjacency_id)\
                    .having(func.count(Seat_SeatAdjacency.seat_adjacency_id) == quantity)
            # key=l0_id, value=連席IDのdictに変換。dictを使ったランダムアクセスによるサーチに使う
            vacant_adjacency_dict = {}
            for seat_adjacency_id, concatenated_l0_ids in vacant_adjacency_query:
                for l0_id in concatenated_l0_ids.split(u','):
                    adjacencies = vacant_adjacency_dict.get(l0_id) or []
                    adjacencies.append(seat_adjacency_id)
                    vacant_adjacency_dict.update({l0_id: adjacencies})

            # 優先順(SeatIndex順)に、空き連席を返す
            seat_adjacency_id = None
            for l0_id in sorted_vacant_l0_ids:
                if l0_id in vacant_adjacency_dict:
                    # SeatIndexの順であればどの連席でも良い仕様のため、任意の連席IDをとる(ここではlistの先頭)
                    seat_adjacency_id = vacant_adjacency_dict.get(l0_id)[0]
                    break

            return self.session.query(Seat_SeatAdjacency.seat_adjacency_id, Seat) \
                .options(joinedload(Seat.status_)) \
                .join(Seat, Seat_SeatAdjacency.l0_id == Seat.l0_id) \
                .filter(Seat.venue_id == venue.id) \
                .filter(Seat_SeatAdjacency.seat_adjacency_id == seat_adjacency_id)

        _selected_seats = query_selected_seats(venue, stock_id, quantity, seat_index_type_id).all()

        if not _selected_seats:
            raise NotEnoughAdjacencyException(stock_id=stock_id, quantity=quantity, seat_index_type_id=seat_index_type_id)
        selected_seats = [seat for _, seat in _selected_seats]
        assert len(selected_seats) == quantity
        assert all(seat.status == SeatStatusEnum.Vacant.v for seat in selected_seats)
        return selected_seats
