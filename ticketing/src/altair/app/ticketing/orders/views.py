# -*- coding: utf-8 -*-

import sys
import json
import logging
import csv
import itertools
from datetime import datetime
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.url import route_path
from paste.util.multidict import MultiDict
import webhelpers.paginate as paginate
from wtforms import ValidationError
from wtforms.validators import Optional
from sqlalchemy import and_
from sqlalchemy.sql import exists
from sqlalchemy.sql.expression import or_, desc
from sqlalchemy.orm import joinedload, undefer
from webob.multidict import MultiDict
from altair.sqlahelper import get_db_session
from altair.app.ticketing.tickets.api import get_svg_builder
from altair.app.ticketing.models import DBSession, merge_session_with_post, record_to_multidict, asc_or_desc
from altair.app.ticketing.core.models import (
    Order,
    Performance,
    PaymentDeliveryMethodPair,
    ShippingAddress,
    Product,
    ProductItem,
    OrderedProduct,
    OrderedProductItem,
    OrderedProductAttribute,
    Ticket,
    TicketBundle,
    TicketFormat,
    Ticket_TicketBundle,
    DeliveryMethod,
    TicketFormat_DeliveryMethod,
    Venue,
    SalesSegmentGroup,
    SalesSegment,
    Stock,
    StockStatus,
    Seat,
    SeatStatus,
    SeatStatusEnum,
    ChannelEnum, 
    MailTypeEnum, 
    OrderedProductItemToken
    )
from altair.app.ticketing.mails.api import get_mail_utility
from altair.app.ticketing.mailmags.models import MailSubscription, MailMagazine, MailSubscriptionStatus
from altair.app.ticketing.orders.export import OrderCSV, get_japanese_columns
from altair.app.ticketing.orders.forms import (OrderForm, OrderSearchForm, OrderRefundSearchForm, SejOrderForm, SejTicketForm,
                                    SejRefundEventForm,SejRefundOrderForm, SendingMailForm,
                                    PerformanceSearchForm, OrderReserveForm, OrderRefundForm, ClientOptionalForm,
                                    SalesSegmentGroupSearchForm, PreviewTicketSelectForm, CartSearchForm, 
                                               )
from altair.app.ticketing.orders.forms import OrderMemoEditFormFactory
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.orders.events import notify_order_canceled
from altair.app.ticketing.orders.exceptions import InnerCartSessionException
from altair.app.ticketing.payments.payment import Payment, get_delivery_plugin
from altair.app.ticketing.payments import plugins as payments_plugins
from altair.app.ticketing.tickets.utils import build_dicts_from_ordered_product_item
from altair.app.ticketing.cart import api
from altair.app.ticketing.cart.models import Cart
from altair.app.ticketing.cart.stocker import NotEnoughStockException
from altair.app.ticketing.cart.reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from altair.app.ticketing.cart.exceptions import NoCartError
from altair.app.ticketing.loyalty import api as loyalty_api

from . import utils
from .api import (
    CartSearchQueryBuilder,
    OrderSummarySearchQueryBuilder,
    QueryBuilderError,
    create_inner_order,
    get_ordered_product_metadata_provider_registry, 
    get_order_metadata_provider_registry
)
from .utils import NumberIssuer
from .models import OrderSummary
from altair.app.ticketing.tickets.preview.api import SVGPreviewCommunication
from altair.app.ticketing.tickets.preview.api import get_placeholders_from_ticket
from altair.app.ticketing.tickets.preview.transform import SVGTransformer
from altair.app.ticketing.tickets.utils import build_cover_dict_from_order
from altair.app.ticketing.core.models import TicketCover
from altair.app.ticketing.core.modelmanage import OrderAttributeManager

logger = logging.getLogger(__name__)

def available_ticket_formats_for_orders(orders):
    return TicketFormat.query\
        .filter(TicketFormat.id==Ticket.ticket_format_id)\
        .filter(Ticket.id==Ticket_TicketBundle.ticket_id)\
        .filter(Ticket_TicketBundle.ticket_bundle_id==TicketBundle.id)\
        .filter(TicketBundle.id==ProductItem.ticket_bundle_id)\
        .filter(ProductItem.id==OrderedProductItem.product_item_id)\
        .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
        .filter(OrderedProduct.order_id.in_(orders))\
        .with_entities(TicketFormat.id, TicketFormat.name)\
        .distinct(TicketFormat.id)

def available_ticket_formats_for_ordered_product_item(ordered_product_item):
    delivery_method_id = ordered_product_item.ordered_product.order.payment_delivery_pair.delivery_method_id
    bundle_id = ordered_product_item.product_item.ticket_bundle_id
    return TicketFormat.query\
        .filter(bundle_id==Ticket_TicketBundle.ticket_bundle_id, 
                Ticket_TicketBundle.ticket_id==Ticket.id, 
                Ticket.ticket_format_id==TicketFormat.id, 
                TicketFormat_DeliveryMethod.delivery_method_id==delivery_method_id, 
                TicketFormat.id==TicketFormat_DeliveryMethod.ticket_format_id)\
                .with_entities(TicketFormat.id, TicketFormat.name).distinct(TicketFormat.id)

def encode_to_cp932(data):
    if not hasattr(data, "encode"):
        return str(data)
    try:
        return data.encode('cp932')
    except UnicodeEncodeError:
        logger.warn('cannot encode character %s to cp932' % data)
        if data is not None and len(data) > 1:
            return ''.join([encode_to_cp932(d) for d in data])
        else:
            return '?'


@view_defaults(xhr=True, permission='sales_counter') ## todo:適切な位置に移動
class OrdersAPIView(BaseView):

    @view_config(renderer="json", route_name="orders.api.performances")
    def get_performances(self):
        form_search = PerformanceSearchForm(self.request.params)
        if not form_search.validate():
            return {"result": [],  "status": False}

        formdata = form_search.data
        query = Performance.query
        if formdata['sort']:
            try:
                query = asc_or_desc(query, getattr(Performance, formdata['sort']), formdata['direction'], 'asc')
            except AttributeError:
                pass

        if formdata['event_id']:
            query = query.filter(Performance.event_id == formdata['event_id'])

        performances = [dict(pk='', name=u'(すべて)')]+[dict(pk=p.id, name='%s (%s)' % (p.name, p.start_on.strftime('%Y-%m-%d %H:%M'))) for p in query]
        return {"result": performances, "status": True}

    @view_config(renderer="json", route_name="orders.api.sales_segment_groups")
    def get_sales_segment_groups(self):
        form_search = SalesSegmentGroupSearchForm(self.request.params)
        if not form_search.validate():
            return {"result": [],  "status": False}

        formdata = form_search.data
        query = SalesSegmentGroup.query
        if formdata['sort']:
            try:
                query = asc_or_desc(query, getattr(SalesSegmentGroup, formdata['sort']), formdata['direction'], 'asc')
            except AttributeError:
                pass

        if formdata['event_id']:
            query = query.filter(SalesSegmentGroup.event_id == formdata['event_id'])
        if formdata['public']:
            query = query.filter(SalesSegmentGroup.public == bool(formdata['public']))

        sales_segment_groups = [dict(pk='', name=u'(すべて)')] + [dict(pk=p.id, name=p.name) for p in query]
        return {"result": sales_segment_groups, "status": True}

    @view_config(renderer="json", route_name="orders.api.checkbox_status", request_method="POST", match_param="action=add")
    def add_checkbox_status(self):
        """ [o:1, o:2, o:3, o:4, ....]
        """
        oid = self.request.POST["target"]
        if not oid.startswith("o:"):
            return {"status": False}

        orders = self.request.session.get("orders") or set()
        orders.add(oid)
        self.request.session["orders"] = orders
        return {"status": True, "count": len(orders), "result": list(orders)}

    @view_config(renderer="json", route_name="orders.api.checkbox_status", request_method="POST", match_param="action=addall")
    def add_all_checkbox_status(self):
        """ [o:1, o:2, o:3, o:4, ....]
        """
        oids = self.request.POST.getall("targets[]")
        orders = self.request.session.get("orders") or set()
        for oid in oids:
            if oid.startswith("o:"):
                orders.add(oid)
        self.request.session["orders"] = orders
        return {"status": True, "count": len(orders), "result": list(orders)}

    @view_config(renderer="json", route_name="orders.api.checkbox_status", request_method="POST", match_param="action=remove")
    def remove_checkbox_status(self):
        """ [o:1, o:2, o:3, o:4, ....]
        """
        oid = self.request.POST["target"]
        if not oid.startswith("o:"):
            return {"status": False}

        orders = self.request.session.get("orders") or set()
        orders.remove(oid)
        self.request.session["orders"] = orders
        return {"status": True, "count": len(orders), "result": list(orders)}

    @view_config(renderer="json", route_name="orders.api.checkbox_status", request_method="POST", match_param="action=removeall")
    def remove_all_checkbox_status(self):
        """ [o:1, o:2, o:3, o:4, ....]
        """
        oids = self.request.POST.getall("targets[]")
        orders = self.request.session.get("orders") or set()
        for oid in oids:
            if oid.startswith("o:"):
                orders.remove(oid)
        self.request.session["orders"] = orders
        return {"status": True, "count": len(orders), "result": list(orders)}

    @view_config(renderer="json", route_name="orders.api.checkbox_status", request_method="GET", match_param="action=load")
    def load_checkbox_status(self):
        if not "orders" in self.request.session:
            return {"status": False, "result": [], "count": 0}
        orders = self.request.session["orders"]
        return {"status": True, "result": list(orders), "count": len(orders)}

    @view_config(renderer="json", route_name="orders.api.checkbox_status", request_method="POST", match_param="action=reset")
    def reset_checkbox_status(self):
        self.request.session["orders"] = set()
        return {"status": True, "count": 0, "result": []}

    @view_config(renderer="json", route_name="orders.api.orders", request_method="GET", match_param="action=matched_by_ticket", request_param="ticket_format_id")
    def checked_matched_orders(self):
        if not "orders" in self.request.session:
            return {"status": False, "result": []}
        ticket_format_id = self.request.GET["ticket_format_id"]
        exclude_issued = self.request.GET.get("exclude_issued", False)
        ords = self.request.session["orders"]
        ords = [o.lstrip("o:") for o in ords if o.startswith("o:")]
        qs = Order.query\
            .filter(Order.deleted_at==None).filter(Order.id.in_(ords))\
            .filter(OrderedProduct.order_id.in_(ords))\
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(ProductItem.id==OrderedProductItem.product_item_id)\
            .filter(TicketBundle.id==ProductItem.ticket_bundle_id)\
            .filter(Ticket_TicketBundle.ticket_bundle_id==TicketBundle.id)\
            .filter(Ticket.id==Ticket_TicketBundle.ticket_id)\
            .filter(Ticket.ticket_format_id==ticket_format_id).distinct()
        if exclude_issued:
            qs = qs.filter(Order.issued==False)

        orders_list = [dict(order_no=o.order_no, event_name=o.performance.event.title, total_amount=int(o.total_amount))
                       for o in qs]
        return {"results": orders_list, "status": True}

