# -*- coding:utf-8 -*-
from ..resources import BoosterCartResource
from ticketing.cart.helpers import format_number
from ticketing.core.models import DeliveryMethod
import logging
logger = logging.getLogger(__name__)
from .schemas import OrderFormSchema, OrderReviewSchema

class BjBambitiousCartResource(BoosterCartResource):
    def product_form(self, params):
        form = OrderFormSchema(params)
        query = self.product_query
        choices = [(str(p.id), u"%s (%s円)" % (p.name, format_number(p.price, ","))) for p in query]
        form.member_type.choices = choices
        pdmps = self.sales_segment.payment_delivery_method_pairs
        dms = set(pdmp.delivery_method for pdmp in pdmps)
        form.product_delivery_method.choices = [(str(dm.id), dm.name) for dm in dms]
        return form

    def load_user_profile(self):
        pm = super(type(self), self).load_user_profile()
        if pm is None:
            return pm
        dm_id = pm.get("product_delivery_method") 
        if dm_id:
            pm["product_delivery_method_name"] = DeliveryMethod.query.filter_by(id=dm_id).first().name()
        return pm

    def orderreview_form(self, params):
        return OrderReviewSchema(params)

    def available_payment_delivery_method_pairs(self, sales_segment):
        pdmps = super(type(self), self).available_payment_delivery_method_pairs(sales_segment)
        ##xxx:
        profile = self.load_user_profile()
        if profile is None:
            logger.warn("session,  user profile is none")
            return pdmps
        delivery_method_id = profile.get("product_delivery_method", None)
        if delivery_method_id is None:
            logger.warn("session,  stored value is not found. (product_delivery_method) ")
            return pdmps
        return [pdmp for pdmp in pdmps if unicode(pdmp.delivery_method_id)== delivery_method_id]

