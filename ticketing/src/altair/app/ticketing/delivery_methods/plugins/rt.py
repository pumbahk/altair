# encoding: utf-8

from zope.interface import implementer
from ..interfaces import IDeliveryFormMaker

from .base import WebCouponDeliveryFormMaker, DeliveryMethodForm
from altair.app.ticketing.core.models import DeliveryMethodPlugin
from altair.app.ticketing.payments.plugins import WEB_COUPON_DELIVERY_PLUGIN_ID

def includeme(config):
    config.add_delivery_form_maker(RTWebCouponDeliveryFormMaker(), u"RT")


class RTWebCouponDeliveryMethodForm(DeliveryMethodForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(RTWebCouponDeliveryMethodForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        web_coupon_choices = [(dmp.id, dmp.name) for dmp in DeliveryMethodPlugin.filter(
            DeliveryMethodPlugin.id == WEB_COUPON_DELIVERY_PLUGIN_ID).all()]
        choices = self.delivery_plugin_id.choices
        choices.extend(web_coupon_choices)
        self.delivery_plugin_id.choices = choices


@implementer(IDeliveryFormMaker)
class RTWebCouponDeliveryFormMaker(WebCouponDeliveryFormMaker):
    def __init__(self):
        super(WebCouponDeliveryFormMaker, self).__init__()

    def make_form(self, formdata=None, obj=None, prefix='', **kwargs):
        return RTWebCouponDeliveryMethodForm(formdata=formdata, obj=obj, prefix=prefix, **kwargs)

