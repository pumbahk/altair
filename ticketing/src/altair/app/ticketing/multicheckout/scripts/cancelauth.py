# -*- coding:utf-8 -*-

""" オーソリキャンセルバッチ

TODO: 抽選などオーソリ保持が必要な機能によるものはキャンセルしない

"""

import argparse
import logging
from datetime import timedelta

from pyramid.paster import bootstrap, setup_logging
import sqlahelper

from altair.app.ticketing.multicheckout import api
from altair.app.ticketing.multicheckout import models as m
from altair.app.ticketing.multicheckout.interfaces import ICancelFilter

logger = logging.getLogger(__name__)


def sync_data(request, statuses):
    """
    前処理（データ訂正）
    
    API問い合わせ結果を正とするようにステータス管理テーブルを訂正する
    
        オーソリ依頼してキャンセルしていないものについて、注文ステータス問い合わせ
        この時点でキャンセル済のものはキャンセル済フラグをたてる
        売り上げ確定済のものは売り上げ確定済フラグをたてる
訂正した場合、対応するAPIレスポンスのデータ取得が必要か？
    """
    for st in statuses:
        order_no = st.OrderNo
        logger.debug("sync for %s" % order_no)
        inquiry = api.checkout_inquiry(request, order_no)

        if not inquiry.is_authorized:
            m.MultiCheckoutOrderStatus.set_status(inquiry.OrderNo, inquiry.Storecd, inquiry.Status,
                u"by cancel auth batch")
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
            m.MultiCheckoutOrderStatus.is_authorized
        ).filter(
            m.MultiCheckoutOrderStatus.past(timedelta(hours=1))
        )

    return [s for s in q if is_cancelable(request, s)]

def cancel_auth(request, statuses):
    """
    本処理
    
        キャンセル条件にしたがってオーソリ依頼データを取得
    """
    for st in statuses:
        order_no = st.OrderNo
        logger.debug('call auth cancel api for %s' % order_no)
        api.checkout_auth_cancel(request, order_no)
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

    # 多重起動防止
    LOCK_NAME = 'cancelauth'
    LOCK_TIMEOUT = 10
    conn = sqlahelper.get_engine().connect()
    status = conn.scalar("select get_lock(%s,%s)", (LOCK_NAME, LOCK_TIMEOUT))
    if status != 1:
        logger.warn('lock timeout: already running process')
        return

    # multicheckoutsettingsごとに行う
    processed_shops = []
    for multicheckout_setting in api.get_multicheckout_settings(request):
        shop_name = multicheckout_setting.shop_name
        shop_id = multicheckout_setting.shop_id
        if shop_id in processed_shops:
            logger.info("%s: shop_id = %s is already processed" % (shop_name, shop_id))
            continue

        request.altair_checkout3d_override_shop_name = shop_name

        logger.info("starting get_auth_orders %s" % shop_name)
        statuses = get_auth_orders(request, shop_id)
        logger.info("finished get_auth_orders %s" % shop_name)

        if statuses:
            logger.info("starting sync_data %s" % shop_name)
            sync_data(request, statuses)
            logger.info("finished sync_data %s" % shop_name)

            logger.info("starting cancel_auth %s" % shop_name)
            cancel_auth(request, statuses)
            logger.info("finished cancel_auth %s" % shop_name)
        processed_shops.append(shop_id)

if __name__ == '__main__':
    main()
