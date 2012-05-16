# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.fanstatic import with_bootstrap
from ticketing.models import merge_session_with_post
from ticketing.views import BaseView
from ticketing.products.models import Product, ProductItem
from ticketing.products.forms import ProductForm, ProductItemForm
from ticketing.events.models import Event, Performance

@view_defaults(decorator=with_bootstrap)
class Products(BaseView):

    @view_config(route_name='products.index', renderer='ticketing:templates/products/index.html')
    def index(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        return {
            'event':event,
        }

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
                    'stock_type_id'  : item.stock_type_id,
                    'stock_type'     : item.stock_type
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
        event_id = int(self.request.POST.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = ProductForm(self.request.POST, event_id=event.id)
        if f.validate():
            product = merge_session_with_post(Product(), f.data)
            product.save()

            self.request.session.flash(u'商品を保存しました')
            return {'success':True}
        else:
            return {'success':False}

    @view_config(route_name='products.json.update', renderer='json')
    def json_update(self):
        product_id = int(self.request.matchdict.get('product_id', 0))
        product = Product.get(product_id)
        if product is None:
            return HTTPNotFound('product id %d is not found' % product_id)

        f = ProductForm(self.request.POST, event_id=product.event_id)
        if f.validate():
            product = merge_session_with_post(product, f.data)
            product.save()

            self.request.session.flash(u'商品を保存しました')
            return {'success':True}
        else:
            return {'success':False}

    @view_config(route_name='products.delete')
    def delete(self):
        product_id = int(self.request.matchdict.get('product_id', 0))
        product = Product.get(product_id)
        if product is None:
            return HTTPNotFound('product id %d is not found' % product_id)

        event_id = product.event_id
        product.delete()

        self.request.session.flash(u'商品を削除しました')
        return HTTPFound(location=route_path('products.index', self.request, event_id=event_id))


@view_defaults(decorator=with_bootstrap)
class ProductItems(BaseView):

    @view_config(route_name='products.json.new_item', renderer='json')
    def json_new_item(self):
        product_id = int(self.request.POST.get('product_id', 0))
        product = Product.get(product_id)
        if product is None:
            return HTTPNotFound('product id %d is not found' % product_id)

        performance_id = int(self.request.POST.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        f = ProductItemForm(self.request.POST)
        if f.validate():
            product_item = merge_session_with_post(ProductItem(), f.data)
            product_item.save()

            self.request.session.flash(u'商品を保存しました')
            return {'success':True}
        else:
            return {'success':False}

    @view_config(route_name='products.json.edit_item', renderer='json')
    def json_edit_item(self):
        product_item_id = int(self.request.matchdict.get('product_item_id', 0))
        product_item = ProductItem.get(product_item_id)
        if product_item is None:
            return HTTPNotFound('product_item id %d is not found' % product_item_id)

        performance_id = int(self.request.POST.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        f = ProductItemForm(self.request.POST)
        if f.validate():
            product_item = merge_session_with_post(product_item, f.data)
            product_item.save()

            self.request.session.flash(u'商品を保存しました')
            return {'success':True}
        else:
            return {'success':False}

    @view_config(route_name='products.delete_item')
    def delete(self):
        product_item_id = int(self.request.matchdict.get('product_item_id', 0))
        product_item = ProductItem.get(product_item_id)
        if product_item is None:
            return HTTPNotFound('product_item id %d is not found' % product_item_id)

        performance_id = product_item.performance_id
        product_item.delete()

        self.request.session.flash(u'商品を削除しました')
        return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance_id, _anchor='product'))