def session_has_order_p(context, request):
    return bool(request.session.get("orders"))


#########################################################################
@view_config(decorator=with_bootstrap,
             route_name='orders.index',
             renderer='altair.app.ticketing:templates/orders/index.html',
             #renderer="string",
             permission='sales_counter')
def index(request):
    slave_session = get_db_session(request, name="slave")

    organization_id = request.context.organization.id
    params = MultiDict(request.params)
    params["order_no"] = " ".join(request.params.getall("order_no"))

    form_search = OrderSearchForm(params, organization_id=organization_id)
    from .download import OrderSummary
    if form_search.validate():
        query = OrderSummary(slave_session,
                            organization_id,
                            condition=form_search)
    else:
        query = OrderSummary(slave_session,
                            organization_id,
                            condition=None)

    if request.params.get('action') == 'checked':
        
        checked_orders = [o.lstrip('o:') 
                          for o in request.session.get('orders', []) 
                          if o.startswith('o:')]
        query.target_order_ids = checked_orders
        
    page = int(request.params.get('page', 0))
    orders = paginate.Page(
        query,
        page=page,
        items_per_page=40,
        url=paginate.PageURL_WebOb(request)
    )

    return {
        'form':OrderForm(),
        'form_search':form_search,
        'orders':orders,
        'page': page,
    }

#@view_config(route_name='orders.download')
def download(request):
    slave_session = get_db_session(request, name="slave")

    organization_id = request.context.organization.id
    params = MultiDict(request.params)
    params["order_no"] = " ".join(request.params.getall("order_no"))

    form_search = OrderSearchForm(params, organization_id=organization_id)
    from .download import OrderDownload, OrderSummaryKeyBreakAdapter, japanese_columns, header_intl, SeatSummaryKeyBreakAdapter, OrderSeatDownload
    export_type = int(request.params.get('export_type', OrderCSV.EXPORT_TYPE_ORDER))
    excel_csv = bool(request.params.get('excel_csv'))

    query_type = OrderDownload
    if export_type == OrderCSV.EXPORT_TYPE_ORDER:
        query_type = OrderDownload
    elif export_type == OrderCSV.EXPORT_TYPE_SEAT:
        query_type = OrderSeatDownload

    if request.method == "POST" and form_search.validate():
        query = query_type(slave_session,
                              organization_id,
                              condition=form_search)
    else:
        query = OrderDownload(slave_session,
                              organization_id,
                              condition=None)

    if export_type == OrderCSV.EXPORT_TYPE_ORDER:
        query = OrderSummaryKeyBreakAdapter(query, 'id',
                                            ('product_price', 'product_quantity',
                                             'product_name',
                                             'product_sales_segment', 'product_margin_ratio'),
                                            'product_id',
                                            ('item_name', 'item_price', 'item_quantity'),
                                            'product_item_id',
                                            ('item_print_histories',),
                                            ('seat_name',),
                                            'seat_id',)
        csv_headers = ([
            "order_no",
            "status",
            "payment_status",
            "created_at",
            "paid_at",
            "delivered_at",
            "canceled_at",
            "total_amount",
            "transaction_fee",
            "delivery_fee",
            "system_fee",
            "special_fee",
            "margin",
            "note",
            "special_fee_name",
            "card_brand",
            "card_ahead_com_code",
            "card_ahead_com_name",
            "billing_number",
            "exchange_number",
            "mail_permission", #"メールマガジン受信可否",
            "user_last_name",
            "user_first_name",
            "user_last_name_kana",
            "user_first_name_kana",
            "user_nick_name",
            "user_sex",
            "membership_name",
            "membergroup_name",
            "auth_identifier",
            "last_name",
            "first_name",
            "last_name_kana",
            "first_name_kana",
            "zip",
            "country",
            "prefecture",
            "city",
            "address_1",
            "address_2",
            "tel_1",
            "tel_2",
            "fax",
            "email_1",
            "email_2",
            "payment_method_name",
            "delivery_method_name",
            "event_title",
            "performance_name",
            "performance_code",
            "performance_start_on",
            "venue_name",
        ] + query.extra_headers)
    else:
        query = SeatSummaryKeyBreakAdapter(query, "seat_id", "order_no", ["item_print_histories"])
        csv_headers = [
            "order_no",  # 予約番号
            "status",  # ステータス
            "payment_status",  # 決済ステータス
            "created_at",  # 予約日時
            "paid_at",  # 支払日時
            "delivered_at",  # 配送日時
            "canceled_at",  # キャンセル日時
            "total_amount",  # 合計金額
            "transaction_fee",  # 決済手数料
            "delivery_fee",  # 配送手数料
            "system_fee",  # システム利用料
            "special_fee",  # 特別手数料
            "margin",  # 内手数料金額
            "note",  # メモ
            "special_fee_name", # 特別手数料名
            "card_brand",  # カードブランド
            "card_ahead_com_code",  #  仕向け先企業コード
            "card_ahead_com_name",  # 仕向け先企業名
            "billing_number",  # SEJ払込票番号
            "exchange_number",  # SEJ引換票番号
            "mail_permission", #"メールマガジン受信可否",
            "user_last_name",  # 姓
            "user_first_name",  # 名
            "user_last_name_kana",  # 姓(カナ)
            "user_first_name_kana",  # 名(カナ)
            "user_nick_name",  # ニックネーム
            "user_sex",  # 性別
            "membership_name",  # 会員種別名
            "membergroup_name",  # 会員グループ名
            "auth_identifier",  # 会員種別ID
            "last_name",  # 配送先姓
            "first_name",  # 配送先名
            "last_name_kana",  # 配送先姓(カナ)
            "first_name_kana",  # 配送先名(カナ)
            "zip",  # 郵便番号
            "country",  # 国
            "prefecture",  # 都道府県
            "city",  # 市区町村
            "address_1",  # 住所1
            "address_2",  # 住所2
            "tel_1",  # 電話番号1
            "tel_2",  # 電話番号2
            "fax",  # FAX
            "address_1",  # メールアドレス1
            "address_2",  # メールアドレス2
            "payment_method_name",  # 決済方法
            "delivery_method_name",  # 引取方法
            "event_title",  # イベント
            "performance_name",  # 公演
            "performance_code",  # 公演コード
            "performance_start_on",  # 公演日
            "venue_name",  # 会場
            "product_name",  # 商品名
            "product_price",  # 商品単価
            "product_quantity", # 商品個数
            "product_sales_segment",  # 販売区分
            "item_name",  # 商品明細名
            "item_price",  # 商品明細単価
            #"item_quantity",  # 商品明細個数
            "seat_quantity",  # 商品明細個数
            "item_print_histories",  #発券作業者
            "seat_name",  # 座席名
        ] + query.extra_headers

    headers = [
        ('Content-Type', 'application/octet-stream; charset=Windows-31J'),
        ('Content-Disposition', 'attachment; filename=orders_{date}.csv'.format(date=datetime.now().strftime('%Y%m%d%H%M%S')))
    ]

    response = Response(headers=headers)
    ordered_product_metadata_provider_registry = get_ordered_product_metadata_provider_registry(request)
    iheaders = header_intl(csv_headers, japanese_columns,
                           ordered_product_metadata_provider_registry)
    logger.debug("csv headers = {0}".format(csv_headers))
    results = list(query)

    # from .download import MailPermissionCache
    # mail_perms = set([m['email'] for m in 
    #                   MailPermissionCache(slave_session,
    #                                       organization_id,
    #                                       condition=form_search)])

    # for row in results:
    #     m1, m2 = row.get('email_1'), row.get('email_2')
    #     if m1 in mail_perms or m2 in mail_perms:
    #         row['mail_permission'] = '1'
    #     else:
    #         row['mail_permission'] = ''

    writer = csv.writer(response, delimiter=',')

    if excel_csv:
        def render_text(v):
            if v is None:
                return u''
            return u'="{0}"'.format(v)
    else:
        def render_text(v):
            if v is None:
                return u''
            return v

    def render_plain(v):
        if not v:
            return u''
        return v

    def render_zip(v):
        if not v:
            return u''
        zip1, zip2 = v[:3], v[3:]
        return u'{0}-{1}'.format(zip1, zip2)

    def render_currency(v):
        from altair.app.ticketing.cart.helpers import format_number
        if v is None:
            return u''
        return format_number(float(v))

    renderers = dict()
    for n in ('total_amount', 'transaction_fee', 'delimiter', 'system_fee', 'special_fee', 'margin', 'product_margin', 'product_price', 'item_price'):
        renderers[n] = render_currency

    renderers['zip'] = render_zip

    # for n in ('created_at', 'paid_at', 'delivered_at', 'canceled_at', 'performance_start_on', 'product_quantity', 'item_quantity', 'seat_quantity'):
    #     renderers[n] = render_plain
    for n in ('order_no', 'tel_1', 'tel_2', 'fax'):
        renderers[n] = render_text

    def render(name, v):
        name, _, _ = name.partition('[')
        renderer = renderers.get(name, render_plain)
        return renderer(v)

    writer.writerows([[encode_to_cp932(c)
                       for c in iheaders]] +
                     [[encode_to_cp932(render(h, columns.get(h)))
                       for h in csv_headers]
                      for columns in results])
    return response

