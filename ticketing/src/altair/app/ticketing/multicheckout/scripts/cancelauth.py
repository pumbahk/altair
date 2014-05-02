# -*- coding:utf-8 -*-

""" オーソリキャンセルバッチ

"""

import argparse
import logging
from datetime import timedelta

from pyramid.paster import bootstrap, setup_logging
import sqlahelper
from sqlalchemy.sql import or_
from altair.multicheckout import models as m
from altair.multicheckout.api import get_multicheckout_3d_api, get_all_multicheckout_settings
from altair.multicheckout.interfaces import ICancelFilter

logger = logging.getLogger(__name__)


def sync_data(request, statuses, shop_name, api=None):
    """
    前処理（データ訂正）
    
    API問い合わせ結果を正とするようにステータス管理テーブルを訂正する
    
        オーソリ依頼してキャンセルしていないものについて、注文ステータス問い合わせ
        この時点でキャンセル済のものはキャンセル済フラグをたてる
        売り上げ確定済のものは売り上げ確定済フラグをたてる
        訂正した場合、対応するAPIレスポンスのデータ取得が必要か？
    """
    if api is None:
        api = get_multicheckout_3d_api(request, shop_name)
    for st in statuses:
        if not (st.Status is None or is_cancelable(request, st)):
            continue
        order_no = st.OrderNo
        logger.debug("sync for %s" % order_no)
        inquiry = api.checkout_inquiry(order_no, u'cancel auth batch')
        m._session.commit()

def get_cancel_filter(request, name):
    return request.registry.queryUtility(ICancelFilter, name=name)

def is_cancelable(request, status):
    order_no = status.OrderNo
    logger.debug('check cancelable {0}'.format(order_no))
    name = status.KeepAuthFor
    if name is None:
        return True
    cancel_filter = get_cancel_filter(request, name)
    if cancel_filter is None:
        logger.debug('no cancel filter for {0}'.format(name))
        return False
    logger.debug('use cancel filter for {0}'.format(name))
    return cancel_filter.is_cancelable(order_no)

def get_auth_orders(request, shop_id):
    q = m._session.query(m.MultiCheckoutOrderStatus).filter(
            m.MultiCheckoutOrderStatus.Storecd==shop_id
        ).filter(
            or_(m.MultiCheckoutOrderStatus.is_authorized,
                m.MultiCheckoutOrderStatus.is_unknown_status,
                )
        ).filter(
            m.MultiCheckoutOrderStatus.past(timedelta(hours=1))
        ).order_by(m.MultiCheckoutOrderStatus.KeepAuthFor, m.MultiCheckoutOrderStatus.id)
    return q.all()

def cancel_auth(request, statuses, shop_name, api=None):
    """
    本処理
    
        キャンセル条件にしたがってオーソリ依頼データを取得
    """
    if api is None:
        api = get_multicheckout_3d_api(request, shop_name)
    for st in statuses:
        if not is_cancelable(request, st):
            continue

        order_no = st.OrderNo
        if not st.is_authorized:
            logger.debug(
                'not call auth cancel api for %s: status %s' % (order_no,
                                                                st.Status))
            continue

        logger.debug('call auth cancel api for %s' % order_no)
        api.checkout_auth_cancel(order_no)

        m._session.commit()

def main():
    """
    TODO: オプション指定
    注文番号指定で実行
    ショップ指定で実行
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    request.environ['PATH_INFO'] = "/cancelauth"
    logger.info("start offline as {request.url}".format(request=request))

    # 多重起動防止
    LOCK_NAME = 'cancelauth'
    LOCK_TIMEOUT = 10
    conn = sqlahelper.get_engine().connect()
    status = conn.scalar("select get_lock(%s,%s)", (LOCK_NAME, LOCK_TIMEOUT))
    if status == 1:
        run(request)
        return
    else:
        logger.warn('lock timeout: already running process')
        return

def run(request):
    # multicheckoutsettingsごとに行う
    processed_shops = []
    for multicheckout_setting in get_all_multicheckout_settings(request):
        shop_name = multicheckout_setting.shop_name
        shop_id = multicheckout_setting.shop_id
        if shop_id in processed_shops:
            logger.info("%s: shop_id = %s is already processed" % (shop_name, shop_id))
            continue
        try:
            process_shop(request, shop_id, shop_name)
        except Exception, e:
            logging.error('Multicheckout API error occured: %s' % e.message)
            break
        processed_shops.append(shop_id)
    return processed_shops

def process_shop(request, shop_id, shop_name):
    logger.info("starting get_auth_orders %s" % shop_name)
    statuses = get_auth_orders(request, shop_id)
    logger.info("finished get_auth_orders %s" % shop_name)
    logger.info(
        "shop:%s auth orders count = %d" % (shop_name, len(statuses)))
    if not statuses:
        return 

    logger.info("starting sync_data and cancel_auth %s" % shop_name)
    api = get_multicheckout_3d_api(request, shop_name)
    for status in statuses:
        sync_data(request, [status], shop_name, api)
        cancel_auth(request, [status], shop_name, api)
    logger.info("finished sync_data and cancel_auth %s" % shop_name)

if __name__ == '__main__':
    main()
