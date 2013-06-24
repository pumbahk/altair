# -*- coding:utf-8 -*-
from ..resources import BoosterCartResource
from ticketing.cart.helpers import format_number
from .schemas import OrderFormSchema, OrderReviewSchema

REGULAR_MEMBER_TYPE_PRICE = 3500 #publicity limit

class BjbigbullsCartResource(BoosterCartResource):
    def product_form(self, params):
        form = OrderFormSchema(params)
        query = self.product_query
        choices = [(str(p.id), u"%s (%s円)" % (p.name, format_number(p.price, ","))) for p in query]
        form.member_type.choices = choices
        return form

    def orderreview_form(self, params):
        return OrderReviewSchema(params)

    def store_user_profile(self, data):
        k = data.get("member_type")
        product = self.products_dict.get(str(k))
        ## for mobile site
        if product.price <= REGULAR_MEMBER_TYPE_PRICE: #too-adhoc
            data["extra"]["publicity"] = None
        return super(type(self), self).store_user_profile(data)