#########################################################################

@view_defaults(decorator=with_bootstrap, permission='sales_editor')
class Orders(BaseView):

    #@view_config(route_name='orders.index', renderer='altair.app.ticketing:templates/orders/index.html', permission='sales_counter')
    def index(self):
        slave_session = get_db_session(self.request, name="slave")

        organization_id = self.context.organization.id
        query = DBSession.query(Order).filter(Order.organization_id==organization_id)

        params = MultiDict(self.request.params)
        params["order_no"] = " ".join(self.request.params.getall("order_no"))

        form_search = OrderSearchForm(params, organization_id=organization_id)
        if form_search.validate():
            try:
                query = OrderSummarySearchQueryBuilder(form_search.data, lambda key: form_search[key].label.text)(slave_session.query(OrderSummary).filter(OrderSummary.organization_id==organization_id, OrderSummary.deleted_at==None))
            except QueryBuilderError as e:
                self.request.session.flash(e.message)

        if self.request.params.get('action') == 'checked':
            checked_orders = [o.lstrip('o:') for o in self.request.session.get('orders', []) if o.startswith('o:')]
            query = query.filter(Order.id.in_(checked_orders))

        page = int(self.request.params.get('page', 0))

        orders = paginate.Page(
            query,
            page=page,
            items_per_page=40,
            item_count=query.count(),
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':OrderForm(),
            'form_search':form_search,
            'orders':orders,
            'page': page,
        }

    @view_config(route_name='orders.download')
    def download(self):
        slave_session = get_db_session(self.request, name="slave")

        organization_id = self.context.organization.id
        query = slave_session.query(OrderSummary).filter(OrderSummary.organization_id==organization_id, OrderSummary.deleted_at==None)

        if self.request.params.get('action') == 'checked':
            checked_orders = [o.lstrip('o:') for o in self.request.session.get('orders', []) if o.startswith('o:')]
            if len(checked_orders) > 0:
                query = query.filter(Order.id.in_(checked_orders))
            else:
                raise HTTPFound(location=route_path('orders.index', self.request))
        else:
            form_search = OrderSearchForm(self.request.params, organization_id=organization_id)
            form_search.sort.data = None
            try:
                query = OrderSummarySearchQueryBuilder(form_search.data, lambda key: form_search[key].label.text, sort=False)(slave_session.query(OrderSummary).filter(OrderSummary.organization_id==organization_id, OrderSummary.deleted_at==None))
            except QueryBuilderError as e:
                self.request.session.flash(e.message)
                raise HTTPFound(location=route_path('orders.index', self.request))
            if query.count() > 5000 and not form_search.performance_id.data:
                self.request.session.flash(u'対象件数が多すぎます。(公演を指定すれば制限はありません)')
                raise HTTPFound(location=route_path('orders.index', self.request))
    
        # XXX: JOINしたら逆に遅くなった
        #query = query.options(
        #    joinedload('ordered_products'),
        #    joinedload('ordered_products.product'),
        #    joinedload('ordered_products.product.sales_segment'),
        #    joinedload('ordered_products.ordered_product_items'),
        #    joinedload('ordered_products.ordered_product_items.product_item'),
        #    joinedload('ordered_products.ordered_product_items.print_histories'),
        #    joinedload('ordered_products.ordered_product_items.seats'),
        #    joinedload('ordered_products.ordered_product_items._attributes'),
        #    ) \
        #    .filter(SalesSegment.deleted_at == None) \
        #    .filter(OrderedProduct.deleted_at == None) \
        #    .filter(OrderedProductItem.deleted_at == None) \
        #    .filter(Product.deleted_at == None) \
        #    .filter(ProductItem.deleted_at == None) \
        #    .filter(Seat.deleted_at == None) \
        #    .filter(OrderedProductAttribute.deleted_at == None)
        orders = query

        headers = [
            ('Content-Type', 'application/octet-stream; charset=Windows-31J'),
            ('Content-Disposition', 'attachment; filename=orders_{date}.csv'.format(date=datetime.now().strftime('%Y%m%d%H%M%S')))
        ]
        response = Response(headers=headers)

        export_type = int(self.request.params.get('export_type', OrderCSV.EXPORT_TYPE_ORDER))
        excel_csv = bool(self.request.params.get('excel_csv'))
        kwargs = {}
        if export_type:
            kwargs['export_type'] = export_type
        if excel_csv:
            kwargs['excel_csv'] = True
        order_csv = OrderCSV(organization_id=self.context.organization.id, localized_columns=get_japanese_columns(self.request), **kwargs)

        writer = csv.writer(response, delimiter=',', quoting=csv.QUOTE_ALL)
        writer.writerows([encode_to_cp932(column) for column in columns] for columns in order_csv(orders))

        return response


@view_defaults(decorator=with_bootstrap, permission='sales_editor', renderer='altair.app.ticketing:templates/orders/refund/index.html')
class OrdersRefundIndexView(BaseView):

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.organization_id = int(self.context.organization.id)

    @view_config(route_name='orders.refund.index')
    def index(self):
        if self.request.session.get('orders'):
            del self.request.session['orders']
        if self.request.session.get('ticketing.refund.condition'):
            del self.request.session['ticketing.refund.condition']

        form_search = OrderRefundSearchForm(organization_id=self.organization_id)
        page = 0
        orders = []

        return {
            'form':OrderForm(),
            'form_search':form_search,
            'page': page,
            'orders':orders,
        }

    @view_config(route_name='orders.refund.search')
    def search(self):
        slave_session = get_db_session(self.request, name="slave")
        if self.request.method == 'POST':
            refund_condition = self.request.params
        else:
            refund_condition = MultiDict(self.request.session.get('ticketing.refund.condition', []))
        form_search = OrderRefundSearchForm(refund_condition, organization_id=self.organization_id)
        if form_search.validate():
            query = Order.filter(Order.organization_id==self.organization_id)
            try:
                query = OrderSummarySearchQueryBuilder(form_search.data, lambda key: form_search[key].label.text)(slave_session.query(OrderSummary).filter(OrderSummary.organization_id==self.organization_id, OrderSummary.deleted_at==None))
            except QueryBuilderError as e:
                self.request.session.flash(e.message)

            if self.request.method == 'POST' and self.request.params.get('page', None) is None:
                # 検索結果のOrder.idはデフォルト選択状態にする
                checked_orders = set()
                for order in query:
                    checked_orders.add('o:%s' % order.id)
                self.request.session['orders'] = checked_orders
                self.request.session['ticketing.refund.condition'] = self.request.params.items()

            page = int(self.request.params.get('page', 0))
            orders = paginate.Page(
                query,
                page=page,
                items_per_page=40,
                item_count=query.count(),
                url=paginate.PageURL_WebOb(self.request)
            )
        else:
            page = 0
            orders = []

        return {
            'form':OrderForm(),
            'form_search':form_search,
            'page': page,
            'orders':orders,
        }

    @view_config(route_name='orders.refund.checked')
    def checked(self):
        slave_session = get_db_session(self.request, name="slave")
        refund_condition = MultiDict(self.request.session.get('ticketing.refund.condition', []))
        form_search = OrderRefundSearchForm(refund_condition, organization_id=self.organization_id)
        if form_search.validate():
            try:
                query = OrderSummarySearchQueryBuilder(form_search.data, lambda key: form_search[key].label.text)(slave_session.query(OrderSummary).filter(OrderSummary.organization_id==self.organization_id, OrderSummary.deleted_at==None))
            except QueryBuilderError as e:
                self.request.session.flash(e.message)

            checked_orders = [o.lstrip('o:') for o in self.request.session.get('orders', []) if o.startswith('o:')]
            query = query.filter(Order.id.in_(checked_orders))

            page = int(self.request.params.get('page', 0))
            orders = paginate.Page(
                query,
                page=page,
                items_per_page=40,
                item_count=query.count(),
                url=paginate.PageURL_WebOb(self.request)
            )
        else:
            page = 0
            orders = []

        return {
            'form':OrderForm(),
            'form_search':form_search,
            'page': page,
            'orders':orders,
        }


