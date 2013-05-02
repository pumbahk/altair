# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from sqlalchemy import sql
from webhelpers.containers import correlate_objects
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import (
    DBSession,
    Event, 
    Product, 
    PaymentDeliveryMethodPair,
    )
from ticketing.lots.models import (
    Lot,
    LotEntry,
    LotEntryWish,
    LotElectWork,
    LotElectedEntry,
    )
import ticketing.lots.api as lots_api
from .helpers import Link
from .forms import ProductForm, LotForm
from . import api

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class Lots(BaseView):
    """ 抽選管理画面：一覧 """

    @view_config(route_name='lots.index', renderer='ticketing:templates/lots/index.html', permission='event_viewer')
    def index(self):
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
        return dict(
            lot=lot,
            )

    @view_config(route_name='lots.edit', renderer='ticketing:templates/lots/edit.html', permission='event_viewer')
    def edit(self):
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
        form = ProductForm(formdata=self.request.POST)
        form.seat_stock_type_id.choices = stock_type_choices
        form.performance_id.choices = performance_choices

        if self.request.POST and form.validate():
            product = form.create_product(lot)
            DBSession.add(product)
            return HTTPFound(self.request.route_url('lots.show', lot_id=lot.id))
        return dict(form=form, lot=lot)


@view_defaults(decorator=with_bootstrap, permission="event_editor")
class LotEntries(BaseView):
    @view_config(route_name='lots.entries.index', renderer='ticketing:templates/lots/entries.html', permission='event_viewer')
    def index(self):
        """ 申し込み状況確認画面
        """
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


        
    @view_config(route_name='lots.entries.import', 
                 renderer="string",
                 permission='event_viewer')
    def import_accepted_entries(self):

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
