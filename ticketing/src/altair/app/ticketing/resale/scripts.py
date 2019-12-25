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
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import Performance, Seat
from altair.app.ticketing.events.performances.api import send_all_resale_request
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.orders.models import (Order,
                                                OrderedProduct,
                                                OrderedProductItem,
                                                OrderedProductItemToken)
from altair.app.ticketing.skidata.models import SkidataBarcode
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
        .filter(ResaleSegment.resale_performance_id != None)\
        .filter(ResaleSegment.deleted_at == None)\
        .filter(ResaleSegment.sent_at != None)\
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

        ordered_product_item_tokens = DBSession_slave.query(OrderedProductItemToken.seat_id, Seat.l0_id) \
            .outerjoin(Seat) \
            .join(OrderedProductItem)\
            .join(OrderedProduct)\
            .join(Order)\
            .join(Performance)\
            .filter(Performance.id == p_resale.id)\
            .filter(Order.deleted_at == None) \
            .filter(Order.canceled_at == None) \
            .filter(Order.paid_at != None) \
            .filter(OrderedProduct.deleted_at == None)\
            .filter(OrderedProductItem.deleted_at == None)\
            .filter(OrderedProductItemToken.deleted_at == None)\
            .filter(Seat.deleted_at == None)

        if ordered_product_item_tokens.count() == 0:
            logging.info("resale performance (ID: {}) has no orders. skip...".format(resale_segment.resale_performance_id))
            continue

        sold_request = query.filter(ResaleRequest.status == ResaleRequestStatus.sold)
        to_syn_count = ordered_product_item_tokens.count() - sold_request.count()
        if to_syn_count <= 0:
            logging.info("resale_segment (ID: {}) has no resale_requests need to be updated. skip...".format(resale_segment.id))
            continue

        spec_l0_id_list = []
        free_seat_count = 0
        for opit in ordered_product_item_tokens.all():
            if opit.seat_id:
                # 指定席
                spec_l0_id_list.append((opit.l0_id))
            else:
                # 自由席
                free_seat_count+=1

        # 指定席
        spec_resale_request_list = DBSession.query(ResaleRequest.id, ResaleRequest.ordered_product_item_token_id) \
            .join(OrderedProductItemToken, and_(OrderedProductItemToken.id == ResaleRequest.ordered_product_item_token_id)) \
            .join(Seat) \
            .filter(ResaleRequest.resale_segment_id == resale_segment.id) \
            .filter(ResaleRequest.status == ResaleRequestStatus.waiting) \
            .filter(ResaleRequest.deleted_at == None) \
            .filter(Seat.l0_id.in_(spec_l0_id_list))\
            .with_lockmode('update')

        spec_resale_requests_id = [id for id, ordered_product_item_token_id in spec_resale_request_list]
        spec_ordered_product_item_token_id = [ordered_product_item_token_id for id, ordered_product_item_token_id, in spec_resale_request_list]

        spec_resale_requests = DBSession.query(ResaleRequest)\
            .filter(ResaleRequest.id.in_(spec_resale_requests_id))
        spec_resale_requests.update(
            {ResaleRequest.status: ResaleRequestStatus.sold, ResaleRequest.sold_at: datetime.now()},
            synchronize_session='fetch')
        transaction.commit()

        logging.info("the reserved seat resale_requests of resale_segment (ID: {}) have been updated.".format(resale_segment.id))

        # 既にリセールされた自由席数
        resale_sold_count = DBSession.query(ResaleRequest.id) \
            .join(OrderedProductItemToken, and_(OrderedProductItemToken.id == ResaleRequest.ordered_product_item_token_id)) \
            .filter(ResaleRequest.resale_segment_id == resale_segment.id) \
            .filter(ResaleRequest.status == ResaleRequestStatus.sold) \
            .filter(ResaleRequest.deleted_at == None) \
            .filter(OrderedProductItemToken.seat_id == None) \
            .count()

        # 自由席
        free_resale_request_list = DBSession.query(ResaleRequest.id, ResaleRequest.ordered_product_item_token_id)\
            .filter(ResaleRequest.resale_segment_id == resale_segment.id)\
            .filter(ResaleRequest.status == ResaleRequestStatus.waiting)\
            .filter(ResaleRequest.deleted_at == None) \
            .order_by(ResaleRequest.created_at) \
            .limit(free_seat_count - resale_sold_count)\
            .with_lockmode('update')

        free_resale_requests_id = [id for id, ordered_product_item_token_id in free_resale_request_list]
        free_ordered_product_item_token_id = [ordered_product_item_token_id for id, ordered_product_item_token_id in free_resale_request_list]

        free_resale_requests = DBSession.query(ResaleRequest) \
            .filter(ResaleRequest.id.in_(free_resale_requests_id))
        free_resale_requests.update(
            {ResaleRequest.status: ResaleRequestStatus.sold, ResaleRequest.sold_at: datetime.now()},
            synchronize_session=False)
        transaction.commit()

        logging.info("the unreserved seat resale_requests of resale_segment (ID: {}) have been updated.".format(
            resale_segment.id))

        # 指定席request_idと自由席request_id結合
        spec_resale_requests_id[len(spec_resale_requests_id):len(spec_resale_requests_id)] = free_resale_requests_id
        spec_ordered_product_item_token_id[len(spec_ordered_product_item_token_id):len(spec_ordered_product_item_token_id)] = free_ordered_product_item_token_id

        ski_qr_codes = DBSession.query(SkidataBarcode.data)\
            .filter(SkidataBarcode.ordered_product_item_token_id.in_(spec_ordered_product_item_token_id))\
            .filter(SkidataBarcode.canceled_at.is_(None))\
            .all()

        # SKIDATA
        for ski_qr_code in ski_qr_codes:
            make_whitelist(action=TSAction.DELETE, qr_code=ski_qr_code.data)

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
        .filter(ResaleSegment.resale_performance_id != None)\
        .filter(ResaleSegment.deleted_at == None)\
        .filter(ResaleSegment.sent_at != None) \
        .filter(ResaleSegment.sent_status == SentStatus.sent) \
        .filter(cast(ResaleSegment.resale_end_at, t_date) == cast((datetime.now()-timedelta(days=1)), t_date))\
        .all()

    for resale_segment in resale_segments:
        logging.info("start updating and sending resale_requests of resale_segment (ID: {}) with not sold.".format(resale_segment.id))

        to_syn_request = DBSession.query(ResaleRequest.id) \
            .filter(ResaleRequest.resale_segment_id == resale_segment.id) \
            .filter(ResaleRequest.status == ResaleRequestStatus.waiting) \
            .filter(ResaleRequest.deleted_at == None)\
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
