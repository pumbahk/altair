# -*- coding:utf-8 -*-
from datetime import timedelta
from altair.app.ticketing.orders.models import Performance
from altair.app.ticketing.payments.plugins import RESERVE_NUMBER_DELIVERY_PLUGIN_ID, WEB_COUPON_DELIVERY_PLUGIN_ID

class CouponHelper(object):

    @classmethod
    def get_term_end_str(order, delivery_plugin_id):
        if not order:
            return u""

        delivery_method = order.payment_delivery_method_pair.delivery_method
        preferences = delivery_method.preferences.get(unicode(delivery_plugin_id), {})

        # 相対有効期限があった場合は優先
        if 'expiration_date' in preferences:
            expiration_date = preferences['expiration_date']
            if str(expiration_date).isdigit():
                fmt = u"%Y年%m月%d日 00:00まで入場できます。"
                return (order.created_at.date() + timedelta(days=(int(expiration_date) + 1))) \
                    .strftime(fmt.encode('utf-8')).decode('utf-8')

        perf = Performance.filter(Performance.id == order.performance_id).first()
        if perf.end_on:
            fmt = u"%Y年%m月%d日%H時%M分まで、ご入場できます。"
            return perf.end_on.strftime(fmt.encode('utf-8')).decode('utf-8')

        fmt = u"%Y年%m月%d日%H時%M分まで、ご入場できます。"
        return perf.start_on.strftime(fmt.encode('utf-8')).decode('utf-8')

    @staticmethod
    def get_term_end_str(order):
        return CouponHelper().get_term_end_str(order, RESERVE_NUMBER_DELIVERY_PLUGIN_ID)

    @staticmethod
    def get_web_coupon_term_end_str(order):
        return CouponHelper().get_term_end_str(order, WEB_COUPON_DELIVERY_PLUGIN_ID)


