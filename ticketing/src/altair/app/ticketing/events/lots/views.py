# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from sqlalchemy import sql
from sqlalchemy import orm
from pyramid.decorator import reify
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import get_renderer
from pyramid_mailer import get_mailer

from altair.sqlahelper import get_db_session

from altair.app.ticketing.views import BaseView as _BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import (
    DBSession,
    Product, 
    Performance,
    PaymentDeliveryMethodPair,
    ShippingAddress,
    StockHolder,
    Stock,
    )
from altair.app.ticketing.lots.models import (
    Lot,
    LotEntry,
    LotElectWork,
    LotRejectWork,
    LotEntryWish,
    )
from altair.app.ticketing.sej.models import (
    SejOrder,
)
from altair.multicheckout.models import (
    MultiCheckoutOrderStatus,
)
from altair.app.ticketing.payments.api import (
    is_finished_payment,
    is_finished_delivery,
)
import altair.app.ticketing.lots.api as lots_api
from altair.app.ticketing.lots.electing import Electing
from altair.app.ticketing.lots.closing import LotCloser
from .helpers import Link
from .forms import (
    ProductForm,
    LotForm,
    SearchEntryForm,
    SendingMailForm,
    LotEntryReportMailForm,
)

from . import api
from .models import LotWishSummary, LotEntryReportSetting
from .models import CSVExporter
from .reporting import LotEntryReporter

from altair.app.ticketing.payments import helpers as payment_helpers

