# -*- coding:utf-8 -*-

""" オーソリキャンセルバッチ

"""

import argparse
import logging
from datetime import datetime, timedelta
import parsedatetime

from pyramid.paster import bootstrap, setup_logging
import sqlahelper
from sqlalchemy.sql import or_
from altair.multicheckout import models as m
from altair.multicheckout.api import get_multicheckout_3d_api, get_all_multicheckout_settings, get_order_no_decorator
from altair.multicheckout.interfaces import ICancelFilter

logger = logging.getLogger(__name__)


class Canceller(object):
    def __init__(self, request, now=None, auth_cancel_expiry=None):
        self.request = request
        self.cancel_filter = self.request.registry.queryUtility(ICancelFilter)
        self.order_no_decorator = get_order_no_decorator(request)
        if now is None:
            now = datetime.now()
        if auth_cancel_expiry is None:
            auth_cancel_expiry = timedelta(hours=1)
        self.now = now
        self.auth_cancel_expiry = auth_cancel_expiry

    @property
    def multicheckout_settings(self):
        return get_all_multicheckout_settings(self.request)

    def is_auth_cancelable(self, status):
        order_no = status['order_no']
        if not status['is_authorized']:
            return False
        name = status['keep_auth_for']
        if name is None:
            return True
        if self.cancel_filter is None:
            logger.debug('no cancel filter for {0}'.format(name))
            return False
        logger.debug('use cancel filter for {0}'.format(name))
        return self.cancel_filter.is_cancelable(order_no)

    def get_auth_orders(self, multicheckout_setting):
        q = m._session.query(m.MultiCheckoutOrderStatus) \
            .filter(m.MultiCheckoutOrderStatus.Storecd==multicheckout_setting.shop_id) \
            .filter(
                or_(m.MultiCheckoutOrderStatus.is_authorized,
                    m.MultiCheckoutOrderStatus.is_unknown_status,
                    )
                ) \
            .filter(m.MultiCheckoutOrderStatus.updated_at < (self.now - self.auth_cancel_expiry)) \
            .order_by(m.MultiCheckoutOrderStatus.KeepAuthFor, m.MultiCheckoutOrderStatus.id)
        return [
            dict(
                id=status.id,
                order_no=self.order_no_decorator.undecorate(status.OrderNo),
                status=status.Status,
                is_authorized=status.is_authorized,
                keep_auth_for=status.KeepAuthFor,
                sales_amount=status.SalesAmount,
                eventual_sales_amount=status.EventualSalesAmount,
                tax_carriage_amount_to_cancel=status.TaxCarriageAmountToCancel
                )
            for status in q
            ]

    def get_orders_to_be_canceled(self, multicheckout_setting):
        q = m._session.query(m.MultiCheckoutOrderStatus) \
            .filter(m.MultiCheckoutOrderStatus.Storecd==multicheckout_setting.shop_id) \
            .filter(m.MultiCheckoutOrderStatus.is_settled) \
            .filter(m.MultiCheckoutOrderStatus.CancellationScheduledAt <= self.now) \
            .order_by(m.MultiCheckoutOrderStatus.CancellationScheduledAt)
        return [
            dict(
                id=status.id,
                order_no=self.order_no_decorator.undecorate(status.OrderNo),
                status=status.Status,
                is_authorized=status.is_authorized,
                keep_auth_for=status.KeepAuthFor,
                sales_amount=status.SalesAmount,
                eventual_sales_amount=status.EventualSalesAmount,
                tax_carriage_amount_to_cancel=status.TaxCarriageAmountToCancel
                )
            for status in q
            ]

    def sync_data(self, api, status):
        """
        前処理（データ訂正）
        
        API問い合わせ結果を正とするようにステータス管理テーブルを訂正する
        
            オーソリ依頼してキャンセルしていないものについて、注文ステータス問い合わせ
            この時点でキャンセル済のものはキャンセル済フラグをたてる
            売り上げ確定済のものは売り上げ確定済フラグをたてる
            訂正した場合、対応するAPIレスポンスのデータ取得が必要か？
        """
        order_no = status['order_no']
        logger.debug("sync for %s" % order_no)
        inquiry = api.checkout_inquiry(order_no, u'cancel auth batch')
        m._session.commit()

    def cancel_auth(self, api, status):
        """
        本処理
        
            キャンセル条件にしたがってオーソリ依頼データを取得
        """
        order_no = status['order_no']
        if not self.is_auth_cancelable(status):
            logger.info('order %s is not auth-cancelable (status=%s)' % (order_no, status['status']))
            return
        logger.info('call auth cancel api for %s' % order_no)
        api.checkout_auth_cancel(order_no)
        m._session.commit()

    def cancel_sales(self, api, status):
        """
        本処理
        
            キャンセル条件にしたがってオーソリ依頼データを取得
        """
        order_no = status['order_no']
        logger.info('call auth cancel api for %s' % order_no)
        amount_to_cancel = status['sales_amount'] - status['eventual_sales_amount']
        if amount_to_cancel > 0:
            api.checkout_sales_part_cancel(order_no, amount_to_cancel, status['tax_carriage_amount_to_cancel'])
        else:
            logger.info('no need to cancel')
        api.unschedule_cancellation(order_no)
        m._session.commit()

    def process_shop(self, multicheckout_setting):
        logger.info("starting get_auth_orders for %s" % multicheckout_setting.shop_name)
        statuses = self.get_auth_orders(multicheckout_setting)
        logger.info("finished get_auth_orders for %s" % multicheckout_setting.shop_name)
        logger.info("shop:%s auth orders count = %d" % (multicheckout_setting.shop_name, len(statuses)))

        api = get_multicheckout_3d_api(self.request, multicheckout_setting.shop_name, now=self.now)

        if statuses:
            logger.info("starting cancel_auth for %s" % multicheckout_setting.shop_name)
            for status in statuses:
                self.sync_data(api, status)
                self.cancel_auth(api, status)
            logger.info("finished cancel_auth for %s" % multicheckout_setting.shop_name)

        logger.info("starting get_orders_to_be_canceled for %s" % multicheckout_setting.shop_name)
        statuses = self.get_orders_to_be_canceled(multicheckout_setting)
        logger.info("finished get_orders_to_be_canceled for %s" % multicheckout_setting.shop_name)

        logger.info("shop:%s orders to be canceled count = %d" % (multicheckout_setting.shop_name, len(statuses)))
        if statuses:
            logger.info("starting sales cancel for %s" % multicheckout_setting.shop_name)
            for status in statuses:
                self.sync_data(api, status)
                self.cancel_sales(api, status)
            logger.info("finished sales_cancel for %s" % multicheckout_setting.shop_name)

    def run(self):
        # multicheckoutsettingsごとに行う
        processed_shops = []
        for multicheckout_setting in self.multicheckout_settings:
            if multicheckout_setting.shop_id in processed_shops:
                logger.info("%s: shop_id = %s is already processed" % (multicheckout_setting.shop_name, multicheckout_setting.shop_id))
                continue
            try:
                self.process_shop(multicheckout_setting)
            except Exception, e:
                logging.exception('Multicheckout API error occured: %s' % e.message)
                break
            processed_shops.append(multicheckout_setting.shop_id)
        return processed_shops

def parse_time_spec(spec):
    s = datetime(1900, 1, 1, 0, 0, 0)
    result, _ = parsedatetime.Calendar().parse(spec, s)
    return datetime(
        year=result.tm_year,
        month=result.tm_mon,
        day=result.tm_mday,
        hour=result.tm_hour,
        minute=result.tm_min,
        second=result.tm_sec
        ) - s

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
        auth_cancel_expiry = request.registry.settings.get('altair.multicheckout.auth_cancel_expiry', '1 hour')
        auth_cancel_expiry = parse_time_spec(auth_cancel_expiry)
        logger.info('auth_cancel_expiry=%s' % auth_cancel_expiry)
        Canceller(
            request,
            auth_cancel_expiry=auth_cancel_expiry
            ).run()
        return
    else:
        logger.warn('lock timeout: already running process')
        return

if __name__ == '__main__':
    main()
