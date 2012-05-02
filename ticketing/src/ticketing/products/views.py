# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from ticketing.fanstatic import with_bootstrap
from ticketing.models import merge_session_with_post
from ticketing.views import BaseView
from ticketing.products.forms import PaymentDeliveryMethodPairForm, ProductForm
from ticketing.products.models import session, Product, SalesSegment, SalesSegmentSet
from ticketing.events.models import Performance

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
        product_id = int(self.request.matchdict.get('product_id', 0))
        product = Product.get(product_id)
        if product is None:
            return HTTPNotFound('product id %d is not found' % product_id)

        performance_id = int(self.request.POST.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        f = ProductForm(self.request.POST)
        if f.validate():
            record = merge_session_with_post(product, f.data)
            Product.update(record)

            sales_segment_set = SalesSegmentSet.find_by_product_id(product.id) or SalesSegmentSet()
            sales_segment_set.sales_segment_id = int(self.request.POST.get('sales_segment_id'))
            sales_segment_set.product_id = product.id
            sales_segment_set.event_id = performance.event_id
            SalesSegmentSet.update(sales_segment_set)

            self.request.session.flash(u'商品を保存しました')
            return {'success':True}
        else:
            return {'success':False}


@view_defaults(decorator=with_bootstrap)
class ProductSegments(BaseView):

    @view_config(route_name='products.sales_segments', renderer='ticketing:templates/products_segments/index.html')
    def index(self):
        sales_segments = session.query(SalesSegment).all()
        return {
            'sales_segments':sales_segments,
        }

    @view_config(route_name='products.sales_segments.show', renderer='ticketing:templates/products_segments/show.html')
    def show(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = session.query(SalesSegment).filter(SalesSegment.id == sales_segment_id).first()
        return {
            'sales_segment':sales_segment,
        }

    @view_config(route_name='products.sales_segments.new', request_method='GET', renderer='ticketing:templates/products_segments/edit.html')
    def new_get(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = session.query(SalesSegment).filter(SalesSegment.id == sales_segment_id).first()

        f = PaymentDeliveryMethodPairForm()
        return {
            'form':f,
            'sales_segment':sales_segment,
        }

    @view_config(route_name='products.sales_segments.new', request_method='POST', renderer='ticketing:templates/products_segments/edit.html')
    def new_post(self):
        pass


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
