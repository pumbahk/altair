# -*- coding: utf-8 -*-

import json
import logging
import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.url import route_path
from paste.util.multidict import MultiDict

from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.models import merge_session_with_post, record_to_multidict
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.core.models import Product, ProductItem, Event, Performance, Stock, SalesSegment, SalesSegmentGroup, Organization
from altair.app.ticketing.products.forms import ProductForm, ProductItemForm
from altair.app.ticketing.loyalty.models import PointGrantSetting

logger = logging.getLogger(__name__)


@view_defaults(decorator=with_bootstrap, permission='event_editor')
class Products(BaseView):

    @view_config(route_name='products.index', renderer='altair.app.ticketing:templates/products/index.html')
    def index(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.user.organization_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        # XXX: is this injection safe?
        sort = self.request.GET.get('sort', 'Product.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        conditions = {
            'performance_id': performance.id
            }
        query = Product.filter_by(**conditions)
        query = query.order_by(sort + ' ' + direction)

        products = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=200,
            url=paginate.PageURL_WebOb(self.request)
            )

        return {
            'form': ProductForm(performance=performance),
            'products': products,
            'performance': performance
        }

    @view_config(route_name='products.new', request_method='GET', renderer='altair.app.ticketing:templates/products/_form.html', xhr=True)
    def new_xhr(self):
        try:
            performance_id = long(self.request.params.get('performance_id'))
        except (TypeError, ValueError):
            performance_id = None
        try:
            sales_segment_id = long(self.request.params.get('sales_segment_id'))
        except (TypeError, ValueError):
            sales_segment_id = None

        performance = sales_segment = None

        if sales_segment_id is not None:
            sales_segment = SalesSegment.query.filter_by(id=sales_segment_id).filter(Organization.id==self.context.user.organization_id).one()
            if sales_segment is None:
                return HTTPNotFound('sales_segment id %d is not found' % sales_segment_id)

        if performance_id is not None:
            performance = Performance.get(performance_id, self.context.user.organization_id)
            if performance is None:
                return HTTPNotFound('performance id %d is not found' % performance_id)

        f = ProductForm(performance=performance, sales_segment=sales_segment, applied_point_grant_settings=(sales_segment and [pgs.id for pgs in sales_segment.point_grant_settings]))
        return {
            'form': f,
            'action': self.request.path,
            }


    @view_config(route_name='products.new', request_method='POST', renderer='altair.app.ticketing:templates/products/_form.html', xhr=True)
    def new_post_xhr(self):
        try:
            performance_id = long(self.request.params.get('performance_id'))
        except (TypeError, ValueError):
            performance_id = None
        try:
            sales_segment_id = long(self.request.params.get('sales_segment_id'))
        except (TypeError, ValueError):
            sales_segment_id = None

        performance = sales_segment = None

        if sales_segment_id is not None:
            sales_segment = SalesSegment.query.filter_by(id=sales_segment_id).filter(Organization.id==self.context.user.organization_id).one()
            if sales_segment is None:
                return HTTPNotFound('sales_segment id %d is not found' % sales_segment_id)

        if performance_id is not None:
            performance = Performance.get(performance_id, self.context.user.organization_id)
            if performance is None:
                return HTTPNotFound('performance id %d is not found' % performance_id)
            
        f = ProductForm(self.request.POST, performance=performance, sales_segment=sales_segment)
        if f.validate():
            point_grant_settings = [PointGrantSetting.query.filter_by(id=point_grant_setting_id, organization_id=self.context.user.organization_id).one() for point_grant_setting_id in f.applied_point_grant_settings.data]

            if f.all_sales_segment.data and performance:
                sales_segment_for_products = SalesSegment.query.filter(SalesSegment.performance_id==performance.id).filter(Organization.id==self.context.user.organization_id)
                for sales_segment_for_product in sales_segment_for_products:
                    product = merge_session_with_post(Product(), f.data)
                    product.sales_segment_id = sales_segment_for_product.id
                    product.performance_id = sales_segment_for_product.performance.id
                    product.point_grant_settings.extend(point_grant_settings)
                    product.save()
            else:
                sales_segment_for_product = SalesSegment.query.filter_by(id=f.sales_segment_id.data).filter(Organization.id==self.context.user.organization_id).one()
                product = merge_session_with_post(Product(), f.data)
                product.performance_id = sales_segment_for_product.performance.id
                product.point_grant_settings.extend(point_grant_settings)
                product.save()

            self.request.session.flash(u'商品を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form': f,
                'action': self.request.path,
                }

    @view_config(route_name="products.edit", request_method="GET", renderer='altair.app.ticketing:templates/products/_form_edit.html', xhr=True)
    def edit_xhr(self):
        product_id = int(self.request.matchdict.get('product_id', 0))
        product = Product.get(product_id)
        if product is None:
            raise HTTPNotFound('product id %d is not found' % product_id)
        f = ProductForm.from_model(product)

        return {
            'form':f,
            'action': self.request.path,
            }

    @view_config(route_name='products.edit', request_method='POST', renderer='altair.app.ticketing:templates/products/_form_edit.html', xhr=True)
    def edit_post_xhr(self):
        product_id = int(self.request.matchdict.get('product_id', 0))
        product = Product.get(product_id)

        if product is None:
            return HTTPNotFound('product id %d is not found' % product_id)

        f = ProductForm(self.request.POST, sales_segment=product.sales_segment)
        if f.validate():
            point_grant_settings = [PointGrantSetting.query.filter_by(id=point_grant_setting_id, organization_id=self.context.user.organization_id).one() for point_grant_setting_id in f.applied_point_grant_settings.data]
            product = merge_session_with_post(product, f.data, excludes={'performance_id'})
            product.point_grant_settings[:] = []
            product.point_grant_settings.extend(point_grant_settings)
            product.save()

            self.request.session.flash(u'商品を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form': f,
                'action': self.request.path,
                }

    @view_config(route_name='products.delete', renderer='altair.app.ticketing:templates/products/_form.html')
    def delete(self):
        product_id = int(self.request.matchdict.get('product_id', 0))
        product = Product.get(product_id)
        if product is None:
            return HTTPNotFound('product id %d is not found' % product_id)

        location = route_path('products.index', self.request, performance_id=product.sales_segment.performance_id)
        try:
            product.delete()
            self.request.session.flash(u'商品を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)

    @view_config(route_name='products.api.get', renderer='json')
    def api_get(self):
        sales_segment_id = self.request.params.get('sales_segment_id', 0)
        products = Product.query.filter_by(sales_segment_id=sales_segment_id).order_by(Product.display_order).all()
        if not products:
            raise HTTPBadRequest(body=json.dumps({'message':u'データが見つかりません'}))

        rows = []
        for product in products:
            row = dict(
                product=dict(
                    id=product.id,
                    name=product.name,
                    price=int(product.price),
                    order=product.display_order,
                    public=product.public
                ),
                stock_type=dict(
                    id=product.seat_stock_type.id
                ),
                parent='null',  # need for sorting
            )
            product_items = product.items

            for i, product_item in enumerate(product_items):
                row2 = row.copy()
                row2.update(
                    stock_holder=dict(
                        id=product_item.stock.stock_holder.id,
                    ),
                    product_item=dict(
                        id=product_item.id,
                        name=product_item.name,
                        price=int(product_item.price),
                        quantity=product_item.quantity,
                    ),
                    stock=dict(
                        id=product_item.stock.id,
                        quantity=product_item.stock.quantity,
                    ),
                    stock_status=dict(
                        quantity=product_item.stock.stock_status.quantity,
                    ),
                    stock_type=dict(
                        id=product_item.stock.stock_type.id
                    ),
                    ticket_bundle=dict(
                        id=product_item.ticket_bundle.id if product_item.ticket_bundle else '',
                    ),
                )
                # 1つのProductに複数のProductItemが紐づいているケースはtree表示
                if len(product_items) > 1:
                    if i == 0:
                        row2.update(
                            parent='null',
                            level=0,
                            isLeaf=False,
                            expanded=True,
                            loaded=True
                        )
                    else:
                        row2.update(
                            parent=product_items[0].id,
                            level=1,
                            isLeaf=True,
                            expanded=True,
                            loaded=True,
                            product=dict(
                                id=product.id,
                                name=u'(複数在庫商品)',
                            ),
                        )
                rows.append(row2)
            if not product_items:
                rows.append(row)

        return {
            'page':self.request.params.get('page', 1),
            'total':len(rows),
            'records':len(rows),
            'rows':rows
        }

    @view_config(route_name='products.api.set', renderer='json')
    def api_set(self):
        performance_id = int(self.request.params.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.organization.id)
        sales_segment_id = int(self.request.params.get('sales_segment_id'), 0)
        sales_segment = SalesSegment.query \
            .join(SalesSegment.sales_segment_group) \
            .join(SalesSegmentGroup.event) \
            .filter(SalesSegment.id==sales_segment_id) \
            .filter(Event.organization_id == self.context.organization.id) \
            .first()

        if performance is None and sales_segment is None:
            logger.warning('performance id %d is not found' % performance_id)
            raise HTTPBadRequest(body=json.dumps({
                'message':u'パフォーマンスが存在しません',
            }))

        json_data = self.request.json_body
        if not json_data:
            raise HTTPBadRequest(body=json.dumps({'message':u'保存するデータがありません'}))

        for row_data in json_data:
            row_data = MultiDict(row_data)

            if row_data.get('product_item_id'):
                product_item_id = int(row_data.get('product_item_id', 0))
                product_item = ProductItem.get(product_item_id)
            else:
                product_item = ProductItem()
            if product_item is None:
                raise HTTPBadRequest(body=json.dumps({'message':u'不正なデータです'}))

            if row_data.get('deleted'):
                try:
                    product_item.delete()
                except Exception, e:
                    logger.info(row_data)
                    logger.info('validation error:%s' % e.message)
                    raise HTTPBadRequest(body=json.dumps({
                        'message':u'入力データを確認してください',
                        'rows':{'rowid':row_data.get('id'), 'errors':[e.message]}
                    }))
            else:
                product_id = row_data['product_id']
                product = Product.query.filter(Product.id==product_id).one()

                f = ProductItemForm(row_data, performance_id=product.performance.id, product=product)
                if not f.validate():
                    logger.info('validation error:%s' % f.errors)
                    raise HTTPBadRequest(body=json.dumps({
                        'message':u'入力データを確認してください',
                        'rows':{'rowid':row_data.get('id'), 'errors':f.errors}
                    }))

                stock = Stock.query.filter_by(
                    stock_type_id=f.stock_type_id.data,
                    stock_holder_id=f.stock_holder_id.data,
                    performance_id=product.performance.id
                ).one()
                product_item.performance_id = product.performance.id
                product_item.product_id = product.id
                product_item.name = f.product_item_name.data
                product_item.price = f.product_item_price.data
                product_item.quantity = f.product_item_quantity.data
                product_item.stock_id = stock.id
                product_item.ticket_bundle_id = f.ticket_bundle_id.data
                product_item.save()

        return {}


@view_defaults(decorator=with_bootstrap, permission='event_editor')
class ProductItems(BaseView):

    @view_config(route_name='product_items.new', request_method='GET', renderer='altair.app.ticketing:templates/product_items/_form.html', xhr=True)
    def new_xhr(self):
        product_id = int(self.request.matchdict.get('product_id', 0))
        product = Product.query.filter_by(id=product_id).filter(Organization.id==self.context.user.organization_id).one()

        default = MultiDict(
            stock_type_id=product.seat_stock_type_id,
            product_item_name=product.name,
            product_item_price=int(product.price),
            product_item_quantity=1
        )
        f = ProductItemForm(default, product=product)
        return {
            'form':f,
            'form_product':ProductForm(
                record_to_multidict(product),
                sales_segment=product.sales_segment),
            'action':self.request.path,
            }

    @view_config(route_name='product_items.new', request_method='POST', renderer='altair.app.ticketing:templates/product_items/_form.html', xhr=True)
    def new_post_xhr(self):
        product_id = int(self.request.matchdict.get('product_id', 0))
        product = Product.get(product_id)
        if product is None:
            return HTTPNotFound('product id %d is not found' % product_id)

        f = ProductItemForm(self.request.POST, product=product)
        if f.validate():
            stock = Stock.query.filter_by(
                stock_type_id=f.stock_type_id.data,
                stock_holder_id=f.stock_holder_id.data,
                performance_id=product.sales_segment.performance.id
            ).one()
            product_item = ProductItem(
                performance_id=product.sales_segment.performance.id,
                product_id=f.product_id.data,
                name=f.product_item_name.data,
                price=f.product_item_price.data,
                quantity=f.product_item_quantity.data,
                stock_id=stock.id,
                ticket_bundle_id=f.ticket_bundle_id.data
            )
            product_item.save()

            self.request.session.flash(u'商品に在庫を割当てました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'form_product':ProductForm(
                    record_to_multidict(product),
                    sales_segment=product.sales_segment),
                'action':self.request.path,
            }

    @view_config(route_name='product_items.edit', request_method='GET', renderer='altair.app.ticketing:templates/product_items/_form.html', xhr=True)
    def edit_xhr(self):
        product_item_id = int(self.request.matchdict.get('product_item_id', 0))
        product_item = ProductItem.query.filter_by(id=product_item_id).filter(Organization.id==self.context.user.organization_id).one()

        params = MultiDict(
            product_item_id=product_item.id,
            product_item_name=product_item.name,
            product_item_price=int(product_item.price),
            product_item_quantity=product_item.quantity,
            stock_type_id=product_item.stock.stock_type_id,
            stock_holder_id=product_item.stock.stock_holder_id,
            ticket_bundle_id=product_item.ticket_bundle_id
        )
        f = ProductItemForm(params, product=product_item.product)
        return {
            'form': f,
            'form_product':ProductForm(
                record_to_multidict(product_item.product),
                sales_segment=product_item.product.sales_segment),
            'action': self.request.path,
        }

    @view_config(route_name='product_items.edit', request_method='POST', renderer='altair.app.ticketing:templates/product_items/_form.html', xhr=True)
    def edit_post_xhr(self):
        product_item_id = int(self.request.matchdict.get('product_item_id', 0))
        product_item = ProductItem.query.filter_by(id=product_item_id).filter(Organization.id==self.context.user.organization_id).one()

        f = ProductItemForm(self.request.POST, product=product_item.product)
        if f.validate():
            stock = Stock.query.filter_by(
                stock_type_id=f.stock_type_id.data,
                stock_holder_id=f.stock_holder_id.data,
                performance_id=product_item.product.sales_segment.performance.id
            ).one()
            product_item = merge_session_with_post(product_item, dict(
                product_id=f.product_id.data,
                name=f.product_item_name.data,
                price=f.product_item_price.data,
                quantity=f.product_item_quantity.data,
                stock_id=stock.id,
                ticket_bundle_id=f.ticket_bundle_id.data
            ))
            product_item.save()

            self.request.session.flash(u'商品明細を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'form_product':ProductForm(
                    record_to_multidict(product_item.product),
                    sales_segment=product_item.product.sales_segment),
                'action':self.request.path,
            }

    @view_config(route_name='product_items.delete', renderer='altair.app.ticketing:templates/product_items/_form.html')
    def delete(self):
        product_item_id = int(self.request.matchdict.get('product_item_id', 0))
        product_item = ProductItem.query.filter_by(id=product_item_id).filter(Organization.id==self.context.user.organization_id).one()

        location = route_path('performances.show', self.request, performance_id=product_item.performance_id, _anchor='product')
        try:
            product_item.delete()
            self.request.session.flash(u'商品から在庫の割当を外しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)