logger = logging.getLogger(__name__)


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

    @view_config(route_name='lots.index', renderer='altair.app.ticketing:templates/lots/index.html', permission='event_viewer')
    def index(self):

        slave_session = get_db_session(self.request, name="slave")
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

        lots = slave_session.query(Lot).filter(Lot.event_id==event.id).all()

        return dict(
            event=event,
            lots=lots,
            )

    @view_config(route_name='lots.new', renderer='altair.app.ticketing:templates/lots/new.html', permission='event_viewer')
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

    @view_config(route_name='lots.show', renderer='altair.app.ticketing:templates/lots/show.html', 
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
                    try:
                        product.delete()
                        self.request.session.flash(u"{0}を削除しました。".format(product.name))
                    except Exception, e:
                        self.request.session.flash(e.message)
                        raise HTTPFound(location=self.request.route_url("lots.show", lot_id=lot.id))

        slave_session = get_db_session(self.request, name="slave")

        performance_ids = [p.id for p in lot.performances]
        stock_holders = slave_session.query(StockHolder).join(Stock).filter(Stock.performance_id.in_(performance_ids)).distinct().all()

        stock_types = lot.event.stock_types
        ticket_bundles = lot.event.ticket_bundles
        options = ["%s:%s%s" % (st.id, st.name, u'(数受け)' if st.quantity_only else u'') for st in stock_types]
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
            "rowNum": 200,
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
                {"hidden": True,
                 "jsonmap": "product_item.id",
                 "name" :'product_item_id',
                 "editable": False},
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

    @view_config(route_name='lots.edit', renderer='altair.app.ticketing:templates/lots/edit.html', permission='event_viewer')
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


    @view_config(route_name='lots.product_new', renderer='altair.app.ticketing:templates/lots/product_new.html', permission='event_viewer')
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

    @view_config(route_name='lots.product_edit', renderer='altair.app.ticketing:templates/lots/product_new.html', permission='event_viewer')
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
    @view_config(route_name='lots.entries.index', renderer='altair.app.ticketing:templates/lots/entries.html', permission='event_viewer')
    @view_config(route_name='lots.entries.index', renderer='altair.app.ticketing:templates/lots/entries_statuses.html', permission='event_viewer', xhr=True)
    def index(self):
        """ 申し込み状況確認画面
        """
        self.check_organization(self.context.event)
        lot = self.context.lot
        lot_status = api.get_lot_entry_status(lot, self.request)
        report_settings = LotEntryReportSetting.query.filter(
            LotEntryReportSetting.lot_id==lot.id
        ).all()

        return dict(
            lot=lot,
            performances = lot_status.performances,
            #  公演、希望順ごとの数
            sub_counts = lot_status.sub_counts,
            lot_status=lot_status,
            report_settings=report_settings,
            )


    @view_config(route_name='lots.entries.export', 
                 renderer='csv', permission='event_viewer')
    @view_config(route_name='lots.entries.export.html', 
                 renderer='altair.app.ticketing:templates/lots/export.html', permission='event_viewer')
    def export_entries(self):
        """ 申し込み内容エクスポート

        - フィルター (すべて、未処理)
        """

        slave_session = get_db_session(self.request, name="slave")

        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = slave_session.query(Lot).filter(Lot.id==lot_id).one()
        #entries = lots_api.get_lot_entries_iter(lot.id)
        entries = CSVExporter(slave_session, lot.id)
        filename='lot-{0.id}.csv'.format(lot)
        if self.request.matched_route.name == 'lots.entries.export':
            self.request.response.content_type = 'text/plain;charset=Shift_JIS'
            self.request.response.content_disposition = 'attachment; filename=' + filename
        return dict(data=list(entries),
                    encoding='sjis',
                    filename=filename)


    def payment_status(self, wish):
        #order = wish.lot_entry.order
        #order = wish.order
        finished = is_finished_payment(self.request, wish, wish)
        detail = payment_helpers.payment_status(wish, wish.auth, wish.sej)
        if finished:
            return u"処理済み( {detail} )".format(detail=detail)
        else:
            return u"( {detail} )".format(detail=detail)

    def delivery_status(self, wish):
        #order = wish.lot_entry.order
        finished = is_finished_delivery(self.request, wish, wish)
        detail = payment_helpers.delivery_status(wish, wish.auth, wish.sej)
        if finished:
            return u"処理済み( {detail} )".format(detail=detail)
        else:
            return u"( {detail} )".format(detail=detail)


    @view_config(route_name='lots.entries.search',
                 renderer='altair.app.ticketing:templates/lots/search.html', permission='event_viewer')
    def search_entries(self):
        """ 申し込み内容エクスポート

        - フィルター (すべて、未処理)
        """
        slave_session = get_db_session(self.request, name="slave")

        # とりあえずすべて
        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = slave_session.query(Lot).filter(Lot.id==lot_id).one()
        form = SearchEntryForm(formdata=self.request.POST)
        form.wish_order.choices = [("", "")] + [(str(i), i + 1) for i in range(lot.limit_wishes)]
        condition = (LotEntry.id != None)
        s_a = ShippingAddress

        include_canceled = False
        enable_elect_all = False
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
            include_canceled = form.include_canceled.data

            if (form.electing.data
                or form.elected.data
                or form.rejecting.data
                or form.rejected.data):
                wish_condition = (LotEntry.id == None) ## means False

                if form.electing.data:
                    wish_condition = sql.or_(wish_condition, 
                                             sql.and_(LotEntryWish.entry_wish_no==LotElectWork.entry_wish_no,
                                                      LotEntryWish.elected_at==None))
                if form.rejecting.data:
                    wish_condition = sql.or_(wish_condition, 
                                             sql.and_(LotEntry.entry_no==LotRejectWork.lot_entry_no,
                                                      LotEntryWish.rejected_at==None))
                if form.elected.data:
                    wish_condition = sql.or_(wish_condition, 
                                             LotEntryWish.elected_at!=None)
                if form.rejected.data:
                    wish_condition = sql.or_(wish_condition, 
                                             LotEntryWish.rejected_at!=None)

                condition = sql.and_(condition, wish_condition)

            if form.wish_order.data:
                condition = sql.and_(condition,
                                     LotEntryWish.wish_order==form.wish_order.data)
                enable_elect_all = True
        else:
            print form.errors

        if not include_canceled:
            condition = sql.and_(condition, 
                                 LotEntry.canceled_at == None)

        logger.debug("LotEntry.canceled_at == {0}".format(LotEntry.canceled_at))
        logger.debug("condition = {0}".format(condition))
        logger.debug("from = {0}".format(form.entried_from.data))

        q = DBSession.query(LotWishSummary).filter(
            LotWishSummary.lot_id==lot_id
        ).options(
            orm.joinedload('products'),
            orm.joinedload('products.product'),
        ).order_by(
            LotWishSummary.entry_no,
            LotWishSummary.wish_order
        )


        wishes = q.filter(condition)
        performances = Performance.query.filter(
            Performance.id==Product.performance_id
        ).filter(
            Product.sales_segment_id==Lot.sales_segment_id
        ).filter(
            Lot.id==lot.id
        ).all()

        performances = dict([(p.id, p) for p in performances])

        electing_url = self.request.route_url('lots.entries.elect_entry_no', lot_id=lot.id)
        electing_all_url = self.request.route_url('lots.entries.elect_all', lot_id=lot.id)
        rejecting_remains_url = self.request.route_url('lots.entries.reject_remains', lot_id=lot.id)
        rejecting_url = self.request.route_url('lots.entries.reject_entry_no', lot_id=lot.id)
        cancel_url = self.request.route_url('lots.entries.cancel', lot_id=lot.id)
        cancel_electing_url = self.request.route_url('lots.entries.cancel_electing', lot_id=lot.id)
        cancel_rejecting_url = self.request.route_url('lots.entries.cancel_rejecting',
                                                      lot_id=lot.id)
        status_url = self.request.route_url('lots.entries.elect', lot_id=lot.id)
        electing = Electing(lot, self.request)

        lot_status = api.get_lot_entry_status(lot, self.request)
        return dict(wishes=wishes.all(),
                    lot=lot,
                    form=form,
                    cancel_url=cancel_url,
                    rejecting_url=rejecting_url,
                    electing_url=electing_url,
                    electing_all_url=electing_all_url,
                    cancel_electing_url=cancel_electing_url,
                    cancel_rejecting_url=cancel_rejecting_url,
                    lot_status=lot_status,
                    status_url=status_url,
                    electing=electing,
                    performances=performances,
                    enable_elect_all=enable_elect_all,
                    rejecting_remains_url=rejecting_remains_url,
        )

        
    @view_config(route_name='lots.entries.import', 
                 renderer="string",
                 permission='event_viewer')
    def import_accepted_entries(self):

        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()

        f = self.request.params['entries'].file
        entries = self._parse_import_file(f)
        if not entries:
            self.request.session.flash(u"当選データがありませんでした")
            return HTTPFound(location=self.request.route_url('lots.entries.index', lot_id=lot.id))

        self.request.session.flash(u"{0}件の当選データを取り込みました".format(len(entries)))
        electing_count = lots_api.submit_lot_entries(lot.id, entries)
        rejecting_count = lots_api.submit_reject_entries(lot_id, lot.rejectable_entries)
        self.request.session.flash(u"新たに{0}件が当選予定となりました".format(electing_count))
        self.request.session.flash(u"新たに{0}件が落選予定となりました".format(rejecting_count))

        return HTTPFound(location=self.request.route_url('lots.entries.index', lot_id=lot.id))

    def _parse_import_file(self, f):
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
            entry_no = parts[1]
            try:
                wish_order = int(parts[2]) - 1
            except ValueError:
                continue

            entries.append((entry_no, wish_order))
        return entries

    @view_config(route_name='lots.entries.elect',
                 renderer="lots/electing.html",
                 request_method="GET",
                 permission='event_viewer')
    @view_config(route_name='lots.entries.elect',
                 renderer="lots/electing_statuses.html",
                 request_method="GET",
                 permission='event_viewer',
                 xhr=True)
    def elect_entries_form(self):
        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()
        electing = Electing(lot, self.request)
        closer = LotCloser(lot, self.request)
        return dict(lot=lot,
                    closer=closer,
                    electing=electing)



    @view_config(route_name='lots.entries.close',
                 renderer="string",
                 request_method="POST",
                 permission='event_viewer')
    def close_entries(self):
        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()
        closer = LotCloser(lot, self.request)
        closer.close()
        self.request.session.flash(u"オーソリ開放可能にしました。")
        lot.finish_lotting()

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
        lot.start_electing()

        return HTTPFound(location=self.request.route_url('lots.entries.index', lot_id=lot.id))

    @view_config(route_name='lots.entries.reject',
                 renderer="string",
                 request_method="POST",
                 permission='event_viewer')
    def reject_entries(self):
        """ 落選確定処理
        """
        self.check_organization(self.context.event)

        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()

        lots_api.reject_lot_entries(self.request, lot.id)

        self.request.session.flash(u"落選確定処理を行いました")

        lot.start_electing()
        return HTTPFound(location=self.request.route_url('lots.entries.index', 
                                                         lot_id=lot.id))



    def render_wish_row(self, wish):
        """ ajaxで当選申込変更後の内容を返す"""
        w = DBSession.query(LotWishSummary).filter(
            LotWishSummary.entry_no==wish.lot_entry.entry_no
        ).filter(
            LotWishSummary.wish_order==wish.wish_order
        ).one()
        tmpl = get_renderer("/lots/search.html")
        auth = MultiCheckoutOrderStatus.by_order_no(wish.lot_entry.entry_no)
        sej =  DBSession.query(SejOrder).filter(SejOrder.order_id==wish.lot_entry.entry_no).first()

        html = tmpl.implementation().get_def('lot_wish_row').render(
            self.request, w=w, auth=auth, sej=sej, view=self)
        return html

    def wish_tr_class(self, wish):
        return 'lot-wish-' + wish.lot_entry.entry_no + '-' + str(wish.wish_order)


    @view_config(route_name="lots.entries.reject_remains",
                 request_method="POST",
                 permission='event_viewer',
                 renderer="json")
    def reject_remains(self):
        """ 一括落選予定処理"""
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()
        entries = lot.rejectable_entries
        rejecting_count = lots_api.submit_reject_entries(lot_id, entries)

        def _wish_generator():
            for e in entries:
                for w in e.wishes:
                    yield w

        return dict(rejecting_count=rejecting_count,
                    html=[(self.wish_tr_class(w), self.render_wish_row(w))
                          for w in _wish_generator()])


    @view_config(route_name="lots.entries.elect_all", 
                 request_method="POST",
                 permission='event_viewer',
                 renderer="json")
    def elect_all(self):
        """ 一括当選予定処理 """
        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()

        params = self.request.json_body
        logger.debug("electing all {0}".format(params))
        wish_ids = params.get('wishes', [])
        if not wish_ids:
            return dict()

        wishes = LotEntryWish.query.join(
            LotEntryWish.lot_entry,
        ).join(
            LotEntry.lot,
        ).outerjoin(
            LotElectWork.__table__,
            LotElectWork.lot_entry_no==LotEntry.entry_no,
        ).filter(
            LotEntryWish.id.in_(wish_ids)
        ).filter(
            LotEntry.elected_at==None
        ).filter(
            LotEntry.rejected_at==None
        ).filter(
            LotEntry.canceled_at==None
        ).filter(
            LotEntry.closed_at==None
        ).filter(
            LotElectWork.lot_entry_no==None
        ).all()

        results = {}
        entries = []
        for w in wishes:
            lot_entry = w.lot_entry
            entry_no = lot_entry.entry_no
            wish_order = w.wish_order
            logger.debug("electing {0}".format(lot_entry))
            if lot_entry.is_electing():
                logger.debug('{0} is already electing'.format(entry_no))
                results[lot_entry.entry_no] = dict(result="NG")
            if lot_entry.is_rejecting():
                logger.debug('{0} is already rejecting'.format(entry_no))
                results[lot_entry.entry_no] = dict(result="NG")

            entries.append((entry_no, wish_order))
            
        affected = lots_api.submit_lot_entries(lot.id, entries)

        logger.debug('elect all: results = {0}'.format(results))
        lot.start_lotting()
        return dict(
            affected=affected,
            html=[(self.wish_tr_class(w), self.render_wish_row(w))
                  for w in wishes])

    @view_config(route_name='lots.entries.elect_entry_no', 
                 request_method="POST",
                 permission='event_viewer',
                 renderer="json")
    def elect_entry(self):
        """ 申し込み番号指定での当選予定処理
        """
        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()

        entry_no = self.request.params['entry_no']
        wish_order = self.request.params['wish_order']

        lot_entry = lot.get_lot_entry(entry_no)

        if lot_entry.is_electing():
            return dict(result="NG",
                        message=u"すでに、当選予定の希望が存在します。一度、他希望の当選予定をキャンセルの上、再度、ステータス変更をしてください")

        wish = lot_entry.get_wish(wish_order)
        if wish is None:
            return dict(result="NG",
                        message="not found")

        entries = [(entry_no, wish_order)]

        affected = lots_api.submit_lot_entries(lot.id, entries)

        lot.start_lotting()

        return dict(result="OK",
                    affected=affected,
                    html=[(self.wish_tr_class(w), self.render_wish_row(w))
                          for w in wish.lot_entry.wishes])


    @view_config(route_name='lots.entries.reject_entry_no', 
                 request_method="POST",
                 permission='event_viewer',
                 renderer="json")
    def reject_entry(self):
        """ 申し込み番号指定での落選予定処理
        """
        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()

        entry_no = self.request.params['entry_no']
        lot_entry = lot.get_lot_entry(entry_no)
        if lot_entry.is_electing():
            return dict(result="NG",
                        message=u"すでに、当選予定の希望が存在します。一度、他希望の当選予定をキャンセルの上、再度、ステータス変更をしてください")
        if lot_entry.is_rejecting():
            return dict(result="NG",
                        message=u"すでに、落選予定となっています。一度、他希望の当選予定をキャンセルの上、再度、ステータス変更をしてください")

        entries = [lot_entry]

        affected = lots_api.submit_reject_entries(lot.id, entries)

        lot.start_lotting()
        return dict(result="OK",
                    affected=affected,
                    html=[(self.wish_tr_class(w), self.render_wish_row(w))
                          for w in lot_entry.wishes])


    @view_config(route_name='lots.entries.cancel', 
                 renderer="json",
                 request_method="POST",
                 permission='event_viewer')
    def cancel_entry(self):
        """ 申し込み番号指定でのキャンセル処理
        """


        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()
        # TODO: form

        entry_no = self.request.params['entry_no']
        lot_entry = lot.get_lot_entry(entry_no)
        if lot_entry is None:
            return dict(result="NG",
                        message="not found")


        # チェック
        if lot_entry.is_electing():
            return dict(result="NG",
                        message=u"「当選予定」ステータスの希望が存在します。一度、他希望の当選予定をキャンセルの上、再度、ステータス変更をしてください")



        lot_entry.cancel()

        return dict(result="OK",
                    html=[(self.wish_tr_class(w), self.render_wish_row(w))
                          for w in lot_entry.wishes])



    @view_config(route_name='lots.entries.cancel_electing',
                 request_method="POST",
                 permission='event_viewer',
                 renderer="json")
    def cancel_electing_entry(self):
        """ 申し込み番号指定での当選予定キャンセル処理
        """
        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()

        entry_no = self.request.params['entry_no']
        wish_order = self.request.params['wish_order']

        lot_entry = lot.get_lot_entry(entry_no)
        wish = lot_entry.get_wish(wish_order)

        logger.debug(wish.works)

        if wish is None:
            return dict(result="NG",
                        message="not found")

        lot.cancel_electing(wish)

        return dict(result="OK",
                    html=[(self.wish_tr_class(w), self.render_wish_row(w))
                          for w in lot_entry.wishes])


    @view_config(route_name='lots.entries.cancel_rejecting',
                 request_method="POST",
                 permission='event_viewer',
                 renderer="json")
    def cancel_rejecting_entry(self):
        """ 申し込み番号指定での当選予定処理
        """
        self.check_organization(self.context.event)
        lot_id = self.request.matchdict["lot_id"]
        lot = Lot.query.filter(Lot.id==lot_id).one()

        entry_no = self.request.params['entry_no']

        lot_entry = lot.get_lot_entry(entry_no)


        lot.cancel_rejecting(lot_entry)

        return dict(result="OK",
                    html=[(self.wish_tr_class(w), self.render_wish_row(w))
                          for w in lot_entry.wishes])


    @view_config(route_name='lots.entries.show', renderer="lots/entry_show.html")
    def entry_show(self):
        self.check_organization(self.context.event)
        slave_session = get_db_session(self.request, name="slave")
        lot_id = self.request.matchdict["lot_id"]
        lot = slave_session.query(Lot).filter(Lot.id==lot_id).one()

        entry_no = self.request.matchdict['entry_no']
        lot_entry = lot.get_lot_entry(entry_no)
        shipping_address = lot_entry.shipping_address
        mail_form = SendingMailForm(recipient=shipping_address.email_1, 
                                    bcc="")
        summaries = slave_session.query(LotWishSummary).filter(LotWishSummary.entry_no==entry_no).order_by(LotWishSummary.wish_order).all()
        wishes = sorted(lot_entry.wishes, key=lambda w: w.wish_order)
        wishes = zip(summaries, wishes)
        for w, ww in wishes:
            assert w.wish_order == ww.wish_order

        return {"lot": lot, 
                "wishes": wishes,
                "lot_entry": lot_entry, 
                "shipping_address": shipping_address, 
                "mail_form": mail_form}



@view_defaults(decorator=with_bootstrap, permission="event_editor")
class LotReport(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def index_url(self):
        return self.request.route_url("lots.entries.index",
                                      **self.request.matchdict)

    @view_config(route_name="lot.entries.new_report_setting",
                 renderer="lots/new_report_setting.html")
    def new_setting(self):
        form = LotEntryReportMailForm(formdata=self.request.POST)
        form.lot_id.data = self.context.lot.id

        if self.request.method == "POST":
            if form.validate():
                new_setting = LotEntryReportSetting()
                form.sync(new_setting)
                DBSession.add(new_setting)
                return HTTPFound(self.index_url)
        return dict(form=form,
                    event=self.context.event)


    @view_config(route_name="lot.entries.delete_report_setting",
                 request_method="POST")
    def delete_setting(self):
        setting = LotEntryReportSetting.query.filter(
            LotEntryReportSetting.id==self.request.matchdict['setting_id']
        ).first()
        if setting is None:
            return HTTPNotFound()
        setting.deleted_at = datetime.now()
        return HTTPFound(self.index_url)

    @view_config(route_name="lot.entries.send_report_setting",
                 request_method="POST")
    def send_report(self):
        """ 手動送信 """
        setting = LotEntryReportSetting.query.filter(
            LotEntryReportSetting.id==self.request.matchdict['setting_id']
        ).first()
        if setting is None:
            return HTTPNotFound()


        mailer = get_mailer(self.request)
        sender = self.request.registry.settings['mail.message.sender']
        reporter = LotEntryReporter(sender, mailer, setting)
        reporter.send()
        return HTTPFound(self.index_url)
