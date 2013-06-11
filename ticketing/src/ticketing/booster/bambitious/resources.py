# -*- coding:utf-8 -*-
from ..resources import BoosterCartResource
from ticketing.cart.helpers import format_number

class BjBambitiousCartResource(BoosterCartResource):
    def product_form(self, formclass,  params):
        form = formclass(params)
        query = self.product_query
        choices = [(str(p.id), u"%s (%s円)" % (p.name, format_number(p.price, ","))) for p in query]
        form.member_type.choices = choices
        return form


