from altair.app.ticketing.core.models import StockType, StockTypeEnum
from altair.sqlahelper import get_db_session
from pyramid.threadlocal import get_current_request


def get_seat_stock_types(event_id):
    return StockType.filter_by(event_id=event_id, type=StockTypeEnum.Seat.v).order_by(StockType.display_order.asc()).all()


def get_non_seat_stock_types(event_id):
    return StockType.filter_by(event_id=event_id, type=StockTypeEnum.Other.v).order_by(StockType.display_order.asc()).all()


def get_seat_stock_types_by_event_id(event_id):
    session = get_db_session(get_current_request(), 'slave')
    return session.query(StockType.id, StockType.name).filter_by(event_id=event_id).all()
