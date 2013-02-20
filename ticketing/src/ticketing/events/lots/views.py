# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.models import (
    DBSession,
    )
from ticketing.core.models import (
    Event, 
    Performance, 
    Product, 
    SalesSegment,
    PaymentDeliveryMethodPair,
    )
from ticketing.lots.models import (
    Lot,
    )
from .helpers import Link
from . forms import ProductForm, LotForm

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class Lots(BaseView):
    """ 抽選管理画面：一覧 """

    @view_config(route_name='lots.index', renderer='ticketing:templates/lots/index.html', permission='event_viewer')
    def index(self):
        if "action-delete" in self.request.params:
            for lot_id in self.request.params.getall('lot_id'):
                lot = Lot.query.filter(Lot.id==lot_id).first()
                if lot:
                    lot.delete()
                    self.request.session.flash(u"{0}を削除しました。".format(lot.name))

        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound()

        lots = Lot.query.filter(Lot.event_id==event_id).all()

        return dict(
            event=event,
            lots=lots,
            )

    @view_config(route_name='lots.new', renderer='ticketing:templates/lots/new.html', permission='event_viewer')
    def new(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
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
            return HTTPFound(self.request.route_url("lots.index", event_id=event_id))
        manage_sales_segment_group_link = Link(label=u"+", url=self.request.route_url('sales_segment_groups.index', event_id=event.id))
        return dict(
            event=event,
            form=form,
            manage_sales_segment_group_link=manage_sales_segment_group_link,
            )

    @view_config(route_name='lots.show', renderer='ticketing:templates/lots/show.html', permission='event_viewer')
    def show(self):
        lot_id = int(self.request.matchdict.get("lot_id", 0))
        lot = Lot.query.filter(Lot.id==lot_id).one()
        if "action-update-pdmp" in self.request.POST:
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
        lot_id = int(self.request.matchdict.get("lot_id", 0))
        lot = Lot.query.filter(Lot.id==lot_id).one()
        event = lot.event
        sales_segment_groups = event.sales_segment_groups
        sales_segment_group_choices = [
            (str(s.id), s.name)
            for s in sales_segment_groups
            ]
        form = LotForm(formdata=self.request.POST, obj=lot)
        form.sales_segment_group_id.choices = sales_segment_group_choices
        if self.request.POST and form.validate():
            form.update_lot(lot)
            return HTTPFound(self.request.route_url("lots.show", lot_id=lot_id))

        manage_sales_segment_group_link = Link(label=u"+", url=self.request.route_url('sales_segment_groups.index', event_id=event.id))

        return dict(
            lot=lot,
            event=event,
            form=form,
            manage_sales_segment_group_link=manage_sales_segment_group_link,
            )


    @view_config(route_name='lots.product_new', renderer='ticketing:templates/lots/product_new.html', permission='event_viewer')
    def product_new(self):
        lot_id = int(self.request.matchdict.get("lot_id", 0))
        lot = Lot.query.filter(Lot.id==lot_id).one()
        event = lot.event
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
            return HTTPFound(self.request.route_url('lots.show', lot_id=lot.id))
        return dict(form=form, lot=lot)
