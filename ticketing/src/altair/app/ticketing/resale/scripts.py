# -*- coding: utf-8 -*-
import argparse
import logging
import sqlahelper
import transaction

from datetime import datetime, timedelta
from pyramid.paster import bootstrap, setup_logging
from sqlalchemy.sql import and_
from sqlalchemy import Date as t_date, cast
from sqlalchemy.orm.exc import (NoResultFound,
                                MultipleResultsFound)
from altair.skidata.api import make_whitelist
from altair.skidata.models import TSAction
from altair.skidata.interfaces import ISkidataSession
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import (Performance,
                                              Seat,
                                              ProductItem,
                                              Stock)
from altair.app.ticketing.events.performances.api import send_all_resale_request
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.orders.models import (Order,
                                                OrderedProduct,
                                                OrderedProductItem,
                                                OrderedProductItemToken)
from altair.app.ticketing.skidata.models import SkidataBarcode
from altair.app.ticketing.skidata.api import send_whitelist_to_skidata
from .models import (ResaleSegment,
                     ResaleRequest,
                     SentStatus,
                     ResaleRequestStatus)


def _parse_resp_resale_request(resale_request, resp_result):
    if int(resp_result['request_id']) == resale_request.id and resp_result['success']:
        resale_request.sent_status = SentStatus.sent
    elif int(resp_result['request_id']) != resale_request.id:
        resale_request.sent_status = SentStatus.fail
        logging.error("fail to send resale request(ID: {}) because request id in orion was {} ...".format(
            resale_request.id,
            resp_result['request_id']
        ))
    elif not resp_result['success']:
        emsgs = resp_result['message']
        resale_request.sent_status = SentStatus.fail
        logging.error("fail to send resale request(ID: {}) with receiving error message was {}...".format(
            resale_request.id, emsgs))
    else:
        emsgs = resp_result['message'] if 'message' in resp_result else u"リセールリクエスト連携は失敗しました。"
        resale_request.sent_status = SentStatus.fail
        logging.error("fail to send resale request(ID: {}) ...".format(resale_request.id))
        logging.error("received error message was {} ...".format(emsgs))

