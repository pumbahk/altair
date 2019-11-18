# encoding: utf-8

from zope.interface import implementer
from ..interfaces import IDeliveryFormMaker

from .base import WebCouponDeliveryFormMaker, DeliveryMethodForm
from altair.app.ticketing.core.models import DeliveryMethodPlugin
from altair.app.ticketing.payments.plugins import WEB_COUPON_DELIVERY_PLUGIN_ID

def includeme(config):
    config.add_delivery_form_maker(WebCouponDeliveryFormMaker(WPWebCouponDeliveryMethodForm), u"WP")


class WPWebCouponDeliveryMethodForm(DeliveryMethodForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(WPWebCouponDeliveryMethodForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        web_coupon_choices = [(dmp.id, dmp.name) for dmp in DeliveryMethodPlugin.filter(
            DeliveryMethodPlugin.id == WEB_COUPON_DELIVERY_PLUGIN_ID).all()]
        choices = self.delivery_plugin_id.choices
        choices.extend(web_coupon_choices)
        self.delivery_plugin_id.choices = choices