@view_defaults(decorator=with_bootstrap, permission='sales_editor', renderer='altair.app.ticketing:templates/orders/refund/confirm.html')
class OrdersRefundConfirmView(BaseView):

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)

        self.checked_orders = [o.lstrip('o:') for o in self.request.session.get('orders', []) if o.startswith('o:')]
        self.refund_condition = MultiDict(self.request.session.get('ticketing.refund.condition', []))
        self.organization_id = int(self.context.organization.id)
        self.form_search = OrderRefundSearchForm(self.refund_condition, organization_id=self.organization_id)

    @view_config(route_name='orders.refund.confirm', request_method='GET')
    def get(self):
        if not self.checked_orders:
            self.request.session.flash(u'払戻対象を選択してください')
            return HTTPFound(location=route_path('orders.refund.checked', self.request))

        params = MultiDict()
        if self.form_search.payment_method.data:
            params.add('payment_method_id', self.form_search.payment_method.data)
        form_refund = OrderRefundForm(params, organization_id=self.organization_id)
        return {
            'orders':self.checked_orders,
            'refund_condition':self.refund_condition,
            'form_search':self.form_search,
            'form_refund':form_refund,
        }

    @view_config(route_name='orders.refund.confirm', request_method='POST')
    def post(self):
        if not self.checked_orders:
            self.request.session.flash(u'払戻対象を選択してください')
            return HTTPFound(location=route_path('orders.refund.checked', self.request))

        orders = Order.query.filter(Order.id.in_(self.checked_orders)).all()
        form_refund = OrderRefundForm(
            self.request.POST,
            organization_id=self.organization_id,
            orders=orders
        )
        if not form_refund.validate():
            return {
                'orders':self.checked_orders,
                'refund_condition':self.refund_condition,
                'form_search':self.form_search,
                'form_refund':form_refund,
            }

        # 払戻予約
        refund_param = form_refund.data
        refund_param.update(dict(orders=orders))
        Order.reserve_refund(refund_param)

        del self.request.session['orders']
        del self.request.session['ticketing.refund.condition']

        self.request.session.flash(u'払戻予約しました')
        return HTTPFound(location=route_path('orders.refund.index', self.request))


