# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from ticketing.views import BaseView

from ticketing.fanstatic import with_bootstrap

@view_defaults(decorator=with_bootstrap)
class Products(BaseView):

    @view_config(route_name='products.index', renderer='ticketing:templates/products/index.html')
    def index(self):
        return {}

@view_defaults(decorator=with_bootstrap)
class ProductSegments(BaseView):
    @view_config(route_name='products.sales_segments', renderer='ticketing:templates/products_segments/index.html')
    def index(self):
        return {}
    @view_config(route_name='products.sales_segments.new', renderer='ticketing:templates/products_segments/index.html')
    def index(self):
        return {}

@view_defaults(decorator=with_bootstrap)
class PaymentDeliveryMethod(BaseView):
    @view_config(route_name='products.payment_delivery_method', renderer='ticketing:templates/delivery_method/index.html')
    def index(self):
        return {}

    @view_config(route_name='products.payment_delivery_method.list', renderer='json')
    def list(self):
        return {
            'delivery_method_list' : self.context.user.client.delivery_method_list,
            'payment_method_list' : self.context.user.client.payment_method_list
        }
