# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
from sqlalchemy import sql
from pyramid.decorator import reify
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from ticketing.views import BaseView as _BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import (
    DBSession,
    Product, 
    PaymentDeliveryMethodPair,
    ShippingAddress,
    StockHolder,
    Stock,
    )
from ticketing.lots.models import (
    Lot,
    LotEntry,
    LotElectWork,
    )
import ticketing.lots.api as lots_api
from .helpers import Link
from .forms import ProductForm, LotForm, SearchEntryForm
from . import api

class BaseView(_BaseView):
    @reify
    def user(self):
        return self.request.context.user

    def check_organization(self, event):
        if event.organization != self.user.organization:
            raise HTTPNotFound()


@view_defaults(decorator=with_bootstrap, permission="event_editor")
class Lots(BaseView):
    """ 抽選管理画面：一覧 """

    @view_config(route_name='lots.index', renderer='ticketing:templates/lots/index.html', permission='event_viewer')
    def index(self):
        self.check_organization(self.context.event)
        if "action-delete" in self.request.params:
            for lot_id in self.request.params.getall('lot_id'):
                lot = Lot.query.filter(Lot.id==lot_id).first()
                if lot:
                    if lot.entries:
                        self.request.session.flash(u'{0}は抽選申し込みが存在します。'.format(lot.name))
                    else:
                        lot.sales_segment.delete()
                        lot.delete()
                        self.request.session.flash(u"{0}を削除しました。".format(lot.name))

        event = self.context.event
        if event is None:
            return HTTPNotFound()

        lots = Lot.query.filter(Lot.event_id==event.id).all()

        return dict(
            event=event,
            lots=lots,
            )

    @view_config(route_name='lots.new', renderer='ticketing:templates/lots/new.html', permission='event_viewer')
    def new(self):
        self.check_organization(self.context.event)
        event = self.context.event
        if event is None:
            return HTTPNotFound()

        sales_segment_groups = event.sales_segment_groups
        sales_segment_group_choices = [
            (str(s.id), s.name)
            for s in sales_segment_groups
            ]
        form = LotForm(formdata=self.request.POST)
        form.sales_segment_group_id.choices = sales_segment_group_choices

        if self.request.POST and form.validate():
            lot = form.create_lot(event)
            DBSession.add(lot)
            return HTTPFound(self.request.route_url("lots.index", event_id=event.id))

        manage_sales_segment_group_link = Link(label=u"+", url=self.request.route_url('sales_segment_groups.index', event_id=event.id))
        return dict(
            event=event,
            form=form,
            manage_sales_segment_group_link=manage_sales_segment_group_link,
            )

    @view_config(route_name='lots.show', renderer='ticketing:templates/lots/show.html', 
                 permission='event_viewer')
    def show(self):
        self.check_organization(self.context.event)
        lot = self.context.lot
        if "action-update-pdmp" in self.request.POST:
            lot.sales_segment.payment_delivery_method_pairs = []
            for pdmp_id in self.request.POST.getall("pdmp_id"):
                pdmp = PaymentDeliveryMethodPair.query.filter(PaymentDeliveryMethodPair.id==pdmp_id).first()
                if pdmp and pdmp not in lot.sales_segment.payment_delivery_method_pairs:
                    lot.sales_segment.payment_delivery_method_pairs.append(pdmp)
        if "action-delete" in self.request.POST:
            for product_id in self.request.POST.getall("product_id"):
                product = Product.query.filter(Product.id==product_id).first()
                if product:
                    product.delete()
                    self.request.session.flash(u"{0}を削除しました。".format(product.name))

        performance_ids = [p.id for p in lot.performances]
        stock_holders = StockHolder.query.join(Stock).filter(Stock.performance_id.in_(performance_ids)).distinct().all()

        stock_types = lot.event.stock_types
        ticket_bundles = lot.event.ticket_bundles
        options = ["%s:%s" % (st.id, st.name) for st in stock_types]
        stock_type_options = {"value": ';'.join(options)}
        options = ["%s:%s" % (st.id, st.name) for st in stock_holders]
        stock_holder_options = {"value": ';'.join(options)}
        options = [u":(なし)"] + ["%s:%s" % (tb.id, tb.name) for tb in ticket_bundles]
        ticket_bundle_options = {"value": ';'.join(options)}
        from altair.grid import altair_grid
        altair_grid.need()

        _query={'sales_segment_id': lot.sales_segment.id}
        product_grid = {
            "url": self.request.route_url('products.api.get',
                                          _query=_query),
            "editurl": self.request.route_url('products.api.set',
                                              _query=_query),
            "jsonReader": {"repeatitems": False},
            "datatype": "json",
            "cellEdit": True,
            "cellsubmit": 'clientArray',
            "colModel" : [ 
                {"hidden": True,
                 "jsonmap": "product.id",
                 "name": "product_id", 
                 "editable": False},
                {"label": u"商品名", 
                 "jsonmap": "product.name",
                 "name": "product_name", 
                 "editable": False, 
                 "width": 150}, 
                {"label": u"価格", 
                 "jsonmap": "product.price",
                 "name" : "product_price", 
                 "editable": False, 
                 "width": 60}, 
                {"label": u"表示順", 
                 "jsonmap": "product.order",
                 "name" :"product_order", 
                 "editable": False, 
                 "width": 40, 
                 "align" :'right'}, 
                {"label": u"一般公開", 
                 "jsonmap": "product.public",
                 "name" :'product_public', 
                 "index" :'tax', 
                 "width": 60, 
                 "edittype": "checkbox",
                 "formatter": "checkbox",
                 "align":'right'}, 
                {"label": u"席種", 
                 "jsonmap": "stock_type.id",
                 "name" :'stock_type_id', 
                 "index" :'stock_type_id', 
                 "width": 150, 
                 "align":'right',
                 "formatter": "select",
                 "edittype": "select",
                 "editoptions": stock_type_options,
                 "editable": True}, 
                {"label": u"配券先", 
                 "jsonmap": "stock_holder.id",
                 "name" :'stock_holder_id', 
                 "index" :'stock_holder_id', 
                 "width":100, 
                 "editable": True,
                 "formatter": 'select',
                 "edittype": 'select',
                 "editoptions": stock_holder_options,
                 "sortable":False},
                {"label": u"商品明細名", 
                 "jsonmap": "product_item.name",
                 "name" :'product_item_name', 
                 "index" :'product_item_name', 
                 "width":150, 
                 "editable": True,
                 "sortable":False},
                {"label": u"単価", 
                 "jsonmap": "product_item.price",
                 "name" :'product_item_price', 
                 "index" :'product_item_price', 
                 "width":60, 
                 "editable": True,
                 "sortable":False},
                {"label": u"販売単位", 
                 "jsonmap": "product_item.quantity",
                 "name" :'product_item_quantity', 
                 "index" :'product_item_quantity', 
                 "width": 60, 
                 "editable": True,
                 "sortable":False},
                {"label": u"券面", 
                 "jsonmap": "ticket_bundle.id",
                 "name" :'ticket_bundle_id', 
                 "index" :'ticket_bundle_id', 
                 "width": 80, 
                 "formatter": 'select',
                 "edittype": 'select',
                 "editoptions": ticket_bundle_options,
                 "editable": True,
                 "sortable":False},
                {"label": u"席数", 
                 "jsonmap": "stock.quantity",
                 "name" :'stock_quantity', 
                 "index" :'stock_quantity', 
                 "editable": True,
                 "width": 60, 
                 "sortable":False},
                {"label": u"残席数", 
                 "jsonmap": "stock_status.quantity",
                 "name" :'stock_status_quantity', 
                 "index" :'stock_status_quantity', 
                 "width": 60, 
                 "editable": False,
                 "sortable":False},
                {"label": u" ", 
                 "name" :'note', 
                 "index" :'note', 
                 "width": 80, 
                 "editable": True,
                 "sortable":False},
            ],
        }

        return dict(
            lot=lot,
            product_grid=product_grid,
            )

    @view_config(route_name='lots.edit', renderer='ticketing:templates/lots/edit.html', permission='event_viewer')
    def edit(self):
        self.check_organization(self.context.event)
        lot = self.context.lot
        event = self.context.event
        sales_segment_groups = event.sales_segment_groups
        sales_segment_group_choices = [
            (str(s.id), s.name)
            for s in sales_segment_groups
            ]
        form = LotForm(formdata=self.request.POST, obj=lot)
        form.sales_segment_group_id.choices = sales_segment_group_choices
        if self.request.POST and form.validate():
            form.update_lot(lot)
            return HTTPFound(self.request.route_url("lots.show", lot_id=lot.id))

        manage_sales_segment_group_link = Link(label=u"+", url=self.request.route_url('sales_segment_groups.index', event_id=event.id))

        return dict(
            lot=lot,
            event=event,
            form=form,
            manage_sales_segment_group_link=manage_sales_segment_group_link,
            )


    @view_config(route_name='lots.product_new', renderer='ticketing:templates/lots/product_new.html', permission='event_viewer')
    def product_new(self):
        self.check_organization(self.context.event)
        lot = self.context.lot
        event = self.context.event

        stock_types = event.stock_types
        stock_type_choices = [
            (s.id, s.name)
            for s in stock_types
        ]
        performances = event.performances
        performance_choices = [
            (p.id, u"{0.name} {0.start_on}".format(p))
            for p in performances
        ]
        form = ProductForm(formdata=self.request.POST)
        form.seat_stock_type_id.choices = stock_type_choices
        form.performance_id.choices = performance_choices

        if self.request.POST and form.validate():
            product = form.create_product(lot)
            DBSession.add(product)
            return HTTPFound(self.request.route_url('lots.show', lot_id=lot.id))
        return dict(form=form, lot=lot)

    @view_config(route_name='lots.product_edit', renderer='ticketing:templates/lots/product_new.html', permission='event_viewer')
    def product_edit(self):
        self.check_organization(self.context.event)
        product = self.context.product
        lot = self.context.lot
        event = self.context.event

        stock_types = event.stock_types
        stock_type_choices = [
            (s.id, s.name)
            for s in stock_types
        ]
        performances = event.performances
        performance_choices = [
            (p.id, u"{0.name} {0.open_on}".format(p))
            for p in performances
        ]
        form = ProductForm(obj=product, formdata=self.request.POST)
        form.seat_stock_type_id.choices = stock_type_choices
        form.performance_id.choices = performance_choices

        if self.request.POST and form.validate():
            product = form.apply_product(product)
            return HTTPFound(self.request.route_url('lots.show', lot_id=lot.id))
        return dict(form=form, lot=lot)