def do_update_resale_request_status_with_sold(request):
    DBSession_slave = get_db_session(request, 'slave')
    resale_segments = DBSession_slave.query(ResaleSegment)\
        .filter(ResaleSegment.resale_performance_id.isnot(None))\
        .filter(ResaleSegment.deleted_at.is_(None))\
        .filter(ResaleSegment.sent_at.isnot(None))\
        .filter(ResaleSegment.sent_status == SentStatus.sent)\
        .filter(ResaleSegment.resale_start_at <= datetime.now())\
        .filter(ResaleSegment.resale_end_at >= datetime.now())\
        .all()

    for resale_segment in resale_segments:
        logging.info("start updating and sending resale_requests of resale_segment (ID: {}) with sold.".format(resale_segment.id))

        try:
            p_resale = DBSession_slave.query(Performance).filter_by(id=resale_segment.resale_performance_id).one()
        except (NoResultFound, MultipleResultsFound):
            logging.info("resale performance (ID: {}) not found. skip...".format(resale_segment.resale_performance_id))
            continue

        query = DBSession_slave.query(ResaleRequest).filter(ResaleRequest.resale_segment_id==resale_segment.id)
        if query.count() == 0:
            logging.info("resale_segment (ID: {}) has no resale_requests. skip...".format(resale_segment.id))
            continue

        # リセール先公演の購入履歴
        ordered_product_item_tokens = DBSession_slave.query(OrderedProductItemToken.seat_id, Seat.l0_id, Stock.id) \
            .outerjoin(Seat) \
            .join(OrderedProductItem)\
            .join(OrderedProduct) \
            .join(ProductItem) \
            .join(Stock) \
            .join(Order)\
            .join(Performance)\
            .filter(Performance.id == p_resale.id)\
            .filter(Order.deleted_at.is_(None)) \
            .filter(Order.canceled_at.is_(None)) \
            .filter(Order.paid_at.isnot(None)) \
            .filter(OrderedProduct.deleted_at.is_(None))\
            .filter(OrderedProductItem.deleted_at.is_(None))\
            .filter(OrderedProductItemToken.deleted_at.is_(None))\
            .filter(Seat.deleted_at.is_(None))

        if ordered_product_item_tokens.count() == 0:
            logging.info("resale performance (ID: {}) has no orders. skip...".format(resale_segment.resale_performance_id))
            continue

        sold_request = query.filter(ResaleRequest.status == ResaleRequestStatus.sold)
        to_syn_count = ordered_product_item_tokens.count() - sold_request.count()
        if to_syn_count <= 0:
            logging.info("resale_segment (ID: {}) has no resale_requests need to be updated. skip...".format(resale_segment.id))
            continue

        spec_l0_id_list = []
        free_stock_quantity_dicts = {}
        for opit in ordered_product_item_tokens.all():
            if opit.seat_id:
                # 指定席
                spec_l0_id_list.append((opit.l0_id))
            else:
                # 自由席_リセール先公演の販売済み情報
                if opit.id in free_stock_quantity_dicts:
                    # 2回目
                    free_stock_quantity_dicts[opit.id] = free_stock_quantity_dicts[opit.id] + 1
                else:
                    # 初期
                    free_stock_quantity_dicts[opit.id] = 1

        # 指定席_リセール出品
        spec_resale_request_list = DBSession.query(ResaleRequest.id, ResaleRequest.ordered_product_item_token_id) \
            .join(OrderedProductItemToken, and_(OrderedProductItemToken.id == ResaleRequest.ordered_product_item_token_id)) \
            .join(Seat) \
            .filter(ResaleRequest.resale_segment_id == resale_segment.id) \
            .filter(ResaleRequest.status == ResaleRequestStatus.waiting) \
            .filter(ResaleRequest.deleted_at.is_(None)) \
            .filter(Seat.l0_id.in_(spec_l0_id_list))\
            .with_lockmode('update')

        spec_resale_requests_id = [id for id, ordered_product_item_token_id in spec_resale_request_list]
        spec_ordered_product_item_token_id = [ordered_product_item_token_id for id, ordered_product_item_token_id, in spec_resale_request_list]

        # 指定席_リセール成立
        spec_resale_requests = DBSession.query(ResaleRequest)\
            .filter(ResaleRequest.id.in_(spec_resale_requests_id))
        spec_resale_requests.update(
            {ResaleRequest.status: ResaleRequestStatus.sold, ResaleRequest.sold_at: datetime.now()},
            synchronize_session='fetch')
        transaction.commit()

        logging.info("the reserved seat resale_requests of resale_segment (ID: {}) have been updated.".format(resale_segment.id))

        # 既にリセールされた自由席数_リセール成立 (リセール元公演)
        resale_sold_info = DBSession.query(ResaleRequest.id,
                                               Stock.id.label('stock_id'),
                                               Stock.stock_type_id) \
            .join(OrderedProductItemToken, and_(OrderedProductItemToken.id == ResaleRequest.ordered_product_item_token_id))\
            .join(OrderedProductItem)\
            .join(OrderedProduct) \
            .join(ProductItem) \
            .join(Stock) \
            .filter(ResaleRequest.resale_segment_id == resale_segment.id) \
            .filter(ResaleRequest.status == ResaleRequestStatus.sold) \
            .filter(ResaleRequest.deleted_at.is_(None)) \
            .filter(OrderedProductItemToken.seat_id.is_(None)).all()

        free_stock_type_quantitys = {}
        # リセール先の購入済みのStock
        for free_stock_id in free_stock_quantity_dicts:
            # リセール元のリセール済みのStock
            for rsi in resale_sold_info:
                # リセール先の購入済みのstock_type_id、リセール元のstock_type_idと一致してる事を抽出
                fix_free_stock_info = DBSession.query(Stock.id, Stock.stock_type_id)\
                    .filter(Stock.id == rsi.stock_id)\
                    .filter(Stock.stock_type_id.in_(
                            DBSession.query(Stock.stock_type_id).filter(Stock.id == free_stock_id).first())).first()

                #抽出stock_type_id、リセール元のstock_type_idと一致した場合(既存席種の購入)
                if fix_free_stock_info and fix_free_stock_info.stock_type_id == rsi.stock_type_id:
                    # リセール先の購入済み数からリセール元のリセール済み数程を差し引き
                    free_stock_type_quantitys[rsi.stock_type_id] = free_stock_quantity_dicts[free_stock_id] - 1
                    free_stock_quantity_dicts[free_stock_id] = free_stock_quantity_dicts[free_stock_id] - 1
                else:
                    # 抽出stock_type_id、リセール元のstock_type_idと一致しない場合(新規席種の購入)
                    first_fix_free_stock_info = DBSession.query(Stock.stock_type_id)\
                        .filter(Stock.id == free_stock_id).first()
                    if first_fix_free_stock_info:
                        # 新規席種の購入, 1から
                        free_stock_type_quantitys[first_fix_free_stock_info.stock_type_id] = 1

        for free_stock_id in free_stock_quantity_dicts:
            # リセール先の購入済みのstock_type_idを抽出
            resale_stock = DBSession.query(Stock.stock_type_id) \
                .filter(Stock.id == free_stock_id).first()

            # 自由席_リセール元の対象抽出(リセール中)
            free_resale_request_list = DBSession.query(ResaleRequest.id, ResaleRequest.ordered_product_item_token_id) \
                .join(OrderedProductItemToken, and_(OrderedProductItemToken.id == ResaleRequest.ordered_product_item_token_id))\
                .join(OrderedProductItem)\
                .join(OrderedProduct) \
                .join(ProductItem) \
                .join(Stock) \
                .filter(ResaleRequest.resale_segment_id == resale_segment.id)\
                .filter(ResaleRequest.status == ResaleRequestStatus.waiting) \
                .filter(Stock.stock_type_id == resale_stock.stock_type_id) \
                .filter(ResaleRequest.deleted_at.is_(None)) \
                .filter(OrderedProductItemToken.seat_id.is_(None))\
                .order_by(ResaleRequest.created_at)

            if resale_stock.stock_type_id in free_stock_type_quantitys and free_stock_quantity_dicts[free_stock_id] > 0:
                # 既存席種を購入された数
                free_resale_request_list = free_resale_request_list.limit(free_stock_quantity_dicts[free_stock_id])
                free_resale_request_list.with_lockmode('update')

            elif (free_stock_id not in free_stock_quantity_dicts) or (not resale_sold_info):
                # 新規席種を購入された数
                resaled_free_cnt = DBSession_slave.query(OrderedProductItemToken.id) \
                    .join(OrderedProductItem) \
                    .join(OrderedProduct) \
                    .join(ProductItem) \
                    .join(Stock) \
                    .join(Order) \
                    .join(Performance) \
                    .filter(Performance.id == p_resale.id) \
                    .filter(Stock.stock_type_id == resale_stock.stock_type_id) \
                    .filter(Order.deleted_at.is_(None)) \
                    .filter(Order.canceled_at.is_(None)) \
                    .filter(Order.paid_at.isnot(None)) \
                    .filter(OrderedProduct.deleted_at.is_(None)) \
                    .filter(OrderedProductItem.deleted_at.is_(None)) \
                    .filter(OrderedProductItemToken.deleted_at.is_(None)) \
                    .filter(OrderedProductItemToken.seat_id.is_(None))

                # リセーリ先の該当席種の数
                rf_cnt = resaled_free_cnt.count()
                # リセール元のリセール中の数
                waiting_cnt = free_resale_request_list.count()

                if waiting_cnt > rf_cnt:
                    waiting_cnt = rf_cnt

                free_resale_request_list = free_resale_request_list.limit(waiting_cnt)
                free_resale_request_list.with_lockmode('update')

            if (resale_stock.stock_type_id in free_stock_type_quantitys and free_stock_quantity_dicts[free_stock_id] > 0) \
                    or (free_stock_id not in free_stock_quantity_dicts) or (not resale_sold_info):
                free_resale_requests_id = [id for id, ordered_product_item_token_id in free_resale_request_list]
                free_ordered_product_item_token_id = [ordered_product_item_token_id for
                                                      id, ordered_product_item_token_id in free_resale_request_list]

                free_resale_requests = DBSession.query(ResaleRequest) \
                    .filter(ResaleRequest.id.in_(free_resale_requests_id))
                free_resale_requests.update(
                    {ResaleRequest.status: ResaleRequestStatus.sold, ResaleRequest.sold_at: datetime.now()},
                    synchronize_session=False)
                transaction.commit()

                # 指定席request_idと自由席request_id結合
                if spec_resale_requests_id and spec_ordered_product_item_token_id:
                    spec_resale_requests_id[len(spec_resale_requests_id):len(spec_resale_requests_id)] = free_resale_requests_id
                    spec_ordered_product_item_token_id[len(spec_ordered_product_item_token_id):len(spec_ordered_product_item_token_id)] = free_ordered_product_item_token_id
                else:
                    spec_resale_requests_id = free_resale_requests_id
                    spec_ordered_product_item_token_id = free_ordered_product_item_token_id

        logging.info("the unreserved seat resale_requresale performance (ID:ests of resale_segment (ID: {}) have been updated.".format(
            resale_segment.id))

        ski_barcodes = DBSession.query(SkidataBarcode)\
            .filter(SkidataBarcode.ordered_product_item_token_id.in_(spec_ordered_product_item_token_id))\
            .filter(SkidataBarcode.canceled_at.is_(None))\
            .all()

        # SKIDATA
        whitelist = []
        barcode_list = []
        for ski_barcode in ski_barcodes:
            if ski_barcode.sent_at is not None:
                whitelist.append(make_whitelist(action=TSAction.DELETE, qr_code=ski_barcode.data))
                barcode_list.append(ski_barcode)

        skidata_session = request.registry.queryUtility(ISkidataSession)
        if whitelist and skidata_session is not None:
            logging.debug('Delete Whitelist because it\'s already sent (SkidataBarcode ID: %s) ',
                         ', '.join([str(barcode.id) for barcode in barcode_list]))
            send_whitelist_to_skidata(skidata_session, whitelist, barcode_list, fail_silently=False)

        resale_requests = DBSession.query(ResaleRequest).filter(ResaleRequest.id.in_(spec_resale_requests_id))
        logging.info("start sending the resale_requests of resale_segment (ID: {}).".format(resale_segment.id))
        resale_requests.update({ResaleRequest.sent_at: datetime.now()}, synchronize_session=False)
        try:
            resp = send_all_resale_request(request, resale_requests.all())
            if not resp or not (resp['success'] and resp['submit']):
                logging.error("fail to send the resale request of resale segment(ID: {0}) ...".format(resale_segment.id))
                resale_requests.update({ResaleRequest.sent_status: SentStatus.fail}, synchronize_session=False)
            else:
                for resale_request, resp_result in zip(resale_requests, resp['result']['updates']):
                    _parse_resp_resale_request(resale_request, resp_result)
                    DBSession.merge(resale_request)

        except Exception as e:
            logging.error("fail to send the resale request of resale segment(ID: {0}) with the exception: {1}...".format(
                resale_segment.id, str(e))
            )
            resale_requests.update({ResaleRequest.sent_status: SentStatus.fail}, synchronize_session=False)

        transaction.commit()
        logging.info("completed updating and sending resale_requests of resale_segment (ID: {}) with sold.".format(resale_segment.id))



