# -*- coding: utf-8 -*-
import argparse
import logging
import sqlahelper
import transaction

from datetime import datetime
from pyramid.paster import bootstrap, setup_logging
from sqlalchemy.orm.exc import (NoResultFound,
                                MultipleResultsFound)
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import ProductItem, Performance
from altair.app.ticketing.orders.models import OrderedProductItem, OrderedProductItemToken
from altair.app.ticketing.core.models import (Stock,
                                              StockHolder,
                                              StockType,
                                              Seat,
                                              Venue,
                                              SeatStatusEnum,
                                              SalesSegment,
                                              SalesSegmentGroup)
from .models import (ResaleSegment,
                     ResaleRequest,
                     SentStatus,
                     ResaleRequestStatus)


def do_update_resale_auto_stock(request):
    DBSession_slave = get_db_session(request, 'slave')
    resale_segments = DBSession_slave.query(ResaleSegment)\
        .filter(ResaleSegment.resale_performance_id.isnot(None))\
        .filter(ResaleSegment.deleted_at.is_(None))\
        .filter(ResaleSegment.sent_at.isnot(None)) \
        .filter(ResaleSegment.sent_status == SentStatus.sent) \
        .filter(ResaleSegment.reception_start_at <= datetime.now()) \
        .filter(ResaleSegment.reception_end_at >= datetime.now()) \
        .all()

    for resale_segment in resale_segments:
        logging.info("start updating auto_stock of resale_segment (ID: {})".format(resale_segment.id))
        try:
            p_resale = DBSession_slave.query(Performance).filter_by(id=resale_segment.resale_performance_id).one()
        except NoResultFound:
            logging.info("resale performance (ID: {}) not found. skip...".format(resale_segment.resale_performance_id))
            continue
        except MultipleResultsFound:
            logging.error("multiple records found for resale performance: (ID: {}) ".format(resale_segment.resale_performance_id))
            continue

        query = DBSession_slave.query(ResaleRequest)\
            .filter(ResaleRequest.resale_segment_id == resale_segment.id)\
            .filter(ResaleRequest.deleted_at.is_(None))\
            .filter(ResaleRequest.sent_status == SentStatus.not_sent)\
            .filter(ResaleRequest.status == ResaleRequestStatus.waiting)\
            .filter(ResaleRequest.stock_count_at.is_(None))\
            .order_by(ResaleRequest.created_at)

        if query.count() == 0:
            # リセール申請数が無い
            logging.info("resale_segment (ID: {}) has no resale_requests. skip...".format(resale_segment.id))
            continue

        resale_requests = query.all()
        resale_requests_id_list = []
        stock_quantity_dict = {}
        for resale_request in resale_requests:
            ordered_product_item_tokens = DBSession_slave.query(OrderedProductItemToken) \
                .filter(OrderedProductItemToken.id == resale_request.ordered_product_item_token_id) \
                .filter(OrderedProductItemToken.deleted_at.is_(None)).first()

            if not ordered_product_item_tokens:
                logging.info("resale_requests (ID: {}) has no tokens. skip...".format(resale_request.id))
                continue

            if ordered_product_item_tokens.seat:
                # 指定席
                origin_seat = Seat.filter_by(l0_id=ordered_product_item_tokens.seat.l0_id) \
                    .join(Seat.venue) \
                    .filter(Venue.performance_id == resale_segment.performance_id).first()

                resale_stock_spec = DBSession_slave.query(Stock.id) \
                    .join(Performance) \
                    .join(StockHolder) \
                    .join(StockType) \
                    .join(SalesSegmentGroup) \
                    .filter(StockHolder.name == u'自社')\
                    .filter(StockType.id == origin_seat.stock.stock_type_id) \
                    .filter(StockType.quantity_only == False) \
                    .filter(Stock.deleted_at.is_(None)) \
                    .filter(Stock.performance_id == p_resale.id).first()

                seat = Seat.filter_by(l0_id=ordered_product_item_tokens.seat.l0_id) \
                    .join(Seat.venue) \
                    .filter(Venue.performance_id == p_resale.id).first()
                seat.stock_id = resale_stock_spec.id
                seat.status = SeatStatusEnum.Vacant.v
                seat.save()

                if resale_stock_spec.id in stock_quantity_dict:
                    # 同じ席種があるの場合
                    stock_quantity_dict[resale_stock_spec.id] = stock_quantity_dict[resale_stock_spec.id] + 1
                else:
                    # 同じ席種がないの場合
                    stock_quantity_dict[resale_stock_spec.id] = 1

                resale_requests_id_list.append(resale_request.id)
            else:
                # 自由席
                resale_stock = DBSession_slave.query(Stock.stock_type_id)\
                    .join(ProductItem)\
                    .join(OrderedProductItem)\
                    .join(OrderedProductItemToken)\
                    .filter(OrderedProductItemToken.id == ordered_product_item_tokens.id)\
                    .filter(ProductItem.deleted_at.is_(None))\
                    .filter(Stock.deleted_at.is_(None)).first()

                resale_stock_free = DBSession_slave.query(Stock.id) \
                    .join(Performance) \
                    .join(StockHolder) \
                    .join(StockType) \
                    .join(SalesSegmentGroup) \
                    .filter(StockHolder.name == u'自社') \
                    .filter(StockType.id == resale_stock.stock_type_id) \
                    .filter(StockType.quantity_only == True) \
                    .filter(Stock.deleted_at.is_(None)) \
                    .filter(Stock.performance_id == p_resale.id).first()

                if resale_stock_free.id in stock_quantity_dict:
                    # 同じ席種があるの場合
                    stock_quantity_dict[resale_stock_free.id] = stock_quantity_dict[resale_stock_free.id] + 1
                else:
                    # 同じ席種がないの場合
                    stock_quantity_dict[resale_stock_free.id] = 1

                resale_requests_id_list.append(resale_request.id)

        if resale_requests_id_list:
            ResaleRequest.query.filter(ResaleRequest.id.in_(resale_requests_id_list)) \
                .update({ResaleRequest.stock_count_at: datetime.now()}, synchronize_session='fetch')
        else:
            logging.info("resale_requests (ID: {}) has no stock. skip...".format(resale_request.id))
            continue

        sale_stocks = DBSession_slave.query(Stock)\
            .join(Performance)\
            .join(SalesSegment)\
            .join(SalesSegmentGroup)\
            .filter(Stock.deleted_at.is_(None)) \
            .filter(Stock.performance_id == p_resale.id).all()

        stock_status_id_item = []
        total_stock_id = None
        total_stock_quantity = 0
        for i, sale_stock in enumerate(sale_stocks):
            if i == 0:
                # 一つ目の総在庫数
                total_stock_id = sale_stock.id
                total_stock_quantity = sale_stock.quantity
            if sale_stock.stock_holder != None and sale_stock.stock_type != None:
                if not sale_stock.stock_type.quantity_only:
                    total_stock_quantity = total_stock_quantity - sale_stock.quantity
                if sale_stock.id in stock_quantity_dict:
                    stock_status_id_item.append((sale_stock.id, stock_quantity_dict[sale_stock.id]))

        if total_stock_id:
            auto_stock = Stock.filter_by(id=total_stock_id).first()
            auto_stock.quantity = total_stock_quantity
            auto_stock.save()

        for stock_id, stock_quantity in stock_status_id_item:
            auto_stock = Stock.filter_by(id=stock_id).first()
            auto_stock.quantity = auto_stock.quantity + stock_quantity
            auto_stock.save()

        transaction.commit()
        logging.info("completed updating auto_stock of resale_segment (ID: {})".format(resale_segment.id))


def update_resale_auto_stock():
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    logging.info('start update_resale_auto_stock batch')

    # 多重起動防止
    LOCK_NAME = update_resale_auto_stock.__name__
    LOCK_TIMEOUT = 10
    conn = sqlahelper.get_engine().connect()
    status = conn.scalar("select get_lock(%s,%s)", (LOCK_NAME, LOCK_TIMEOUT))
    if status != 1:
        logging.warn('lock timeout: already running process')
        return
    try:
        do_update_resale_auto_stock(request)
    except Exception as e:
        logging.error('failed to update_resale_auto_stock: {}'.format(e.message), exc_info=True)

    conn.close()
    logging.info('end update_resale_auto_stock batch')
