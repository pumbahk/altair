# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.fanstatic import with_bootstrap
from ticketing.models import merge_session_with_post
from ticketing.views import BaseView
from ticketing.products.models import Product
from ticketing.products.forms import ProductForm

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
        print self.request.body
        return dict()

    @view_config(route_name='products.json.update', renderer='json')
    def json_update(self):
        product_id = int(self.request.matchdict.get('product_id', 0))
        product = Product.get(product_id)
        if product is None:
            return HTTPNotFound('product id %d is not found' % product_id)

        '''
        performance_id = int(self.request.POST.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)
        '''

        f = ProductForm(self.request.POST, event_id=product.event_id)
        if f.validate():
            product = merge_session_with_post(product, f.data)
            product.save()

            '''
            product_item = ProductItem()
            stocks = []
            for stock_id in list(self.request.POST.get('stock_id')):
                stocks.append(Stock.get(stock_id))
            product_item.stocks = stocks
            product_item.performance_id = performance_id
            product_item.product_id = product_id
            product_item.save()
            '''

            self.request.session.flash(u'商品を保存しました')
            return {'success':True}
        else:
            return {'success':False}
