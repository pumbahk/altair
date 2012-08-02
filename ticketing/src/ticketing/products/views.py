# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from ticketing.fanstatic import with_bootstrap
from ticketing.models import merge_session_with_post
from ticketing.views import BaseView
from ticketing.core.models import Product, ProductItem, Event, Performance
from ticketing.products.forms import ProductForm, ProductItemForm

@view_defaults(decorator=with_bootstrap)
class Products(BaseView):

    @view_config(route_name='products.index', renderer='ticketing:templates/products/index.html')
    def index(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        sort = self.request.GET.get('sort', 'Product.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        conditions = {
            'event_id':event.id
        }
        query = Product.filter_by(**conditions)
        query = query.order_by(sort + ' ' + direction)

        products = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':ProductForm(event_id=event.id),
            'products':products,
            'event':event,
        }

    @view_config(route_name='products.new', request_method='POST', renderer='ticketing:templates/products/_form.html')
    def new_post(self):
        event_id = int(self.request.POST.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = ProductForm(self.request.POST, event_id=event.id)
        if f.validate():
            product = merge_session_with_post(Product(), f.data)
            product.save()

            self.request.session.flash(u'商品を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='products.edit', request_method='POST', renderer='ticketing:templates/products/_form.html')
    def edit_post(self):
        product_id = int(self.request.matchdict.get('product_id', 0))
        product = Product.get(product_id)
        if product is None:
            return HTTPNotFound('product id %d is not found' % product_id)

        f = ProductForm(self.request.POST, event_id=product.event_id)
        if f.validate():
            product = merge_session_with_post(product, f.data)
            product.save()

            self.request.session.flash(u'商品を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='products.delete', renderer='ticketing:templates/products/_form.html')
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

    @view_config(route_name='product_items.new', request_method='POST', renderer='ticketing:templates/product_items/_form.html')
    def new_post(self):
        product_id = int(self.request.POST.get('product_id', 0))
        product = Product.get(product_id)
        if product is None:
            return HTTPNotFound('product id %d is not found' % product_id)

        performance_id = int(self.request.POST.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        f = ProductItemForm(self.request.POST, user_id=self.context.user.id, performance_id=performance_id)
        if f.validate():
            product_item = merge_session_with_post(ProductItem(), f.data)
            product_item.save()

            self.request.session.flash(u'商品を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'form_product':ProductForm(event_id=performance.event_id),
                'performance':performance,
            }

    @view_config(route_name='product_items.edit', request_method='POST', renderer='ticketing:templates/product_items/_form.html')
    def edit_post(self):
        product_item_id = int(self.request.matchdict.get('product_item_id', 0))
        product_item = ProductItem.get(product_item_id)
        if product_item is None:
            return HTTPNotFound('product_item id %d is not found' % product_item_id)

        performance_id = int(self.request.POST.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        f = ProductItemForm(self.request.POST, user_id=self.context.user.id, performance_id=performance_id)
        if f.validate():
            product_item = merge_session_with_post(product_item, f.data)
            product_item.save()

            self.request.session.flash(u'商品を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'form_product':ProductForm(event_id=performance.event_id),
                'performance':performance,
            }

    @view_config(route_name='product_items.delete', renderer='ticketing:templates/product_items/_form.html')
    def delete(self):
        product_item_id = int(self.request.matchdict.get('product_item_id', 0))
        product_item = ProductItem.get(product_item_id)
        if product_item is None:
            return HTTPNotFound('product_item id %d is not found' % product_item_id)

        performance_id = product_item.performance_id
        product_item.delete()

        self.request.session.flash(u'商品を削除しました')
        return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance_id, _anchor='product'))
