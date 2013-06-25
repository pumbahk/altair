# -*- coding:utf-8 -*-
from ..resources import BoosterCartResource
from ticketing.cart.helpers import format_number
from .schemas import OrderFormSchema, OrderReviewSchema
from .reflect import form_permissions_from_product

REGULAR_MEMBER_TYPE_PRICE = 3500 #publicity limit

class BjbigbullsCartResource(BoosterCartResource):
    def product_form(self, params):
        form = OrderFormSchema(params)
        products = self.product_query.all()
        choices = [(str(p.id), u"%s (%s円)" % (p.name, format_number(p.price, ","))) for p in products]
        form.permission_dict = {str(p.id):form_permissions_from_product(p, default=[]) for p in products}
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
