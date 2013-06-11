# -*- coding:utf-8 -*-
from ..resources import BoosterCartResource
from ticketing.cart.helpers import format_number
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

    def orderreview_form(self, params):
        return OrderReviewSchema(params)

    def available_payment_delivery_method_pairs(self, sales_segment):
        pdmps = super(type(self), self).available_payment_delivery_method_pairs(sales_segment)
        ##xxx:
        delivery_method_id = self.request.session.get("delivery_method_id", None)
        if delivery_method_id is None:
            logger.warn("session,  stored value is not found. (delivery_method_id) ")
            return pdmps
        return [pdmp for pdmp in pdmps if pdmp.delivery_method_id == delivery_method_id]