@view_defaults(decorator=with_bootstrap, permission="event_editor")
class LotEntries(BaseView):
    @view_config(route_name='lots.entries.index', renderer='ticketing:templates/lots/entries.html', permission='event_viewer')
    def index(self):
        """ 申し込み状況確認画面
        """
        self.check_organization(self.context.event)
        lot = self.context.lot
        lot_status = api.get_lot_entry_status(lot, self.request)

        return dict(
            lot=lot,
            performances = lot_status.performances,
            #  公演、希望順ごとの数
            sub_counts = lot_status.sub_counts,
            lot_status=lot_status,
            )


    @view_config(route_name='lots.entries.export', 
                 renderer='csv', permission='event_viewer')
    @view_config(route_name='lots.entries.export.html', 
                 renderer='ticketing:templates/lots/export.html', permission='event_viewer')
    def export_entries(self):
        """ 申し込み内容エクスポート

        - フィルター (すべて、未処理)
        """

        # とりあえずすべて

        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()
        entries = lots_api.get_lot_entries_iter(lot.id)
        filename='lot-{0.id}.csv'.format(lot)
        if self.request.matched_route.name == 'lots.entries.export':
            self.request.response.content_type = 'text/plain;charset=Shift_JIS'
            self.request.response.content_disposition = 'attachment; filename=' + filename
        return dict(data=list(entries),
                    encoding='sjis',
                    filename=filename)

    @view_config(route_name='lots.entries.search',
                 renderer='ticketing:templates/lots/search.html', permission='event_viewer')
    def search_entries(self):
        """ 申し込み内容エクスポート

        - フィルター (すべて、未処理)
        """

        # とりあえずすべて
        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()
        form = SearchEntryForm(formdata=self.request.POST)
        condition = (LotEntry.id != None)
        s_a = ShippingAddress

        if form.validate():
            if form.entry_no.data:
                condition = sql.and_(condition, LotEntry.entry_no==form.entry_no.data)
            if form.tel.data:
                condition = sql.and_(condition, 
                                     sql.or_(ShippingAddress.tel_1==form.tel.data,
                                             ShippingAddress.tel_2==form.tel.data))
            if form.name.data:
                condition = sql.and_(condition, 
                                     sql.or_(s_a.full_name==form.name.data,
                                             s_a.last_name==form.name.data,
                                             s_a.first_name==form.name.data,
                                             s_a.full_name_kana==form.name.data,
                                             s_a.last_name_kana==form.name.data,
                                             s_a.first_name_kana==form.name.data,))
            if form.email.data:
                condition = sql.and_(condition, 
                                     sql.or_(s_a.email_1==form.email.data,
                                             s_a.email_2==form.email.data))

            if form.entried_from.data:
                condition = sql.and_(condition, 
                                     LotEntry.created_at>=form.entried_from.data)
            if form.entried_to.data:
                condition = sql.and_(condition, 
                                     LotEntry.created_at<=form.entried_to.data)
        logger.debug("condition = {0}".format(condition))
        logger.debug("from = {0}".format(form.entried_from.data))
        entries = lots_api.get_lot_entries_iter(lot.id, condition)
        return dict(data=list(entries),
                    lot=lot,
                    form=form)


        
    @view_config(route_name='lots.entries.import', 
                 renderer="string",
                 permission='event_viewer')
    def import_accepted_entries(self):

        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()

        f = self.request.params['entries'].file
        header = 1
        entries = []
        for line in f:
            if header:
                header = 0
                continue
            if not line:
                continue
            if line.startswith('#'):
                continue

            parts = line.split(",")
            if len(parts) < 3:
                raise Exception, parts
            entry_no = parts[2]
            wish_order = parts[5]
            entries.append((entry_no, wish_order))
        if not entries:
            self.request.session.flash(u"当選データがありませんでした")
            return HTTPFound(location=self.request.route_url('lots.entries.index', lot_id=lot.id))

        self.request.session.flash(u"{0}件の当選データを取り込みました".format(len(entries)))
        lots_api.submit_lot_entries(lot.id, entries)
        
        return HTTPFound(location=self.request.route_url('lots.entries.index', lot_id=lot.id))

    @view_config(route_name='lots.entries.elect', 
                 renderer="string",
                 request_method="POST",
                 permission='event_viewer')
    def elect_entries(self):
        """ 当選確定処理
        """
        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()

        lots_api.elect_lot_entries(self.request, lot.id)

        self.request.session.flash(u"当選確定処理を行いました")
        LotElectWork.query.filter(LotElectWork.lot_id==lot.id).delete()
        return HTTPFound(location=self.request.route_url('lots.entries.index', lot_id=lot.id))

    @view_config(route_name='lots.entries.elect_entry_no', 
                 renderer="string",
                 request_method="POST",
                 permission='event_viewer')
    def elect_entry(self):
        """ 申し込み番号指定での当選処理
        """


        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()
        entries = []

        # TODO: form
        entry_no = self.request.params['entry_no']
        wish_order = self.request.params['wish_order']
        entries.append((entry_no, wish_order))
        lots_api.submit_lot_entries(lot.id, entries)

        self.request.session.flash(u"当選確定処理を行いました {0}".format(entry_no))
        return HTTPFound(location=self.request.route_url('lots.entries.index', lot_id=lot.id))