@view_defaults(decorator=with_bootstrap, permission='sales_counter')
class OrderDetailView(BaseView):
    @view_config(route_name='orders.show', renderer='altair.app.ticketing:templates/orders/show.html')
    def show(self):
        order = self.context.order
        if order is None:
            raise HTTPNotFound('order id %d is not found' % self.context.order_id)

        dependents = self.context.get_dependents_models(order)
        order_history = dependents.histories
        mail_magazines = dependents.mail_magazines

        joined_objects_for_product_item = dependents.describe_objects_for_product_item_provider()
        ordered_product_attributes = joined_objects_for_product_item.get_product_item_attributes(
            get_ordered_product_metadata_provider_registry(self.request)
        )
        order_attributes = dependents.get_order_attributes(
            get_order_metadata_provider_registry(self.request)
        )

        forms = self.context.get_dependents_forms(order)
        form_shipping_address = forms.get_shipping_address_form()
        form_order = forms.get_order_form()
        form_order_reserve = forms.get_order_reserve_form()
        form_refund = forms.get_order_refund_form()

        return {
            'is_current_order': order.deleted_at is None, 
            'order':order,
            'ordered_product_attributes': ordered_product_attributes,
            'order_attributes': order_attributes,
            'order_history':order_history,
            'point_grant_settings': loyalty_api.applicable_point_grant_settings_for_order(order),
            'sej_order':SejOrder.query.filter(SejOrder.order_no==order.order_no).order_by(desc(SejOrder.branch_no)).first(),
            'mail_magazines':mail_magazines,
            'form_shipping_address':form_shipping_address,
            'form_order':form_order,
            'form_order_reserve':form_order_reserve,
            'form_refund':form_refund,
            'form_order_edit_attribute': forms.get_order_edit_attribute(), 
            "objects_for_describe_product_item": joined_objects_for_product_item()
        }

    @view_config(route_name='orders.cancel', permission='sales_editor')
    def cancel(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        if order.cancel(self.request):
            notify_order_canceled(self.request, order)
            self.request.session.flash(u'受注(%s)をキャンセルしました' % order.order_no)
            return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))
        else:
            self.request.session.flash(u'受注(%s)をキャンセルできません' % order.order_no)
            raise HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

    @view_config(route_name='orders.delete', permission='administrator')
    def delete(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        try:
            order.delete()
        except Exception:
            self.request.session.flash(u'受注(%s)を非表示にできません' % order.order_no)
            raise HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

        self.request.session.flash(u'受注(%s)を非表示にしました' % order.order_no)
        return HTTPFound(location=route_path('orders.index', self.request))

    @view_config(route_name='orders.refund.immediate', permission='sales_editor')
    def refund_immediate(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        f = OrderRefundForm(
            self.request.POST,
            organization_id=self.context.organization.id,
            orders=[order]
        )
        if f.validate():
            refund_param = f.data
            refund_param.update(dict(orders=[order]))
            Order.reserve_refund(refund_param)
            if order.call_refund(self.request):
                self.request.session.flash(u'受注(%s)を払戻しました' % order.order_no)
                return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
            else:
                self.request.session.flash(u'受注(%s)を払戻できません' % order.order_no)

        response = render_to_response('altair.app.ticketing:templates/orders/refund/_form.html', {'form':f}, request=self.request)
        response.status_int = 400
        return response

    @view_config(route_name='orders.change_status', permission='sales_editor')
    def change_status(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        status = self.request.matchdict.get('status', 0)
        if order.change_status(status):
            self.request.session.flash(u'受注(%s)のステータスを変更しました' % order.order_no)
        else:
            self.request.session.flash(u'受注(%s)のステータスを変更できません' % order.order_no)
        return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

    @view_config(route_name='orders.delivered', permission='sales_editor')
    def delivered(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        if order.delivered():
            self.request.session.flash(u'受注(%s)を配送済みにしました' % order.order_no)
        else:
            self.request.session.flash(u'受注(%s)を配送済みにできません' % order.order_no)
        return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

    @view_config(route_name='orders.undelivered', permission='sales_editor')
    def undelivered(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)
            
        if order.undelivered():
            self.request.session.flash(u'受注(%s)を未配送にしました' % order.order_no)
        else:
            self.request.session.flash(u'受注(%s)を未配送済みにできません' % order.order_no)
        return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

    @view_config(route_name='orders.edit.shipping_address', request_method='POST', renderer='altair.app.ticketing:templates/orders/_form_shipping_address.html')
    def edit_shipping_address_post(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        f = ClientOptionalForm(self.request.POST)
        if f.validate():
            shipping_address = merge_session_with_post(order.shipping_address or ShippingAddress(), f.data)
            shipping_address.tel_1 = f.tel_1.data
            shipping_address.email_1 = f.email_1.data
            shipping_address.email_2 = f.email_2.data
            order.shipping_address = shipping_address
            order.save()

            self.request.session.flash(u'予約を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='orders.edit.product', request_method='POST')
    def edit_product_post(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        f = OrderForm(self.request.POST)
        has_error = False

        try:
            if not f.validate():
                raise ValidationError()
            new_order = Order.clone(order, deep=True)
            new_order.system_fee = f.system_fee.data
            new_order.transaction_fee = f.transaction_fee.data
            new_order.delivery_fee = f.delivery_fee.data
            new_order.special_fee = f.special_fee.data
            new_order.special_fee_name = f.special_fee_name.data

            for op, nop in itertools.izip(order.items, new_order.items):
                # 個数が変更できるのは数受けのケースのみ
                if op.product.seat_stock_type.quantity_only:
                    nop.quantity = int(self.request.params.get('product_quantity-%d' % op.id) or 0)
                for opi, nopi in itertools.izip(op.ordered_product_items, nop.ordered_product_items):
                    nopi.price = int(self.request.params.get('product_item_price-%d' % opi.id) or 0)
                    if op.product.seat_stock_type.quantity_only:
                        stock_status = opi.product_item.stock.stock_status
                        new_quantity = nop.quantity * nopi.product_item.quantity
                        old_quantity = op.quantity
                        if stock_status.quantity < (new_quantity - old_quantity):
                            raise NotEnoughStockException(stock_status.stock, stock_status.quantity, new_quantity)
                        stock_status.quantity -= (new_quantity - old_quantity)
                        nopi.quantity = new_quantity
                nop.price = sum(nopi.price * nopi.product_item.quantity for nopi in nop.ordered_product_items)

            total_amount = sum(nop.price * nop.quantity for nop in new_order.items)\
                           + new_order.system_fee + new_order.transaction_fee + new_order.delivery_fee + new_order.special_fee
            if new_order.payment_status != 'unpaid':
                if total_amount != new_order.total_amount:
                    raise ValidationError(u'入金済みの為、合計金額は変更できません')
            new_order.total_amount = total_amount

            new_order.save()
        except ValidationError, e:
            if e.message:
                self.request.session.flash(e.message)
            has_error = True
        except NotEnoughStockException, e:
            logger.info("not enough stock quantity :%s" % e)
            self.request.session.flash(u'在庫がありません')
            has_error = True
        except Exception, e:
            logger.info('save error (%s)' % e.message, exc_info=sys.exc_info())
            self.request.session.flash(u'入力された金額および個数が不正です')
            has_error = True
        finally:
            if has_error:
                response = render_to_response('altair.app.ticketing:templates/orders/_form_product.html', {'form':f, 'order':order}, request=self.request)
                response.status_int = 400
                return response

        self.request.session.flash(u'予約を保存しました')
        return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

    @view_config(route_name="orders.cover.preview", request_method="GET", renderer="altair.app.ticketing:templates/orders/_cover_preview_dialog.html")
    def cover_preview_dialog(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            raise HTTPNotFound('order id %d is not found' % order_id)
        cover = TicketCover.get_from_order(order)
        if cover is None:
            raise HTTPNotFound('cover is not found. order id %d' % order_id)
        svg_builder = get_svg_builder(self.request)
        svg = svg_builder.build(cover.ticket, build_cover_dict_from_order(order))
        data = {"ticket_format": cover.ticket.ticket_format_id, "sx": "1", "sy": "1"}
        transformer = SVGTransformer(svg, data)
        svg = transformer.transform()
        preview = SVGPreviewCommunication.get_instance(self.request)
        imgdata_base64 = preview.communicate(self.request, svg)
        return {"order": order, "cover":cover, "data": imgdata_base64}

    @view_config(route_name="orders.ticket.placeholder", request_method="GET", renderer='json')
    def order_ticket_placeholder_data(self):
        order = self.context.order
        tickets = Ticket.query \
            .filter(OrderedProduct.order_id==order.id)\
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(ProductItem.id==OrderedProductItem.product_item_id)\
            .filter(TicketBundle.id==ProductItem.ticket_bundle_id)\
            .filter(Ticket_TicketBundle.ticket_bundle_id==TicketBundle.id)\
            .filter(Ticket.id==Ticket_TicketBundle.ticket_id)\
            .options(joinedload(Ticket.ticket_format))\
            .all()

        delivery_method = order.payment_delivery_pair.delivery_method
        tickets = [t for t in tickets if any(dm == delivery_method for dm in t.ticket_format.delivery_methods)]

        placeholders = set()
        for t in tickets:
            placeholders = placeholders.union(get_placeholders_from_ticket(self.request, t))
        placeholders = sorted([ph for ph in placeholders if not "." in ph or ph.startswith("aux.")])
        return {"placeholders": placeholders}


    @view_config(route_name="orders.item.preview", request_method="GET", renderer='altair.app.ticketing:templates/orders/_item_preview_dialog.html')
    def order_item_preview_dialog(self):
        item = OrderedProductItem.query.filter_by(id=self.request.matchdict["item_id"]).first()
        if item is None:
            return {} ### xxx:
        form = PreviewTicketSelectForm(item_id=item.id, ticket_formats=available_ticket_formats_for_ordered_product_item(item))
        return {"form": form, "item": item}

    @view_config(route_name="orders.item.preview.getdata", request_method="GET", renderer="json")
    def order_item_get_data_for_preview(self):
        item = OrderedProductItem.query.filter_by(id=self.request.matchdict["item_id"]).one()
        ticket_format = TicketFormat.query.filter_by(id=self.request.matchdict["ticket_format_id"]).one()
        tickets = Ticket.query \
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(ProductItem.id==OrderedProductItem.product_item_id)\
            .filter(TicketBundle.id==ProductItem.ticket_bundle_id)\
            .filter(Ticket_TicketBundle.ticket_bundle_id==TicketBundle.id)\
            .filter(Ticket.id==Ticket_TicketBundle.ticket_id)\
            .filter(Ticket.ticket_format_id==ticket_format.id)\
            .filter(OrderedProductItem.id==item.id)\
            .all()
        dicts = build_dicts_from_ordered_product_item(item, ticket_number_issuer=NumberIssuer())
        data = dict(ticket_format.data)
        data["ticket_format_id"] = ticket_format.id
        results = []
        names = []
        svg_builder = get_svg_builder(self.request)
        for seat, dict_ in dicts:
            names.append(seat.name if seat else dict_["product"]["name"])
            preview_type = utils.delivery_type_from_built_dict(dict_)

            for ticket in tickets:
                svg = svg_builder.build(ticket, dict_)
                r = data.copy()
                r["preview_type"] = preview_type
                r.update(drawing=svg)
                results.append(r)

        ticket_dicts = [{"name": t.name, "id": t.id, "url": self.request.route_path("events.tickets.boundtickets.show", event_id=t.event_id, id=t.id)}
                        for t in tickets]
        return {"results": results, "names": names, "ticket_dicts": ticket_dicts}

    @view_config(route_name="orders.attributes_edit", request_method="POST")
    def edit_order_attributes(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'不正なデータです',
            }))
        ## todo:validation?
        params = {k.decode("utf-8"):v for k, v in self.request.POST.items() if not k.startswith("_")}
        order = OrderAttributeManager.update(order, params)
        order.save()
        self.request.session.flash(u'属性を変更しました')
        return HTTPFound(self.request.route_path(route_name="orders.show", order_id=order_id)+"#order_attributes")

    @view_config(route_name="orders.memo_on_order", request_method="POST", renderer="json")
    def edit_memo_on_order(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'不正なデータです',
            }))

        f = OrderMemoEditFormFactory(3)(MultiDict(self.request.json_body))
        if not f.validate():
            raise HTTPBadRequest(body=json.dumps({
                'message':f.get_error_messages(), 
            }))
        marker = object()
        #logger.debug(self.request.json_body)
        for k, v in f.get_result():
            old = order.attributes.get(k, marker)
            if v or old is not marker:
                order.attributes[k] = v
        order.save()
        return {}
        
    @view_config(route_name='orders.note', request_method='POST', renderer='json', permission='sales_counter')
    def note(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'不正なデータです',
            }))

        f = OrderReserveForm(MultiDict(self.request.json_body))
        if not f.note.validate(f):
            raise HTTPBadRequest(body=json.dumps({
                'message':f.note.errors,
            }))

        order.note = f.note.data
        order.save()
        return {}

    @view_config(route_name='orders.sales_summary', renderer='altair.app.ticketing:templates/orders/_sales_summary.html', permission='sales_counter')
    def sales_summary(self):
        performance_id = int(self.request.params.get('performance_id') or 0)
        performance = Performance.get(performance_id, self.context.organization.id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        sales_segments = performance.sales_segments
        sales_segment_id = int(self.request.params.get('sales_segment_id') or 0)
        if sales_segment_id:
            sales_segments = [ss for ss in sales_segments if ss.id == sales_segment_id]

        sales_summary = []
        for stock_type in performance.stock_types:
            stock_data = []
            stocks = Stock.filter(Stock.performance_id==performance_id)\
                .options(joinedload('stock_status'))\
                .filter(Stock.stock_type_id==stock_type.id)\
                .filter(Stock.quantity>0)\
                .filter(exists().where(and_(ProductItem.performance_id==performance_id, ProductItem.stock_id==Stock.id))).all()
            for stock in stocks:
                products = [p for p in performance.products if stock in p.stocks and p.sales_segment in sales_segments]
                if products:
                    stock_data.append(dict(
                        stock=stock,
                        products=sorted(products, key=lambda x:(x.sales_segment.order, x.price)),
                    ))
            sales_summary.append(dict(
                stock_type=stock_type,
                total_quantity=sum([s.get('stock').quantity for s in stock_data]),
                rest_quantity=sum([s.get('stock').stock_status.quantity for s in stock_data]),
                stocks=stock_data
            ))

        return {
            'sales_summary':sales_summary
        }

    @view_config(route_name="orders.issue_status", request_method="POST", request_param='issued')
    def issue_status(self):
        order = Order.query.get(self.request.matchdict["order_id"])
        order.issued = int(self.request.params['issued'])
        return HTTPFound(location=self.request.route_path('orders.show', order_id=order.id))

    @view_config(route_name="orders.print.queue.dialog", request_method="GET", renderer="altair.app.ticketing:templates/orders/_print_queue_dialog.html")
    def print_queue_dialog(self):
        order = Order.query.get(self.request.matchdict["order_id"])
        return {"order": order}


    @view_config(route_name="orders.checked.queue", request_method="POST", permission='sales_counter')
    def enqueue_checked_order(self):
        ords = self.request.session.get("orders", [])
        ords = [o.lstrip("o:") for o in ords if o.startswith("o:")]

        qs = DBSession.query(Order)\
            .filter(Order.deleted_at==None).filter(Order.id.in_(ords))\
            .filter(Order.issued==False)\
            .options(joinedload(Order.operator))

        for order in qs:
            if not order.operator.is_member_of_organization(self.context.user.organization):
                continue
            if not order.queued:
                utils.enqueue_cover(operator=self.context.user, order=order)
                utils.enqueue_for_order(operator=self.context.user, order=order)

        # def clean_session_callback(request):
        logger.info("*ticketing print queue many* clean session")
        session_values = self.request.session.get("orders", [])
        for order in qs:
            session_values.remove("o:%s" % order.id)
        self.request.session["orders"] = session_values
        # self.request.add_finished_callback(clean_session_callback)
        self.request.session.flash(u'券面を印刷キューに追加しました. (既に印刷済みの注文は印刷キューに追加されません)')
        if self.request.POST.get("redirect_url"):
            return HTTPFound(location=self.request.POST.get("redirect_url"))
        return HTTPFound(location=self.request.route_path('orders.index'))

    @view_config(route_name="orders.print.queue.each")
    def order_tokens_print_queue(self):
        order = self.context.order
        if order is None:
            raise HTTPNotFound('order id %d is not found' % self.context.order_id)

        #token@seat@ticket.id
        actions = self.context.get_dependents_actions(order)
        candidates_action = actions.get_print_candidate_action(self.request.POST.getall("candidate_id"))
        candidates_action.enqueue(operator=self.context.user)
        self.request.session.flash(u'券面を印刷キューに追加しました')
        return HTTPFound(location=self.request.route_path('orders.show', order_id=order.id))
        
    @view_config(route_name='orders.print.queue')
    def order_print_queue(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.query.get(order_id)
        utils.enqueue_cover(operator=self.context.user, order=order)
        utils.enqueue_for_order(operator=self.context.user, order=order)
        self.request.session.flash(u'券面を印刷キューに追加しました')
        return HTTPFound(location=self.request.route_path('orders.show', order_id=order_id))

    @view_config(route_name="orders.checked.delivered", request_method="POST", permission='sales_counter')
    def change_checked_orders_to_delivered(self):
        ords = self.request.session.get("orders", [])
        ords = [o.lstrip("o:") for o in ords if o.startswith("o:")]
        qs = Order.query.filter(Order.organization_id==self.context.organization.id)\
                        .filter(Order.id.in_(ords))        
        exist_order_ids = set()
        fail_nos = []
        for order in qs:
            exist_order_ids.add(str(order.id))
            no = order.order_no
            status = order.delivered()
            if not status:
                fail_nos.append(no)

        request_ids = set(ords)
        lost_order_ids = request_ids - exist_order_ids

        if fail_nos:
            nos_str = ', '.join(fail_nos)            
            self.request.session.flash(u'配送済に変更できない注文が含まれていました。')
            self.request.session.flash(u'({0})'.format(nos_str))

        if lost_order_ids:
            ids_str = ', '.join(map(repr, lost_order_ids))
            self.request.session.flash(u'存在しない注文が含まれていました。')
            self.request.session.flash(u'({0})'.format(ids_str))
            
        return HTTPFound(location=self.request.route_path('orders.index'))

    @view_config(route_name='orders.fraud.clear', permission='sales_editor')
    def fraud_clear(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        order.fraud_suspect = 0
        order.save()

        self.request.session.flash(u'不正アラートを解除しました')
        return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))


@view_defaults(decorator=with_bootstrap, permission='sales_counter')
class OrdersReserveView(BaseView):

    def release_seats(self, venue, l0_ids):
        # 確保座席があるならステータスを戻す
        logger.info("release seats : %s" % l0_ids)
        if l0_ids:
            seat_statuses = SeatStatus.filter(SeatStatus.status.in_([int(SeatStatusEnum.Keep), int(SeatStatusEnum.InCart)]))\
                .join(SeatStatus.seat)\
                .filter(and_(Seat.l0_id.in_(l0_ids), Seat.venue_id==venue.id))\
                .with_lockmode('update').all()
            for seat_status in seat_statuses:
                logger.info("seat(%s) status InCart to Vacant" % seat_status.seat_id)
                seat_status.status = int(SeatStatusEnum.Vacant)
                seat_status.save()

    def get_inner_cart_session(self):
        inner_cart_session = self.request.session.get('altair.app.ticketing.inner_cart')
        logger.info("inner cart session : %s" % inner_cart_session)
        if inner_cart_session is None:
            raise InnerCartSessionException('Inner cart session is expired')
        return inner_cart_session

    def clear_inner_cart_session(self):
        inner_cart_session = self.request.session.get('altair.app.ticketing.inner_cart')
        logger.info("clear cart session : %s" % inner_cart_session)

        if inner_cart_session:
            if inner_cart_session.get('seats'):
                venue = Venue.get(inner_cart_session.get('venue_id'))
                self.release_seats(venue, inner_cart_session.get('seats'))
            del self.request.session['altair.app.ticketing.inner_cart']

    @view_config(route_name='orders.api.get', renderer='json')
    def get_order_by_seat(self):
        l0_id = self.request.params.get('l0_id', 0)
        performance_id = self.request.params.get('performance_id', 0)
        logger.debug('call get order api (seat l0_id = %s)' % l0_id)
        order = Order.filter_by(organization_id=self.context.organization.id)\
            .filter(Order.performance_id==performance_id)\
            .filter(Order.canceled_at==None)\
            .join(Order.ordered_products)\
            .join(OrderedProduct.ordered_product_items)\
            .join(OrderedProductItem.seats)\
            .filter(Seat.l0_id==l0_id).first()
        if not order:
            raise HTTPBadRequest(body=json.dumps({'message':u'予約データが見つかりません'}))

        name = order.shipping_address.last_name + order.shipping_address.first_name if order.shipping_address else ''
        products = [ordered_product.product.name for ordered_product in order.ordered_products]
        seat_names = []
        for op in order.ordered_products:
            for opi in op.ordered_product_items:
                seat_names += [seat.name for seat in opi.seats]

        return {
            'order_no':order.order_no,
            'name':name,
            'price':int(order.total_amount),
            'products':products,
            'seat_names':seat_names
        }

    @view_config(route_name='orders.reserve.form', request_method='POST', renderer='altair.app.ticketing:templates/orders/_form_reserve.html')
    def reserve_form(self):
        post_data = MultiDict(self.request.json_body)
        logger.debug('order reserve post_data=%s' % post_data)

        performance_id = int(post_data.get('performance_id', 0))
        sales_segment_id = int(post_data.get('sales_segment_id', 0))
        performance = Performance.get(performance_id, self.context.organization.id)
        if performance is None:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'パフォーマンスが存在しません',
            }))

        # 古いカートのセッションが残っていたら削除
        old_cart = api.get_cart(self.request)
        if old_cart:
            old_cart.release()
            api.remove_cart(self.request)

        # 古い確保座席がセッションに残っていたら削除
        self.clear_inner_cart_session()

        stocks = post_data.get('stocks')
        form_reserve = OrderReserveForm(post_data, performance_id=performance_id, stocks=stocks, sales_segment_id=sales_segment_id)
        form_reserve.sales_segment_id.validators = [Optional()]
        form_reserve.payment_delivery_method_pair_id.validators = [Optional()]
        form_reserve.validate()

        # 選択されたSeatがあるならステータスをKeepにして確保する
        seats = []
        if post_data.get('seats'):
            try:
                reserving = api.get_reserving(self.request)
                stock_status = [(stock, 0) for stock in StockStatus.filter(StockStatus.stock_id.in_(stocks))]
                seats = reserving.reserve_selected_seats(stock_status, performance_id, post_data.get('seats'), reserve_status=SeatStatusEnum.Keep)
            except InvalidSeatSelectionException:
                logger.info("seat selection is invalid.")
                raise HTTPBadRequest(body=json.dumps({'message':u'既に予約済か選択できない座席です。画面を最新の情報に更新した上で再度座席を選択してください。'}))
            except Exception, e:
                logger.exception('save error (%s)' % e.message)
                raise HTTPBadRequest(body=json.dumps({'message':u'エラーが発生しました'}))

        # セッションに保存
        self.request.session['altair.app.ticketing.inner_cart'] = {
            'venue_id':performance.venue.id,
            'stocks':post_data.get('stocks'),
            'seats':post_data.get('seats'),
        }
        return {
            'seats':seats,
            'form':form_reserve,
            'form_order_edit_attribute': OrderMemoEditFormFactory(3)(), 
            'performance':performance,
        }

    @view_config(route_name='orders.reserve.form.reload', request_method='POST', renderer='altair.app.ticketing:templates/orders/_form_reserve.html')
    def reserve_form_reload(self):
        post_data = MultiDict(self.request.json_body)
        post_data.update(self.get_inner_cart_session())
        performance_id = int(post_data.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.organization.id)

        f = OrderReserveForm(post_data, performance_id=performance_id, stocks=post_data.get('stocks'), sales_segment_id=post_data.get('sales_segment_id'))
        selected_seats = Seat.query.filter(and_(
            Seat.l0_id.in_(post_data.get('seats')),
            Seat.venue_id==post_data.get('venue_id')
        )).all()

        return {
            'seats':selected_seats,
            'form':f,
            'form_order_edit_attribute': OrderMemoEditFormFactory(3)(post_data), 
            'performance':performance,
        }

    @view_config(route_name='orders.reserve.confirm', request_method='POST', renderer='altair.app.ticketing:templates/orders/_form_reserve_confirm.html')
    def reserve_confirm(self):
        post_data = MultiDict(self.request.json_body)

        performance_id = int(post_data.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.organization.id)
        if performance is None:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'パフォーマンスが存在しません',
            }))

        try:
            post_data.update(self.get_inner_cart_session())
            logger.debug('order reserve confirm post_data=%s' % post_data)

            # validation
            f = OrderReserveForm(performance_id=performance_id, stocks=post_data.get('stocks'), sales_segment_id=post_data.get('sales_segment_id'), request=self.request)
            f.process(post_data)
            if not f.validate():
                raise ValidationError(reduce(lambda a,b: a+b, f.errors.values(), []))

            ## memo
            form_order_edit_attribute = OrderMemoEditFormFactory(3)(post_data)
            if not form_order_edit_attribute.validate():
                raise ValidationError(form_order_edit_attribute.get_error_messages())

            seats = post_data.get('seats')
            order_items = []
            total_quantity = 0
            for product_id, product_name in f.products.choices:
                quantity = post_data.get('product_quantity-%d' % product_id)
                if not quantity:
                    continue
                quantity = quantity.encode('utf-8')
                if not quantity.isdigit():
                    raise ValidationError(u'個数が不正です')
                product_quantity = int(quantity)
                product = DBSession.query(Product).filter_by(id=product_id).one()
                total_quantity += product_quantity * product.get_quantity_power(product.seat_stock_type, performance_id)
                order_items.append((product, product_quantity))

            if not total_quantity:
                raise ValidationError(u'個数を入力してください')
            elif seats and total_quantity != len(seats):
                raise ValidationError(u'個数の合計数（%d）が選択した座席数（%d席）と一致しません' % (total_quantity, len(seats)))

            # 選択されたSeatのステータスをいったん戻してカートデータとして再確保する
            self.release_seats(performance.venue, seats)

            # create cart
            sales_segment = SalesSegment.get(f.sales_segment_id.data)
            cart = api.order_products(self.request, sales_segment.id, order_items, selected_seats=seats)
            cart.sales_segment = sales_segment
            pdmp = DBSession.query(PaymentDeliveryMethodPair).filter_by(id=post_data.get('payment_delivery_method_pair_id')).one()
            cart.payment_delivery_pair = pdmp
            cart.channel = ChannelEnum.INNER.v
            cart.operator = self.context.user

            # コンビニ決済は通知を行うので購入者情報が必要
            if cart.payment_delivery_pair.id in f.payment_delivery_method_pair_id.sej_plugin_id:
                cart.shipping_address = ShippingAddress(
                    first_name=f.first_name.data,
                    last_name=f.last_name.data,
                    first_name_kana=f.first_name_kana.data,
                    last_name_kana=f.last_name_kana.data,
                    tel_1=f.tel_1.data,
                )

            DBSession.add(cart)
            DBSession.flush()
            api.set_cart(self.request, cart)

            return {
                'cart':cart,
                'form':f,
                'performance': performance,
                'form_order_edit_attribute': form_order_edit_attribute
            }
        except ValidationError, e:
            raise HTTPBadRequest(body=json.dumps({'message':e.message}))
        except NotEnoughAdjacencyException:
            logger.info("not enough adjacency")
            raise HTTPBadRequest(body=json.dumps({'message':u'連席で座席を確保できません。座席を直接指定するか、席数を減らして確保してください。'}))
        except InvalidSeatSelectionException:
            logger.info("seat selection is invalid.")
            raise HTTPBadRequest(body=json.dumps({'message':u'既に予約済か選択できない座席です。画面を最新の情報に更新した上で再度座席を選択してください。'}))
        except NotEnoughStockException as e:
            logger.info("not enough stock quantity :%s" % e)
            raise HTTPBadRequest(body=json.dumps({'message':u'在庫がありません'}))
        except InnerCartSessionException as e:
            logger.info("%s" % e.message)
            raise HTTPBadRequest(body=json.dumps({'message':u'エラーが発生しました。もう一度選択してください。'}))
        except Exception, e:
            logger.exception('save error (%s)' % e.message)
            raise HTTPBadRequest(body=json.dumps({'message':u'エラーが発生しました'}))

    @view_config(route_name='orders.reserve.complete', request_method='POST', renderer='json')
    def reserve_complete(self):
        post_data = MultiDict(self.request.json_body)
        with_enqueue = post_data.get('with_enqueue', False)

        performance_id = int(post_data.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.organization.id)
        if performance is None:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'パフォーマンスが存在しません',
            }))

        try:
            # create order
            cart = api.get_cart_safe(self.request)
            note = post_data.get('note')
            order = create_inner_order(cart, note)

            # 窓口での決済方法
            attr = 'sales_counter_payment_method_id'
            sales_counter_id = int(post_data.get(attr, 0))
            if sales_counter_id:
                order.attributes[attr] = sales_counter_id

                # 窓口で決済済みなら決済済みにする (コンビニ決済以外)
                payment_plugin_id = order.payment_delivery_pair.payment_method.payment_plugin_id
                if payment_plugin_id != payments_plugins.SEJ_PAYMENT_PLUGIN_ID:
                    order.paid_at = datetime.now()

            ## memo
            form_order_edit_attribute = OrderMemoEditFormFactory(3)(post_data)
            if not form_order_edit_attribute.validate():
                raise HTTPBadRequest(body=json.dumps({
                    "message": u"文言・メモの設定でエラーが発生しました",
                }))
            for k, v in form_order_edit_attribute.get_result():
                if v:
                    order.attributes[k] = v


            if with_enqueue:
                utils.enqueue_for_order(operator=self.context.user, order=order)

            # clear session
            api.remove_cart(self.request)
            if self.request.session.get('altair.app.ticketing.inner_cart'):
                del self.request.session['altair.app.ticketing.inner_cart']

            return dict(order_id=order.id)
        except NoCartError, e:
            logger.info("%s" % e.message)
            raise HTTPBadRequest(body=json.dumps({'message':u'エラーが発生しました。もう一度選択してください。'}))
        except Exception, e:
            logger.exception('save error (%s)' % e.message)
            raise HTTPBadRequest(body=json.dumps({'message':u'エラーが発生しました'}))

    @view_config(route_name='orders.reserve.reselect', request_method='POST', renderer='json')
    def reserve_reselect(self):
        try:
            # release cart
            cart = api.get_cart(self.request)
            if cart:
                cart.release()
            api.remove_cart(self.request)

            # clear session
            self.clear_inner_cart_session()

            return {}
        except Exception, e:
            logger.exception('save error (%s)' % e.message)
            raise HTTPBadRequest(body=json.dumps({
                'message':u'エラーが発生しました',
            }))


