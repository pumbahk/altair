# -*- coding:utf-8 -*-

""" オーソリキャンセルバッチ

TODO: 抽選などオーソリ保持が必要な機能によるものはキャンセルしない

"""

import argparse
import logging
from datetime import timedelta
from pyramid.paster import bootstrap, setup_logging

from ticketing.multicheckout import api
from ticketing.multicheckout import models as m

logger = logging.getLogger(__name__)


def sync_data(request, multicheckout_setting):
    """
    前処理（データ訂正）
    
    API問い合わせ結果を正とするようにステータス管理テーブルを訂正する
    
        オーソリ依頼してキャンセルしていないものについて、注文ステータス問い合わせ
        この時点でキャンセル済のものはキャンセル済フラグをたてる
        売り上げ確定済のものは売り上げ確定済フラグをたてる
訂正した場合、対応するAPIレスポンスのデータ取得が必要か？
    """
    q = m._session.query(m.MultiCheckoutOrderStatus).filter(
            m.MultiCheckoutOrderStatus.is_authorized
        ).filter(
            m.MultiCheckoutOrderStatus.past(timedelta(hours=1))
        )

    for st in q:
        order_no = st.OrderNo
        logging.debug("sync for %s" % order_no)
        inquiry = api.checkout_inquiry(request, order_no)

        if not inquiry.is_authorized:
            m.MultiCheckoutOrderStatus.set_status(inquiry.OrderNo, inquiry.Storecd, inquiry.Status,
                u"by cancel auth batch")
        m._session.commit()


def get_auth_orders(shop_id):
    q = m._session.query(m.MultiCheckoutOrderStatus).filter(
            m.MultiCheckoutOrderStatus.Storecd==shop_id
        ).filter(
            m.MultiCheckoutOrderStatus.is_authorized
        ).filter(
            m.MultiCheckoutOrderStatus.past(timedelta(hours=1))
        ).filter(
            m.MultiCheckoutOrderStatus.KeepAuthFor==None,
        )
    return q

def cancel_auth(request, multicheckout_setting):
    """
    本処理
    
        キャンセル条件にしたがってオーソリ依頼データを取得
    """

    shop_id = multicheckout_setting.shop_id
    shop_name = multicheckout_setting.shop_name
    logger.debug('search authorization for %s:%s' % (shop_name, shop_id))

    q = get_auth_orders(shop_id)

    for st in q:
        order_no = st.OrderNo
        logging.debug('call auth cancel api for %s' % order_no)
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

    # multicheckoutsettingsごとに行う
    processed_shops = []
    for multicheckout_setting in api.get_multicheckout_settings(request):
        name = multicheckout_setting.shop_name
        shop_id = multicheckout_setting.shop_id
        if shop_id in processed_shops:
            logger.info("%s: shop_id = %s is already processed" % (name, shop_id))
            continue

        request.altair_checkout3d_override_shop_name = name

        logger.info("starting sync_data %s" % name)
        sync_data(request, multicheckout_setting)
        logger.info("finished sync_data %s" % name)

        logger.info("starting cancel_auth %s" % name)
        cancel_auth(request, multicheckout_setting)
        logger.info("finished cancel_auth %s" % name)
        processed_shops.append(shop_id)

if __name__ == '__main__':
    main()
