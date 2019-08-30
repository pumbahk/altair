# encoding: utf-8

from zope.interface import implementer
from ..interfaces import IDeliveryFormMaker

from .base import WebCouponDeliveryFormMaker, DeliveryMethodForm
from altair.app.ticketing.payments.plugins import WEB_COUPON_DELIVERY_PLUGIN_ID

def includeme(config):
    config.add_delivery_form_maker(RTWebCouponDeliveryFormMaker(), u"RT")


class RTWebCouponDeliveryMethodForm(DeliveryMethodForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(RTWebCouponDeliveryMethodForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        organization_id = self.request.registry.settings.get(
            'altair.delivery_methods.web_coupon.white_organization_id', '')
        if self.context.organization.id != int(organization_id):
            choices = [choice for choice in self.delivery_plugin_id.choices
                       if choice[0] != WEB_COUPON_DELIVERY_PLUGIN_ID]
            self.delivery_plugin_id.choices = choices


@implementer(IDeliveryFormMaker)
class RTWebCouponDeliveryFormMaker(WebCouponDeliveryFormMaker):
    def __init__(self):
        super(WebCouponDeliveryFormMaker, self).__init__()

    def make_form(self, formdata=None, obj=None, prefix='', **kwargs):
        return RTWebCouponDeliveryMethodForm(formdata=formdata, obj=obj, prefix=prefix, **kwargs)