def do_update_resale_request_status_with_not_sold(request):
    DBSession_slave = get_db_session(request, 'slave')
    resale_segments = DBSession_slave.query(ResaleSegment)\
        .filter(ResaleSegment.resale_performance_id.isnot(None))\
        .filter(ResaleSegment.deleted_at.is_(None))\
        .filter(ResaleSegment.sent_at.isnot(None)) \
        .filter(ResaleSegment.sent_status == SentStatus.sent) \
        .filter(cast(ResaleSegment.resale_end_at, t_date) == cast((datetime.now()-timedelta(days=1)), t_date))\
        .all()

    for resale_segment in resale_segments:
        logging.info("start updating and sending resale_requests of resale_segment (ID: {}) with not sold.".format(resale_segment.id))

        to_syn_request = DBSession.query(ResaleRequest.id) \
            .filter(ResaleRequest.resale_segment_id == resale_segment.id) \
            .filter(ResaleRequest.status == ResaleRequestStatus.waiting) \
            .filter(ResaleRequest.deleted_at.is_(None))\
            .with_lockmode('update')

        if to_syn_request.count() == 0:
            logging.info("resale_segment (ID: {}) has no resale_requests need to be updated. skip...".format(resale_segment.id))
            continue

        to_syn_request_list = [id for id, in to_syn_request]
        resale_requests = DBSession.query(ResaleRequest) \
            .filter(ResaleRequest.id.in_(to_syn_request_list))

        resale_requests.update(
            {ResaleRequest.status: ResaleRequestStatus.back},
            synchronize_session=False)
        transaction.commit()
        logging.info("the resale_requests of resale_segment (ID: {}) have been updated.".format(resale_segment.id))

        logging.info("start sending the resale_requests of resale_segment (ID: {}).".format(resale_segment.id))
        resale_requests.update({ResaleRequest.sent_at: datetime.now()}, synchronize_session=False)
        try:
            resp = send_all_resale_request(request, resale_requests.all())
            if not resp or not (resp['success'] and resp['submit']):
                logging.error("fail to send the resale request of resale segment(ID: {0}) ...".format(resale_segment.id))
                resale_requests.update({ResaleRequest.sent_status: SentStatus.fail}, synchronize_session=False)
            else:
                for resale_request, resp_result in zip(resale_requests, resp['result']['updates']):
                    _parse_resp_resale_request(resale_request, resp_result)
                    DBSession.merge(resale_request)

        except Exception as e:
            logging.error("fail to send the resale request of resale segment(ID: {0}) with the exception: {1}...".format(
                resale_segment.id, str(e))
            )
            resale_requests.update({ResaleRequest.sent_status: SentStatus.fail}, synchronize_session=False)

        transaction.commit()
        logging.info("completed updating and sending resale_requests of resale_segment (ID: {}) with not sold.".format(resale_segment.id))

def update_resale_request_status():
    """リセールリクエストの一括更新（販売されたリクエストのみ）
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--sold', action='store_true')
    g.add_argument('--not_sold', action='store_true')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    logging.info('start update_resale_request_status batch')

    # 多重起動防止
    LOCK_NAME = update_resale_request_status.__name__
    LOCK_TIMEOUT = 10
    conn = sqlahelper.get_engine().connect()
    status = conn.scalar("select get_lock(%s,%s)", (LOCK_NAME, LOCK_TIMEOUT))
    if status != 1:
        logging.warn('lock timeout: already running process')
        return
    if args.sold:
        try:
            do_update_resale_request_status_with_sold(request)
        except Exception as e:
            logging.error('failed to update_resale_request_status_with_sold: {}'.format(e.message), exc_info=True)
    elif args.not_sold:
        try:
            do_update_resale_request_status_with_not_sold(request)
        except Exception as e:
            logging.error('failed to update_resale_request_status_with_not_sold: {}'.format(e.message), exc_info=True)
    else:
        logging.error('please specify the status to update the resale requests.', exc_info=True)

    conn.close()
    logging.info('end update_resale_request_status batch')
