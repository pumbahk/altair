# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.fanstatic import with_bootstrap
from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.views import BaseView
from ticketing.products.forms import PaymentDeliveryMethodPairForm, ProductForm, SalesSegmentForm
from ticketing.products.models import PaymentDeliveryMethodPair, Product, ProductItem, SalesSegment, Stock
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
        print self.request.body
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

        f = ProductForm(self.request.POST, organization_id=self.context.user.organization_id)
        if f.validate():
            product = merge_session_with_post(product, f.data)
            product.save()

            product_item = ProductItem()
            product_item.stocks = [Stock.get(self.request.POST.get('stock_id'))]
            product_item.performance_id = performance_id
            product_item.product_id = product_id
            product_item.save()

            self.request.session.flash(u'商品を保存しました')
            return {'success':True}
        else:
            return {'success':False}


@view_defaults(decorator=with_bootstrap)
class ProductSegments(BaseView):

    @view_config(route_name='products.sales_segments', renderer='ticketing:templates/products_segments/index.html')
    def index(self):
        sales_segments = SalesSegment.get_by_organization_id(self.context.user.organization_id)
        form_ss = SalesSegmentForm()
        return {
            'form_ss':form_ss,
            'sales_segments':sales_segments,
        }

    @view_config(route_name='products.sales_segments.show', renderer='ticketing:templates/products_segments/show.html')
    def show(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = SalesSegment.get(sales_segment_id)
        if sales_segment is None:
            return HTTPNotFound('sales_segment id %d is not found' % sales_segment_id)

        form_ss = SalesSegmentForm()
        form_ss.process(record_to_multidict(sales_segment))
        return {
            'form_ss':form_ss,
            'form_pdmp':PaymentDeliveryMethodPairForm(),
            'sales_segment':sales_segment,
        }

    @view_config(route_name='products.sales_segments.new', request_method='POST')
    def new_post(self):
        f = SalesSegmentForm(self.request.POST)
        if f.validate():
            sales_segment = merge_session_with_post(SalesSegment(), f.data)
            sales_segment.organization_id = self.context.user.organization_id
            sales_segment.save()
            self.request.session.flash(u'販売区分を保存しました')

        return HTTPFound(location=route_path('products.sales_segments.show', self.request, sales_segment_id=sales_segment.id))

    @view_config(route_name='products.sales_segments.edit', request_method='POST')
    def edit_post(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = SalesSegment.get(sales_segment_id)
        if sales_segment is None:
            return HTTPNotFound('sales_segment id %d is not found' % sales_segment_id)

        f = SalesSegmentForm(self.request.POST)
        if f.validate():
            sales_segment = merge_session_with_post(sales_segment, f.data)
            sales_segment.save()
            self.request.session.flash(u'販売区分を保存しました')

        return HTTPFound(location=route_path('products.sales_segments.show', self.request, sales_segment_id=sales_segment.id))

    @view_config(route_name='products.sales_segments.delete')
    def delete(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = SalesSegment.get(sales_segment_id)
        if sales_segment is None:
            return HTTPNotFound('sales_segment id %d is not found' % sales_segment_id)

        sales_segment.delete()

        self.request.session.flash(u'販売区分を削除しました')
        return HTTPFound(location=route_path('products.sales_segments', self.request))


@view_defaults(decorator=with_bootstrap)
class PaymentDeliveryMethodPairs(BaseView):

    @view_config(route_name='products.payment_delivery_method_pair.new', request_method='GET', renderer='ticketing:templates/payment_delivery_method_pair/edit.html')
    def new_get(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = SalesSegment.get(sales_segment_id)

        f = PaymentDeliveryMethodPairForm(organization_id=self.context.user.organization_id)
        f.sales_segment_id.data = sales_segment_id
        return {
            'form':f,
            'sales_segment':sales_segment
        }

    @view_config(route_name='products.payment_delivery_method_pair.new', request_method='POST', renderer='ticketing:templates/payment_delivery_method_pair/edit.html')
    def new_post(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = SalesSegment.get(sales_segment_id)
        if sales_segment is None:
            return HTTPNotFound('sales_segment id %d is not found' % sales_segment_id)

        f = PaymentDeliveryMethodPairForm(self.request.POST, organization_id=self.context.user.organization_id)
        if f.validate():
            for payment_method_id in f.data['payment_method_ids']:
                for delivery_method_id in f.data['delivery_method_ids']:
                    payment_delivery_method_pair = merge_session_with_post(PaymentDeliveryMethodPair(), f.data)
                    payment_delivery_method_pair.sales_segment_id = sales_segment_id
                    payment_delivery_method_pair.payment_method_id = payment_method_id
                    payment_delivery_method_pair.delivery_method_id = delivery_method_id
                    payment_delivery_method_pair.save()

            self.request.session.flash(u'販売区分を登録しました')
            return HTTPFound(location=route_path('products.sales_segments.show', self.request, sales_segment_id=sales_segment.id))
        else:
            return {
                'form':f,
                'sales_segment':sales_segment,
            }

    @view_config(route_name='products.payment_delivery_method_pair.edit', request_method='GET', renderer='ticketing:templates/payment_delivery_method_pair/edit.html')
    def edit_get(self):
        id = int(self.request.matchdict.get('payment_delivery_method_pair_id', 0))
        pdmp = PaymentDeliveryMethodPair.get(id)
        if pdmp is None:
            return HTTPNotFound('payment_delivery_method_pair id %d is not found' % id)

        f = PaymentDeliveryMethodPairForm(organization_id=self.context.user.organization_id)
        f.process(record_to_multidict(pdmp))
        f.payment_method_ids.data = [pdmp.payment_method_id]
        f.delivery_method_ids.data = [pdmp.delivery_method_id]
        return {
            'form':f,
            'payment_delivery_method_pair':pdmp
        }

    @view_config(route_name='products.payment_delivery_method_pair.edit', request_method='POST', renderer='ticketing:templates/payment_delivery_method_pair/edit.html')
    def edit_post(self):
        id = int(self.request.matchdict.get('payment_delivery_method_pair_id', 0))
        pdmp = PaymentDeliveryMethodPair.get(id)
        if pdmp is None:
            return HTTPNotFound('payment_delivery_method_pair id %d is not found' % id)

        f = PaymentDeliveryMethodPairForm(self.request.POST, organization_id=self.context.user.organization_id)
        f.id.data = id
        f.payment_method_ids.data = [pdmp.payment_method_id]
        f.delivery_method_ids.data = [pdmp.delivery_method_id]
        if f.validate():
            payment_delivery_method_pair = merge_session_with_post(PaymentDeliveryMethodPair(), f.data)
            payment_delivery_method_pair.save()

            self.request.session.flash(u'販売区分を登録しました')
            return HTTPFound(location=route_path('products.sales_segments.show', self.request, sales_segment_id=pdmp.sales_segment_id))
        else:
            return {
                'form':f,
                'payment_delivery_method_pair':pdmp
            }

    @view_config(route_name='products.payment_delivery_method_pair.delete')
    def delete(self):
        id = int(self.request.matchdict.get('payment_delivery_method_pair_id', 0))
        pdmp = PaymentDeliveryMethodPair.get(id)
        if pdmp is None:
            return HTTPNotFound('payment_delivery_method_pair id %d is not found' % id)

        pdmp.delete()

        self.request.session.flash(u'販売区分を削除しました')
        return HTTPFound(location=route_path('products.sales_segments.show', self.request, sales_segment_id=pdmp.sales_segment_id))

    @view_config(route_name='products.payment_delivery_method_pair.list', renderer='json')
    def list(self):
        return {
            'delivery_method_list' : self.context.user.organization.delivery_method_list,
            'payment_method_list' : self.context.user.organization.payment_method_list
        }
