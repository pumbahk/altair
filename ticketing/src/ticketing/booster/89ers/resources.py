# -*- coding:utf-8 -*-
from ..resources import BoosterCartResource
from ticketing.cart.helpers import format_number
from .schemas import OrderFormSchema, OrderReviewSchema
from ..api import filtering_data_by_products_and_member_type

class Bj89ersCartResource(BoosterCartResource):
    def product_form(self, params):
        form = OrderFormSchema(params)
        query = self.product_query
        choices = [(str(p.id), u"%s (%s円)" % (p.name, format_number(p.price, ","))) for p in query]
        form.member_type.choices = choices
        return form

    def orderreview_form(self, params):
        return OrderReviewSchema(params)

    def store_user_profile(self, data):
        data = filtering_data_by_products_and_member_type(data, self.products_dict)
        return super(type(self), self).store_user_profile(data)