from altair.app.ticketing.sej.models import SejOrder, SejTicket, SejTicketTemplateFile, SejRefundEvent, SejRefundTicket, SejTenant
from altair.app.ticketing.sej.ticket import SejTicketDataXml
from altair.app.ticketing.sej.payment import request_update_order, request_cancel_order
from altair.app.ticketing.sej.models import code_from_ticket_type, code_from_update_reason, code_from_payment_type
from altair.app.ticketing.sej.exceptions import  SejServerError
from altair.app.ticketing.sej import api as sej_api

from sqlalchemy import or_, and_
from pyramid.threadlocal import get_current_registry

@view_defaults(decorator=with_bootstrap, permission='administrator')
class SejOrderView(object):

    def __init__(self, request):
        self.request = request

    @view_config(route_name='orders.sej', renderer='altair.app.ticketing:templates/sej/index.html')
    def index_get(self):
        sort = self.request.GET.get('sort', 'SejOrder.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        filter = None
        query_str = self.request.GET.get('q', None)
        if query_str:
           filter = or_(
               SejOrder.billing_number.like('%'+ query_str +'%'),
               SejOrder.exchange_number.like('%'+ query_str + '%'),
               SejOrder.order_no.like('%'+ query_str + '%'),
               SejOrder.user_name.like('%'+ query_str + '%'),
               SejOrder.user_name_kana.like('%'+ query_str + '%'),
               SejOrder.email.like('%'+ query_str + '%'),
           )
        else:
            query_str = ''

        query = SejOrder.filter(filter).order_by(sort + ' ' + direction)
        orders = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'q' : query_str,
            'orders': orders
        }

