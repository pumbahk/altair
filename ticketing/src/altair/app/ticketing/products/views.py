# -*- coding: utf-8 -*-

import json
import logging
import webhelpers.paginate as paginate
import sqlalchemy.orm as orm
from sqlalchemy import func
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.url import route_path
from paste.util.multidict import MultiDict
from altair.sqlahelper import get_db_session
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.models import merge_session_with_post, record_to_multidict
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.core.models import Product, ProductItem, Event, Performance, Stock, SalesSegment, SalesSegmentGroup, Organization, StockHolder, TicketBundle
from altair.app.ticketing.products.forms import ProductItemForm, ProductAndProductItemForm, ProductAndProductItemAPIForm, ProductCopyForm
from altair.app.ticketing.loyalty.models import PointGrantSetting
from altair.app.ticketing.utils import moderate_name_candidates
from .forms import PreviewImageDownloadForm
from decimal import Decimal

logger = logging.getLogger(__name__)


@view_defaults(decorator=with_bootstrap, permission='event_editor')
class ProductAndProductItem(BaseView):

    @view_config(route_name='products.new', request_method='GET', renderer='altair.app.ticketing:templates/products/_form.html', xhr=True)
    def new_xhr(self):
        # 商品、商品明細一括登録画面
        sales_segment = self.context.sales_segment
        f = ProductAndProductItemForm(sales_segment=sales_segment, new_form=True)

        ticket_bundles = TicketBundle.query.filter_by(event_id=sales_segment.sales_segment_group.event_id).all()
        if len(ticket_bundles) == 1:
            f.ticket_bundle_id.data = ticket_bundles[0].id

        return dict(form=f)

    @view_config(route_name='products.new', request_method='POST', renderer='altair.app.ticketing:templates/products/_form.html', xhr=True)
    def new_post_xhr(self):
        # 商品、商品明細一括登録画面
        sales_segment = self.context.sales_segment
        f = ProductAndProductItemForm(self.request.POST, sales_segment=sales_segment, new_form=True)
        if f.validate():
            point_grant_settings = [
                PointGrantSetting.query.filter_by(id=point_grant_setting_id, organization_id=self.context.user.organization_id).one()
                for point_grant_setting_id in f.applied_point_grant_settings.data
                ]

            query = SalesSegment.query.filter(Organization.id==self.context.user.organization_id)
            if f.all_sales_segment.data:
                query = query.filter_by(performance_id=f.performance_id.data)
            else:
                query = query.filter_by(id=f.sales_segment_id.data)

            for sales_segment_for_product in query:
                product = merge_session_with_post(Product(), f.data, excludes={'id'})
                max_display_order = Product.query.filter(
                        Product.sales_segment_id==sales_segment_for_product.id
                    ).with_entities(
                        func.max(Product.display_order)
                    ).scalar()
                product.display_order = (max_display_order or 0) + 1
                product.sales_segment = sales_segment_for_product
                product.performance = sales_segment_for_product.performance
                product.point_grant_settings.extend(point_grant_settings)
                product.save()

                stock = Stock.query.filter_by(
                    stock_type_id=f.seat_stock_type_id.data,
                    stock_holder_id=f.stock_holder_id.data,
                    performance_id=sales_segment_for_product.performance.id
                ).one()
                product_item = ProductItem(
                    performance_id=sales_segment_for_product.performance.id,
                    product=product,
                    name=f.name.data,
                    price=f.price.data / f.product_item_quantity.data,
                    quantity=f.product_item_quantity.data,
                    stock_id=stock.id,
                    ticket_bundle_id=f.ticket_bundle_id.data
                )
                product_item.save()

            self.request.session.flash(u'商品を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return dict(form=f)

    @view_config(route_name="products.edit", request_method="GET", renderer='altair.app.ticketing:templates/products/_form.html', xhr=True)
    def edit_xhr(self):
        product = self.context.product
        product_item = self.context.product_item
        f = ProductAndProductItemForm.from_model(product, product_item)
        return dict(form=f)

    @view_config(route_name='products.edit', request_method='POST', renderer='altair.app.ticketing:templates/products/_form.html', xhr=True)
    def edit_post_xhr(self):
        product = self.context.product
        product_item = self.context.product_item
        f = ProductAndProductItemForm(self.request.POST, sales_segment=product.sales_segment)
        if product_item is not None and len(product.items) != 1:
            f.product_item_price.data = product_item.price
        if f.validate():
            point_grant_settings = [
                PointGrantSetting.query.filter_by(id=point_grant_setting_id, organization_id=self.context.user.organization_id).one()
                for point_grant_setting_id in f.applied_point_grant_settings.data
                ]
            product = merge_session_with_post(product, f.data, excludes={'performance_id'})
            product.point_grant_settings[:] = []
            product.point_grant_settings.extend(point_grant_settings)
            product.save()

            if product_item:
                stock = Stock.query.filter_by(
                    stock_type_id=f.seat_stock_type_id.data,
                    stock_holder_id=f.stock_holder_id.data,
                    performance_id=f.performance_id.data
                ).one()
                product_item.name = f.product_item_name.data
                if len(product.items) == 1:
                    product_item.price = f.product_item_price.data
                product_item.quantity = f.product_item_quantity.data
                product_item.stock_id = stock.id
                product_item.ticket_bundle_id = f.ticket_bundle_id.data
                product_item.save()
            else:
                if len(product.items) == 1:
                    product.items[0].price = product.price / product.items[0].quantity
                    product.items[0].save()

            self.request.session.flash(u'商品を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return dict(form=f)

    @view_config(route_name='products.copy', request_method='GET', renderer='altair.app.ticketing:templates/products/_copy_form.html', xhr=True)
    def copy_xhr(self):
        # 商品の販売区分間コピー
        copy_sales_segments = self.context.copy_sales_segments
        f = ProductCopyForm(copy_sales_segments=copy_sales_segments)
        return dict(form=f, origin_sales_segment=self.context.sales_segment)

    @view_config(route_name='products.copy', request_method='POST', renderer='altair.app.ticketing:templates/products/_form.html', xhr=True)
    def copy_post_xhr(self):
        # 商品の販売区分間コピー
        origin_sales_segment = self.context.sales_segment
        form = ProductCopyForm(self.request.POST, origin_sales_segment)
        copy_sales_segments = form['copy_sales_segments'].data

        for copy_sales_segment_id in copy_sales_segments:
            copy_sales_segment = SalesSegment.get(copy_sales_segment_id)
            products = Product.query.filter(Product.sales_segment_id==origin_sales_segment.id).all()

            for product in products:
                new_product = Product.get(Product.create_from_template(template=product, with_product_items=True)[product.id])
                for new_product_name in moderate_name_candidates(new_product.name):
                    existing_product_in_copy_sales_segment = Product.query.filter(
                        Product.sales_segment_id == copy_sales_segment_id,
                        Product.name == new_product_name
                        ).first()
                    if existing_product_in_copy_sales_segment is None:
                        new_product.name = new_product_name
                        break
                new_product.sales_segment = copy_sales_segment
                new_product.sales_segment_id = copy_sales_segment.id

        self.request.session.flash(u'商品をコピーしました')
        return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

    @view_config(route_name='products.delete')
    def delete(self):
        product = self.context.product
        location = self.request.route_path('performances.show_tab', performance_id=product.performance_id, tab='product')
        try:
            product.delete()
            self.request.session.flash(u'商品を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)
        return HTTPFound(location=location)

    @view_config(route_name='products.api.get', renderer='json')
    def api_get(self):
        sales_segment = self.context.sales_segment
        products = Product.query.filter_by(sales_segment_id=sales_segment.id).order_by(Product.display_order).all()
        if not products:
            raise HTTPBadRequest(body=json.dumps({'message':u'データが見つかりません'}))

        rows = []
        parent_id = 0
        for product in products:
            row = dict(
                product=dict(
                    id=product.id,
                    name=product.name,
                    price=int(product.price),
                    display_order=product.display_order,
                    public=product.public,
                    must_be_chosen=product.must_be_chosen,
                    performance_id=product.performance_id,
                    amount_mismatching=product.is_amount_mismatching(),
                ),
                stock_type=dict(
                    id=product.seat_stock_type.id
                ),
                parent='null',  # need for sorting
                level=0,
                is_leaf=False,
                expanded=True,
                loaded=True
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
                        parent_id = len(rows) + 1
                    else:
                        row2.update(
                            parent=parent_id,
                            level=1,
                            is_leaf=True,
                            expanded=True,
                            loaded=True,
                            product=dict(
                                id=product.id,
                                name=u'(複数在庫商品)',
                                performance_id=product.performance_id,
                                amount_mismatching=product.is_amount_mismatching(),
                            ),
                        )
                row2.update(row_id=len(rows) + 1)
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
        sales_segment = self.context.sales_segment
        json_data = self.request.json_body
        if not json_data:
            raise HTTPBadRequest(body=json.dumps({'message':u'保存するデータがありません'}))

        for row_data in json_data:
            row_data = MultiDict(row_data)

            product_id = long(row_data.get('product_id') or 0)
            if product_id:
                product = Product.get(product_id)
            else:
                product = Product()

            product_item_id = long(row_data.get('product_item_id') or 0)
            if product_item_id:
                product_item = ProductItem.get(product_item_id)
            else:
                product_item = ProductItem()

            f = ProductAndProductItemAPIForm(row_data, sales_segment=sales_segment)
            if row_data.get('deleted'):
                try:
                    if f.is_leaf.data:
                        product_item.delete()
                    else:
                        product.delete()
                except Exception, e:
                    logger.info(row_data)
                    logger.info('validation error:%s' % e.message)
                    raise HTTPBadRequest(body=json.dumps({
                        'message':u'入力データを確認してください',
                        'rows':{'rowid':row_data.get('id'), 'errors':[e.message]}
                    }))
            else:
                if not f.validate():
                    logger.info('validation error:%s' % f.errors)
                    raise HTTPBadRequest(body=json.dumps({
                        'message':u'入力データを確認してください',
                        'rows':{'rowid':row_data.get('id'), 'errors':f.errors}
                    }))

                if not f.is_leaf.data:
                    product.name = f.name.data
                    product.price = f.price.data
                    product.display_order = f.display_order.data
                    product.public = f.public.data
                    product.must_be_chosen = f.must_be_chosen.data
                    product.seat_stock_type_id = f.seat_stock_type_id.data
                    product.sales_segment = sales_segment
                    product.performance_id = f.performance_id.data
                    product.save()

                stock = Stock.query.filter_by(
                    stock_type_id=f.stock_type_id.data,
                    stock_holder_id=f.stock_holder_id.data,
                    performance_id=f.performance_id.data
                ).one()
                product_item.performance_id = f.performance_id.data
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
        product = self.context.product
        default = MultiDict(
            stock_type_id=product.seat_stock_type_id,
            product_item_name=product.name,
            product_item_price=int(product.price),
        )
        f = ProductItemForm(default, product=product)
        return {
            'form':f,
            'form_product':ProductAndProductItemForm(
                obj=product,
                sales_segment=product.sales_segment),
            }

    @view_config(route_name='product_items.new', request_method='POST', renderer='altair.app.ticketing:templates/product_items/_form.html', xhr=True)
    def new_post_xhr(self):
        product = self.context.product
        f = ProductItemForm(self.request.POST, product=product)
        if f.validate():
            price = Decimal()
            if f.product.items:
                price = sum(item.price * item.quantity for item in f.product.items)

            price += f.product_item_price.data * f.product_item_quantity.data
            f.product.price = price
            f.product.save()

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
                'form_product':ProductAndProductItemForm(
                    obj=product,
                    sales_segment=product.sales_segment),
            }

    @view_config(route_name='product_items.edit', request_method='GET', renderer='altair.app.ticketing:templates/product_items/_form.html', xhr=True)
    def edit_xhr(self):
        product_item = self.context.product_item
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
            'form_product':ProductAndProductItemForm(
                obj=product_item.product,
                sales_segment=product_item.product.sales_segment),
        }

    @view_config(route_name='product_items.edit', request_method='POST', renderer='altair.app.ticketing:templates/product_items/_form.html', xhr=True)
    def edit_post_xhr(self):
        product_item = self.context.product_item
        f = ProductItemForm(self.request.POST, product=product_item.product)
        if f.validate():
            # 商品価格の再計算前の初期化
            f.product.price = 0
            for item in f.product.items:
                if unicode(item.id) == f.product_item_id.data:
                    f.product.price += f.product_item_price.data * f.product_item_quantity.data
                else:
                    f.product.price += item.price * item.quantity
            f.product.save()

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
                'form_product':ProductAndProductItemForm(
                    obj=product_item.product,
                    sales_segment=product_item.product.sales_segment),
            }

    @view_config(route_name='product_items.delete')
    def delete(self):
        product_item = self.context.product_item
        location = self.request.route_path('performances.show_tab', performance_id=product_item.performance_id, tab='product')
        try:
            product_item.delete()
            self.request.session.flash(u'商品明細を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)
        return HTTPFound(location=location)

@view_config(route_name="products.sub.older.show", permission='event_editor', renderer="altair.app.ticketing:templates/products/_sub_older_show.html")
def subview_older(context, request):
    sales_segment = context.sales_segment
    ## todo: order
    ## todo: joined load
    products = (Product.query
                .filter_by(sales_segment_id=sales_segment.id)
                .order_by(Product.display_order)
                .all())

    return {
        "sales_segment": sales_segment, 
        "products": products, 
        "performance": sales_segment.performance, 
        "download_form": PreviewImageDownloadForm(sales_segment=sales_segment)
    }

@view_config(route_name="products.sub.newer.show", permission='event_editor', renderer="altair.app.ticketing:templates/products/_sub_newer_show.html")
def subview_newer(context, request):
    sales_segment = context.sales_segment
    event = sales_segment.event
    session = get_db_session(request, 'slave')
    try:
        performance_id = request.params["performance_id"]
        stock_holders = session.query(StockHolder).join(StockHolder.stock).filter(Stock.performance_id==performance_id).distinct().all()
    except KeyError:
        event = sales_segment.sales_segment_group.event
        performance_ids = [p.id for p in event.performances]
        stock_holders = session.query(StockHolder).join(Stock).filter(StockHolder.event_id == event.id).filter(Stock.performance_id.in_(performance_ids)).distinct().all()
    return dict(event=event, 
         stock_types = event.stock_types, 
         ticket_bundles = event.ticket_bundles, 
         sales_segment = sales_segment, 
         stock_holders = stock_holders
    )
