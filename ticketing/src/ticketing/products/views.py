# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from ticketing.views import BaseView

from ticketing.fanstatic import with_bootstrap
from models import Product, ProductItem

@view_defaults(decorator=with_bootstrap)
class Products(BaseView):

    @view_config(route_name='products.index', renderer='ticketing:templates/products/index.html')
    def index(self):
        return {}

    @view_config(route_name='products.json.list', renderer='json')
    def json_list(self):
        '''
        '''
        performance_id  = self.request.GET.get('performance_id')
        list = Product.find(performance_id=performance_id)

        def product_items(items):
            return [
                {
                    'price'         : item.price,
                    'seat_type_id'  : item.seat_type_id,
                    'seat_type'     : item.seat_type
                } for item in items
            ]
        products = [
            {
                'name'          : row.name,
                'price'         : row.price,
                'product_items' : product_items(row.items)
            } for row in list]

        return {
            'products' : products
        }

    @view_config(route_name='products.json.show', renderer='json')
    def json_show(self):
        return dict()
    @view_config(route_name='products.json.new', renderer='json')
    def json_new(self):
        return dict()
    @view_config(route_name='products.json.update', renderer='json')
    def json_update(self):
        return dict()

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
            'delivery_method_list' : self.context.user.organization.delivery_method_list,
            'payment_method_list' : self.context.user.organization.payment_method_list
        }