@view_defaults(decorator=with_bootstrap, permission='administrator')
class SejOrderInfoView(object):

    def __init__(self, request):
        settings = get_current_registry().settings
        tenant = SejTenant.filter_by(organization_id=request.context.organization.id).first()
        self.sej_hostname = (tenant and tenant.inticket_api_url) or settings.get('sej.inticket_api_url')
        self.shop_id = (tenant and tenant.shop_id) or settings.get('sej.shop_id')
        self.secret_key = (tenant and tenant.api_key) or settings.get('sej.api_key')

        self.request = request

    @view_config(route_name='orders.sej.order.request', request_method="GET", renderer='altair.app.ticketing:templates/sej/request.html')
    def order_request_get(self):
        f = SejOrderForm()
        ft = SejTicketForm()
        templates = SejTicketTemplateFile.query.all()
        return dict(
            form=f,
            ticket_form=ft,
            templates=templates
        )

    @view_config(route_name='orders.sej.order.request', request_method="POST", renderer='altair.app.ticketing:templates/sej/request.html')
    def order_request_post(self):
        f = SejOrderForm(self.request.POST)
        templates = SejTicketTemplateFile.query.all()
        if f.validate():
            return HTTPFound(location=route_path('orders.sej'))
        else:
            return dict(
                form=f,
                templates=templates
            )

    @view_config(route_name='orders.sej.order.info', request_method="GET", renderer='altair.app.ticketing:templates/sej/order_info.html')
    def order_info_get(self):
        order_no = self.request.matchdict.get('order_no', '')
        order = SejOrder.query.filter_by(order_no=order_no).order_by(desc(SejOrder.branch_no)).first()

        templates = SejTicketTemplateFile.query.all()
        f = SejOrderForm(order_no=order.order_no)
        tf = SejTicketForm()
        rf = SejRefundOrderForm()
        f.process(record_to_multidict(order))

        return dict(order=order, form=f, refund_form=rf, ticket_form=tf,templates=templates)


    @view_config(route_name='orders.sej.order.info', request_method="POST",  renderer='altair.app.ticketing:templates/sej/order_info.html')
    def order_info_post(self):
        order_no = self.request.matchdict.get('order_no', '')
        order = SejOrder.query.filter_by(order_no=order_no).order_by(desc(SejOrder.branch_no)).first()

        tickets = []
        for ticket in order.tickets:
            td = dict(
                idx = ticket.ticket_idx,
                ticket_type         = code_from_ticket_type[int(ticket.ticket_type)],
                event_name          = ticket.event_name,
                performance_name    = ticket.performance_name,
                ticket_template_id  = ticket.ticket_template_id,
                performance_datetime= ticket.performance_datetime,
                xml                 = SejTicketDataXml(ticket.ticket_data_xml)
            )
            tickets.append(td)

        f = SejOrderForm(self.request.POST, order_no=order.order_no)
        if f.validate():
            data = f.data
            try:
                request_update_order(
                    update_reason   = code_from_update_reason[int(data.get('update_reason'))],
                    total           = int(data.get('total_price')),
                    ticket_total    = int(data.get('ticket_price')),
                    commission_fee  = int(data.get('commission_fee')),
                    ticketing_fee   = int(data.get('altair.app.ticketing_fee')),
                    payment_type    = code_from_payment_type[int(order.payment_type)],
                    payment_due_at  = data.get('payment_due_at'),
                    ticketing_start_at = data.get('altair.app.ticketing_start_at'),
                    ticketing_due_at = data.get('altair.app.ticketing_due_at'),
                    regrant_number_due_at = data.get('regrant_number_due_at'),
                    tickets = tickets,
                    condition=dict(
                        order_no        = order.order_no,
                        billing_number  = order.billing_number,
                        exchange_number = order.exchange_number,
                    ),
                    shop_id=self.shop_id,
                    secret_key=self.secret_key,
                    hostname=self.sej_hostname
                )
                self.request.session.flash(u'オーダー情報を送信しました。')
            except SejServerError, e:
                self.request.session.flash(u'オーダー情報を送信に失敗しました。 %s' % e)
        else:
            logger.info(str(f.errors))
            self.request.session.flash(u'バリデーションエラー：更新出来ませんでした。')

        return HTTPFound(location=self.request.route_path('orders.sej.order.info', order_no=order_no))
    #
    @view_config(route_name='orders.sej.order.ticket.data', request_method="GET", renderer='json')
    def order_info_ticket_data(self):
        order_no = self.request.matchdict.get('order_no', '')
        ticket_id = int(self.request.matchdict.get('ticket_id', 0))
        order = SejOrder.query.filter_by(order_no=order_no).order_by(desc(SejOrder.branch_no)).first()
        if order:
            ticket = SejTicket.query.get(ticket_id)
            return dict(
                ticket_type = ticket.ticket_type,
                event_name = ticket.event_name,
                performance_name = ticket.performance_name,
                performance_datetime = ticket.performance_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                ticket_template_id = ticket.ticket_template_id,
                ticket_data_xml = ticket.ticket_data_xml,
            )
        return dict()

    @view_config(route_name='orders.sej.order.ticket.data', request_method="POST", renderer='altair.app.ticketing:templates/sej/order_info.html')
    def order_info_ticket_data_post(self):
        order_no = self.request.matchdict.get('order_no', '')
        ticket_id = int(self.request.matchdict.get('ticket_id', 0))
        order = SejOrder.query.filter_by(order_no=order_no).order_by(desc(SejOrder.branch_no)).first()
        if order:
            ticket = SejTicket.query.get(ticket_id)
            f = SejTicketForm(self.request.POST)
            if f.validate():
                data = f.data
                ticket.event_name = data.get('event_name')
                ticket.performance_name = data.get('performance_name')
                ticket.performance_datetime = data.get('performance_datetime')
                ticket.ticket_template_id = data.get('ticket_template_id')
                ticket.ticket_data_xml = data.get('ticket_data_xml')
                self.request.session.flash(u'チケット情報を更新しました。')
            else:
                self.request.session.flash(u'バリデーションエラー：更新出来ませんでした。')

        return HTTPFound(location=self.request.route_path('orders.sej.order.info', order_no=order_no))

    @view_config(route_name='orders.sej.order.cancel', renderer='altair.app.ticketing:templates/sej/order_info.html')
    def order_cancel(self):
        order_no = self.request.matchdict.get('order_no', '')
        sej_order = SejOrder.query.filter_by(order_no=order_no).order_by(desc(SejOrder.branch_no)).first()

        result = sej_api.cancel_sej_order(sej_order, self.request.context.organization.id)
        if result:
            self.request.session.flash(u'オーダーをキャンセルしました。')
            return HTTPFound(location=self.request.route_path('orders.sej.order.info', order_no=order_no))
        else:
            self.request.session.flash(u'オーダーをキャンセルに失敗しました。')
            raise HTTPFound(location=self.request.route_path('orders.sej.order.info', order_no=order_no))


