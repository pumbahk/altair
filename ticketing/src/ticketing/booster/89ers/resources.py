import sqlalchemy as sa
from .resources import BoosterCartResource
from ticketing.core.models import Product
from pyramid.decorator import reify
from ticketing.helpers import products_filter_by_salessegment
from ticketing.cart.helpers import format_number

class Bj89ersCartResource(BoosterCartResource):
    @reify 
    def product_query(self):
        query = Product.query
        query = query.filter(Product.event_id == self.event_id)
        query = query.order_by(sa.desc("price"))

        salessegment = self.get_sales_segment()
        return products_filter_by_salessegment(query, salessegment)

    def product_form(self, formclass,  params):
        form = formclass(params)
        query = self.context.product_query
        choices = [(str(p.id), u"%s (%s円)" % (p.name, format_number(p.price, ","))) for p in query]
        form.member_type.choices = choices
        return form


