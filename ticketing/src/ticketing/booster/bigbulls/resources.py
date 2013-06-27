# -*- coding:utf-8 -*-
from ..resources import BoosterCartResource
from ticketing.cart.helpers import format_number
from .schemas import OrderFormSchema, OrderReviewSchema
from .reflect import form_permissions_from_product, Symbols
REGULAR_MEMBER_TYPE_PRICE = 3500 #publicity limit
import logging
logger = logging.getLogger(__name__)

from datetime import date
INVALID_AGE = 1900
def get_age(y, m, d):
    try:
        today = date.today()
        birthday = date(int(y), int(m), int(d))
        age = today.year - birthday.year
        if (today.month, today.day) < (birthday.month, birthday.day):
            return age -1
        return age
    except Exception as e:
        logger.warn(str(e))
        return INVALID_AGE #?

class BjbigbullsCartResource(BoosterCartResource):
    def product_form(self, params):
        form = OrderFormSchema(params)
        products = self.product_query.all()
        permission_dict = {str(p.id):form_permissions_from_product(p, default=[]) for p in products}
        form.permission_dict = permission_dict
        form.member_type.choices = [(str(p.id), u"%s (%s円)" % (p.name, format_number(p.price, ","))) for p in products]

        ## after postdata
        data = form.data
        if "member_type" in data:
            permissions = form.permission_dict.get(data["member_type"], [])
            if Symbols.for_kids in permissions:
                form.extra.configure_for_kids()
                form.configure_for_kids(get_age(data["year"], data["month"], data["day"]))
            if Symbols.authentic_uniform in permissions:
                form.extra.configure_for_authentic_uniform()
            if Symbols.replica_uniform in permissions:
                form.extra.configure_for_replica_uniform()
            if Symbols.t_shirts_size in permissions:
                form.extra.configure_for_t_shirts_size()
        return form

    def orderreview_form(self, params):
        return OrderReviewSchema(params)

    def store_user_profile(self, data):
        k = data.get("member_type")
        if k is None:
            return super(type(self), self).store_user_profile(data)

        products = self.product_query.all()
        permission_dict = {str(p.id):form_permissions_from_product(p, default=[]) for p in products}
        ## for mobile site
        if "extra" not in data:
            return super(type(self), self).store_user_profile(data)
        extra = data["extra"]
        permissions = permission_dict.get(k, [])
        if Symbols.for_kids not in permissions:
            extra["parent_first_name"] = None
            extra["parent_first_name_kana"] = None
            extra["parent_last_name"] = None
            extra["parent_last_name_kana"] = None
            extra["relationship"] = None
        if Symbols.authentic_uniform not in permissions:
            extra["authentic_uniform_size"] = None
            extra["authentic_uniform_no"] = None
            extra["authentic_uniform_color"] = None
            extra["authentic_uniform_name"] = None
        if Symbols.replica_uniform not in permissions:
            extra["replica_uniform_size"] = None
        if Symbols.t_shirts_size not in permissions:
            extra["t_shirts_size"] = None
        return super(type(self), self).store_user_profile(data)
