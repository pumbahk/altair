# -*- coding:utf-8 -*-
from ..resources import BoosterCartResource
from altair.app.ticketing.cart.helpers import format_number
from .schemas import OrderFormSchema, OrderReviewSchema
from .reflect import form_permissions_from_product, Symbols

"""
メモリアルブックの追加はレギュラー会員より上の人々。値段で分岐するのは筋悪
"""

REGULAR_MEMBER_TYPE_PRICE = 3500 #memorial_book limit
def is_higher_than_regular_member(product):
    return product.price > REGULAR_MEMBER_TYPE_PRICE #too-adhoc

class Bj89ersCartResource(BoosterCartResource):
    def product_form(self, params):
        form = OrderFormSchema(params)
        products = self.product_query.all()
        form.member_type.choices = [(str(p.id), u"%s (%s円)" % (p.name, format_number(p.price, ","))) for p in products]
        permission_dict = {str(p.id):form_permissions_from_product(p, default=[]) for p in products}
        form.permission_dict = permission_dict

        data = form.data
        if "member_type" in data:
            permissions = form.permission_dict.get(data["member_type"], [])
            if Symbols.memorial_book in permissions:
                form.extra.configure_for_memorial_book()
            if Symbols.t_shirts_size in permissions:
                form.extra.configure_for_t_shirts_size()
            if Symbols.official_ball in permissions:
                form.extra.configure_for_official_ball()
            if Symbols.coupon in permissions:
                form.extra.configure_coupon()
        return form

    def orderreview_form(self, params):
        return OrderReviewSchema(params)

    def store_user_profile(self, data):
        k = data.get("member_type")
        product = self.products_dict.get(str(k))
        ## for mobile site
        if not is_higher_than_regular_member(product):
            data["extra"]["memorial_book"] = None
        return super(type(self), self).store_user_profile(data)
