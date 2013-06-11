# -*- coding:utf-8 -*-
from ..resources import BoosterCartResource
from ticketing.cart.helpers import format_number
from .schemas import OrderFormSchema, OrderReviewSchema

class Bj89ersCartResource(BoosterCartResource):
    def product_form(self, params):
        form = OrderFormSchema(params)
        query = self.product_query
        choices = [(str(p.id), u"%s (%s円)" % (p.name, format_number(p.price, ","))) for p in query]
        form.member_type.choices = choices
        return form

    def orderreview_form(self, params):
        return OrderReviewSchema(params)