@view_defaults(decorator=with_bootstrap, permission='administrator')
class SejRefundView(BaseView):

    @view_config(route_name='orders.sej.event.refund', renderer='altair.app.ticketing:templates/sej/event_refund.html')
    def order_event_refund(self):

        sort = self.request.GET.get('sort', 'SejRefundEvent.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = SejRefundEvent.filter().order_by(sort + ' ' + direction)

        events = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        f = SejRefundEventForm()
        return dict(
            form = f,
            events = events
        )

    @view_config(route_name='orders.sej.event.refund.detail', renderer='altair.app.ticketing:templates/sej/event_refund_detail.html')
    def order_event_detail(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = SejRefundEvent.query.get(event_id)
        return dict(event=event)

    @view_config(route_name='orders.sej.event.refund.add', renderer='altair.app.ticketing:templates/sej/event_form.html')
    def order_event_refund_add(self):
        f = SejRefundEventForm(self.request.POST)
        if f.validate():
            e = SejRefundEvent()
            d = f.data
            e.available = d.get('available')
            e.shop_id = d.get('shop_id')
            e.event_code_01 = d.get('event_code_01')
            e.event_code_02 = d.get('event_code_02')
            e.title = d.get('title')
            e.sub_title = d.get('sub_title')
            e.event_at = d.get('event_at')
            e.start_at = d.get('start_at')
            e.end_at = d.get('end_at')
            e.ticket_expire_at = d.get('ticket_expire_at')
            e.event_expire_at = d.get('event_expire_at')
            e.refund_enabled = d.get('refund_enabled')
            e.disapproval_reason = d.get('disapproval_reason')
            e.need_stub = d.get('need_stub')
            e.remarks = d.get('remarks')
            DBSession.add(e)
        else:
            return dict(
                form = f
            )

        return HTTPFound(location=self.request.route_path('orders.sej.event.refund'))

    @view_config(route_name='orders.sej.order.ticket.refund', request_method='POST', renderer='altair.app.ticketing:templates/sej/ticket_refund.html')
    def order_ticket_refund(self):

        ticket_id = int(self.request.matchdict.get('ticket_id', 0))
        ticket = SejTicket.query.get(ticket_id)

        f = SejRefundOrderForm(self.request.POST)
        if f.validate():
            data = f.data
            event = data.get('event')
            from sqlalchemy.orm.exc import NoResultFound
            try:
                ct = SejRefundTicket.filter(
                    and_(
                        SejRefundTicket.order_no == ticket.order_no,
                        SejRefundTicket.ticket_barcode_number == ticket.barcode_number
                    )).one()
            except NoResultFound, e:
                ct = SejRefundTicket()
                DBSession.add(ct)

            ct.available     = 1
            ct.event_code_01 = event.event_code_01
            ct.event_code_02 = event.event_code_02
            ct.order_no = ticket.order_no
            ct.ticket_barcode_number = ticket.barcode_number
            ct.refund_ticket_amount = data.get('refund_ticket_amount')
            ct.refund_other_amount = data.get('refund_other_amount')
            event.tickets.append(ct)
            DBSession.flush()

            self.request.session.flash(u'払い戻し予約を行いました。')
        else:
            self.request.session.flash(u'失敗しました')

        return HTTPFound(location=self.request.route_path('orders.sej.order.info', order_no=ticket.order.order_no))

# @TODO move this
@view_defaults(decorator=with_bootstrap, permission='administrator')
class SejTicketTemplate(BaseView):

    @view_config(route_name='orders.sej.ticket_template', renderer='altair.app.ticketing:templates/sej/ticket_template.html')
    def order_ticket_preview(self):

        sort = self.request.GET.get('sort', 'SejTicketTemplateFile.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'


        query = SejTicketTemplateFile.filter().order_by(sort + ' ' + direction)

        templates = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return dict(
            templates=templates
        )

@view_defaults(decorator=with_bootstrap, permission="authenticated", route_name="orders.mailinfo")
class MailInfoView(BaseView):
    @view_config(match_param="action=show", renderer="altair.app.ticketing:templates/orders/mailinfo/show.html")
    def show(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        mutil = get_mail_utility(self.request, MailTypeEnum.PurchaseCancelMail)
        message = mutil.build_message(self.request, order)
        mail_form = SendingMailForm(subject=message.subject,
                                    recipient=message.recipients[0] if message.recipients else "",
                                    bcc=message.bcc[0] if message.bcc else "")
        performance = order.performance
        return dict(order=order, mail_form=mail_form, performance=performance)

    @view_config(match_param="action=complete_mail_preview", renderer="string")
    def complete_mail_preview(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        mutil = get_mail_utility(self.request, MailTypeEnum.PurchaseCompleteMail)
        return mutil.preview_text(self.request, order)

    @view_config(match_param="action=complete_mail_send", renderer="string", request_method="POST")
    def complete_mail_send(self):
        form = SendingMailForm(self.request.POST)
        order_id = int(self.request.matchdict.get('order_id', 0))
        if not form.validate():
            self.request.session.flash(u'失敗しました: %s' % form.errors)
            raise HTTPFound(self.request.current_route_url(order_id=order_id, action="show"))

        order = Order.get(order_id, self.context.organization.id)
        mutil = get_mail_utility(self.request, MailTypeEnum.PurchaseCompleteMail)
        mutil.send_mail(self.request, order, override=form.data)
        self.request.session.flash(u'メール再送信しました')
        return HTTPFound(self.request.current_route_url(order_id=order_id, action="show"))

    @view_config(match_param="action=cancel_mail_preview", renderer="string")
    def cancel_mail_preview(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        mutil = get_mail_utility(self.request, MailTypeEnum.PurchaseCancelMail)
        return mutil.preview_text(self.request, order)

    @view_config(match_param="action=cancel_mail_send", renderer="string", request_method="POST")
    def cancel_mail_send(self):
        form = SendingMailForm(self.request.POST)
        order_id = int(self.request.matchdict.get('order_id', 0))
        if not form.validate():
            self.request.session.flash(u'失敗しました: %s' % form.errors)
            raise HTTPFound(self.request.current_route_url(order_id=order_id, action="show"))

        order = Order.get(order_id, self.context.organization.id)
        mutil = get_mail_utility(self.request, MailTypeEnum.PurchaseCancelMail)
        mutil.send_mail(self.request, order, override=form.data)
        self.request.session.flash(u'メール再送信しました')
        return HTTPFound(self.request.current_route_url(order_id=order_id, action="show"))


@view_defaults(decorator=with_bootstrap, permission='sales_editor')
class CartView(BaseView):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='cart.search', renderer="altair.app.ticketing:templates/carts/index.html")
    def index(self):
        slave_session = get_db_session(self.request, name="slave")

        form = CartSearchForm(self.request.params, organization_id=self.context.organization.id)
        carts = []
        organization_id = self.context.organization.id
        if not self.request.params:
            self.request.session.flash(u'検索条件を指定してください')
        elif not form.validate():
            self.request.session.flash(u'検索条件に誤りがあります')
        else:
            try:
                query = slave_session.query(Cart).filter(Cart.organization_id == organization_id).filter(Cart.deleted_at == None)
                query = CartSearchQueryBuilder(form.data)(query)
            except QueryBuilderError as e:
                self.request.session.flash(e.message)
            page = int(self.request.params.get('page', 0))
            carts = paginate.Page(
                query,
                page=page,
                items_per_page=40,
                item_count=query.count(),
                url=paginate.PageURL_WebOb(self.request)
            )

        return { 'form_search': form, 'carts': carts, 'url': self.request.path }

