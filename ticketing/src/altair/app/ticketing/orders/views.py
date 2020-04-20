# -*- coding: utf-8 -*-

import sys
import json
import logging
import csv
import itertools
import re
from collections import OrderedDict
from datetime import datetime, timedelta
from .api import get_pgw_info

from altair.app.ticketing.checkout.models import Checkout
from altair.app.ticketing.discount_code.forms import DiscountCodeTargetStForm
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest, HTTPInternalServerError
from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.decorator import reify
from pyramid.url import route_path
from pyramid.compat import escape
from paste.util.multidict import MultiDict
import webhelpers.paginate as paginate
from wtforms import ValidationError
from wtforms.validators import Optional
from sqlalchemy import and_, func
from sqlalchemy.sql import exists
from sqlalchemy.sql.expression import or_, desc, func
from sqlalchemy.orm import joinedload, undefer
from sqlalchemy.orm.session import make_transient
from webob.multidict import MultiDict
import transaction

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from .reservation import ReservationReportOperator

from altair.sqlahelper import get_db_session
import  altair.viewhelpers.datetime_
from altair.app.ticketing.tickets.api import get_svg_builder
from altair.app.ticketing.models import DBSession, merge_session_with_post, record_to_multidict, asc_or_desc
from altair.app.ticketing.core.models import (
    OrganizationSetting,
    Performance,
    PaymentDeliveryMethodPair,
    ShippingAddress,
    Product,
    ProductItem,
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
    Refund,
    RefundStatusEnum,
    Event,
    OrionTicketPhone,
    PointUseTypeEnum,
    Refund_Performance)
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.core import helpers as core_helpers
from altair.app.ticketing.orders.models import (
    Order,
    OrderedProduct,
    OrderedProductItem,
    OrderedProductItemToken,
    OrderedProductAttribute,
    ProtoOrder,
    DownloadItemsPattern,
    RefundPointEntry,
    )
from altair.app.ticketing.lots.models import LotEntry, LotElectedEntry
from altair.app.ticketing.sej import api as sej_api
from altair.app.ticketing.mails.api import get_mail_utility
from altair.app.ticketing.mailmags.models import MailSubscription, MailMagazine, MailSubscriptionStatus
from altair.app.ticketing.orders.export import OrderCSV, OrderOptionalCSV, get_japanese_columns, get_ordered_ja_col, RefundResultCSVExporter, get_ordered_ja_col
from .forms import (
    OrderForm,
    OrderInfoForm,
    OrderSearchForm,
    OrderRefundSearchForm,
    SejRefundEventForm,
    SejRefundOrderForm,
    SendingMailForm,
    PerformanceSearchForm,
    OrderReserveForm,
    OrderRefundForm,
    ClientOptionalForm,
    SalesSegmentGroupSearchForm,
    TicketFormatSelectionForm,
    CartSearchForm,
    DeliverdEditForm,
    SejOrderCancelForm,
    FamiPortOrderCancelForm,
    DownloadItemsPatternForm,
    OrderRefundIndexSearchForm)
from altair.app.ticketing.orders.forms import OrderMemoEditFormFactory
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.orders.events import notify_order_canceled
from altair.app.ticketing.payments.payment import Payment
from altair.app.ticketing.payments.api import get_payment_plugin, lookup_plugin, get_delivery_plugin, validate_order_like
from altair.app.ticketing.payments.exceptions import OrderLikeValidationFailure, SilentOrderLikeValidationFailure
from altair.app.ticketing.payments import plugins as payments_plugins
from altair.app.ticketing.payments.plugins.sej import SejDeliveryPlugin, SejPaymentDeliveryPlugin
from altair.app.ticketing.tickets.utils import build_dicts_from_ordered_product_item
from altair.app.ticketing.cart import api
from altair.app.ticketing.cart.models import Cart
from altair.app.ticketing.cart.stocker import NotEnoughStockException
from altair.app.ticketing.cart.reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from altair.app.ticketing.cart.exceptions import NoCartError
from altair.app.ticketing.loyalty import api as loyalty_api
from altair.app.ticketing.qr.utils import build_qr_by_token, build_qr_by_order
from altair.app.ticketing.carturl.api import get_orderreview_qr_url_builder, get_orderreview_skidata_qr_url_builder
from altair.app.ticketing.skidata.api import send_whitelist_if_necessary

from . import utils
from altair.multicheckout.api import get_multicheckout_3d_api
from altair.multicheckout.util import (
    get_multicheckout_error_message,
    get_multicheckout_card_error_message,
    get_multicheckout_status_description,
    )

from .api import (
    CartSearchQueryBuilder,
    OrderSummarySearchQueryBuilder,
    QueryBuilderError,
    create_inner_order,
    save_order_modification,
    save_order_modifications_from_proto_orders,
    recalculate_total_amount_for_order,
    get_order_by_order_no,
    get_order_by_id,
    refresh_order,
    OrderAttributeIO,
    get_payment_delivery_plugin_info,
    get_patterns_info
)

from .exceptions import (
    OrderCreationError,
    MassOrderCreationError,
    InnerCartSessionException,
    MassOrderModificationError,
)
from .utils import NumberIssuer
from .models import OrderSummary
from .helpers import build_candidate_id
from .mail import send_refund_reserve_mail
from altair.app.ticketing.tickets.preview.api import SVGPreviewCommunication
from altair.app.ticketing.tickets.preview.api import get_placeholders_from_ticket
from altair.app.ticketing.tickets.preview.transform import SVGTransformer
from altair.app.ticketing.tickets.utils import build_cover_dict_from_order
from altair.app.ticketing.core.models import TicketCover

from altair.app.ticketing.payments.plugins import ORION_DELIVERY_PLUGIN_ID, CHECKOUT_PAYMENT_PLUGIN_ID

## ハウステンボス専用のQRコードユーティリティ
#from altair.app.ticketing.project_specific.huistenbosch.qr_utilits import build_ht_qr_by_token
from altair.app.ticketing.qr.lookup import lookup_qr_aes_plugin

from altair.app.ticketing.famiport.exc import (
    FamiportPaymentDateNoneError,
    FamiPortTicketingDateNoneError,
    FamiPortAlreadyPaidError
)

from altair.app.ticketing.pgw import api as pgw_api
from altair.app.ticketing.pgw.models import PGWResponseLog


# 当日窓口発券モードで発券を許可する引取方法プラグイン
INNER_DELIVERY_PLUGIN_IDS = [
    payments_plugins.SHIPPING_DELIVERY_PLUGIN_ID,
    payments_plugins.RESERVE_NUMBER_DELIVERY_PLUGIN_ID,
    payments_plugins.SKIDATA_QR_DELIVERY_PLUGIN_ID,
]

logger = logging.getLogger(__name__)

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
            query = asc_or_desc(query, Performance.start_on, 'asc')

        performances = [] if formdata.get('performance_opt_all_disable') else [dict(pk='', name=u'(すべて)')]
        performances = performances + [dict(pk=p.id, name='%s (%s)' % (
                p.name, altair.viewhelpers.datetime_.dt2str(p.start_on, self.request, with_weekday=True)))
            for p in query]
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

        sales_segment_groups = [dict(pk=p.id, name=p.name) for p in query]
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


class OrderBaseView(BaseView):
    @reify
    def endpoints(self):
        return {
            'enqueue_orders': self.request.route_path('orders.checked.queue'),
            }



@view_defaults(decorator=with_bootstrap, renderer='altair.app.ticketing:templates/orders/index.html', permission='order_viewer')
class OrderIndexView(OrderBaseView):

    @view_config(route_name='orders.index')
    def index(self):
        request = self.request
        slave_session = get_db_session(request, name="slave")

        organization_id = request.context.organization.id
        params = MultiDict(request.params)
        params["order_no"] = " ".join(request.params.getall("order_no"))

        form_search = OrderSearchForm(params, organization_id=organization_id)

        orders = None
        page = int(request.params.get('page', 0))
        if request.params:
            from .download import OrderSummary, OrderProductItemSummary
            if form_search.validate():
                query = OrderSummary(self.request,
                                    slave_session,
                                    organization_id,
                                    condition=form_search)
            else:
                return {
                    'form':OrderForm(context=self.context),
                    'form_search':form_search,
                    'orders':orders,
                    'page': page,
                    'endpoints': self.endpoints,
                    }

            if request.params.get('action') == 'checked':
                checked_orders = [o.lstrip('o:')
                                  for o in request.session.get('orders', [])
                                  if o.startswith('o:')]
                query.target_order_ids = checked_orders

            count = query.count()

            orders = paginate.Page(
                query,
                page=page,
                item_count=count,
                items_per_page=40,
                url=paginate.PageURL_WebOb(request)
            )

        return {
            'form':OrderForm(context=self.context),
            'form_search':form_search,
            'orders':orders,
            'page': page,
            'endpoints': self.endpoints,
            }

    @view_config(route_name='orders.show_total_amount', renderer='json')
    def show_total_amount(self):
        from .download import OrderSummary
        request = self.request
        slave_session = get_db_session(request, name="slave")
        organization_id = request.context.organization.id
        form_search = OrderSearchForm(MultiDict(request.params), organization_id=organization_id)
        total_amount = None
        if form_search.validate():
            query = OrderSummary(self.request,
                                slave_session,
                                organization_id,
                                condition=form_search)
            total_amount = query.total_amount()[0]
        return {
            'total_amount': total_amount
        }

    @view_config(route_name='orders.show_total_quantity', renderer='json')
    def show_total_quantity(self):
        from .download import OrderProductItemSummary
        request = self.request
        slave_session = get_db_session(request, name="slave")
        organization_id = request.context.organization.id
        form_search = OrderSearchForm(MultiDict(request.params), organization_id=organization_id)
        total_quantity = None
        if form_search.validate():
            query_ordered_product_item = OrderProductItemSummary(self.request,
                                        slave_session,
                                        organization_id,
                                        condition=form_search)
            total_quantity = query_ordered_product_item.total_quantity()[0]
        return {
            'total_quantity': total_quantity
        }


@view_defaults(decorator=with_bootstrap, permission='sales_editor') # sales_counter ではない!
class OrderReportDownloadView(OrderBaseView):

    @view_config(route_name='orders.report_download')
    def report_download(self):
        """
        予約管理者のレポートダウンロード
        Operator_name_201701_00001.xls
        通番は5桁とし、Orderの件数とする
        """
        operator = ReservationReportOperator(self.request, self.context.order, self.context.user)
        return operator.create_report_response()

@view_defaults(decorator=with_bootstrap, permission='sales_editor') # sales_counter ではない!
class OrderDownloadView(OrderBaseView):
    # downloadに関しては古いコードがイキ
    @view_config(route_name='orders.download')
    def download_old(self):
        slave_session = get_db_session(self.request, name="slave")

        organization_id = self.context.organization.id
        query = slave_session.query(OrderSummary).filter(OrderSummary.organization_id==organization_id, OrderSummary.deleted_at==None)

        if self.request.params.get('action') == 'checked':
            checked_orders = [o.lstrip('o:') for o in self.request.session.get('orders', []) if o.startswith('o:')]
            if len(checked_orders) > 0:
                query = query.filter(Order.id.in_(checked_orders))
            else:
                raise HTTPFound(location=route_path('orders.optional', self.request))
        else:
            form_search = OrderSearchForm(self.request.params, organization_id=organization_id)
            form_search.sort.data = None
            try:
                builder = OrderSummarySearchQueryBuilder(form_search.data, lambda key: form_search[key].label.text, sort=False)
                query = builder(slave_session.query(OrderSummary).filter(OrderSummary.organization_id==organization_id, OrderSummary.deleted_at==None))
            except QueryBuilderError as e:
                self.request.session.flash(e.message)
                raise HTTPFound(location=route_path('orders.optional', self.request))
            ordered_term = None
            if form_search.ordered_from.data and form_search.ordered_to.data:
                ordered_term = form_search.ordered_to.data - form_search.ordered_from.data
            if not form_search.performance_id.data and (ordered_term is None or ordered_term.days > 0):
                if query.count() >= 100000:
                    self.request.session.flash(u'対象件数が多すぎます。(予約期間を1日にするか、公演を指定すれば制限はありません)')
                    raise HTTPFound(location=route_path('orders.optional', self.request))

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
        #    )

        query._request = self.request # XXX
        orders = query

        headers = [
            ('Content-Type', 'application/octet-stream; charset=Windows-31J'),
            ('Content-Disposition', 'attachment; filename=orders_{date}.csv'.format(date=datetime.now().strftime('%Y%m%d%H%M%S')))
        ]
        response = Response(headers=headers)

        export_type = int(self.request.params.get('export_type', OrderCSV.EXPORT_TYPE_ORDER))
        excel_csv = bool(self.request.params.get('excel_csv'))
        kwargs = {
            # 通常のダウンロードは発券開始日時と期限を表示しません
            'empty_columns': ['order.issuing_start_at', 'order.issuing_end_at']
        }
        if export_type:
            kwargs['export_type'] = export_type
        if excel_csv:
            kwargs['excel_csv'] = True
        order_csv = OrderCSV(self.request,
                             organization_id=self.context.organization.id,
                             localized_columns=get_japanese_columns(self.request),
                             session=slave_session, **kwargs)
        def _orders(orders):
            prev_order = None
            for order in orders:
                if prev_order is not None:
                    make_transient(prev_order)
                prev_order = order
                yield order

        def writer_factory(f):
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
            def writerow(columns):
                writer.writerow([encode_to_cp932(column) for column in columns])
            return writerow

        response.app_iter = order_csv(_orders(orders), writer_factory)
        return response

    # 新しいコードも参照用にとっておいてある
    def download_new(self):
        request = self.request
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
            query = query_type(self.request,
                               slave_session,
                               organization_id,
                               condition=form_search)
        else:
            query = OrderDownload(self.request,
                                  slave_session,
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
                "created_from_lot_entry",
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
                "created_from_lot_entry",  # 抽選
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
        iheaders = header_intl(csv_headers, japanese_columns)
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


@view_defaults(decorator=with_bootstrap, renderer='altair.app.ticketing:templates/orders/optional_index.html', permission='order_viewer')
class OrderOptionalIndexView(OrderBaseView):
    @view_config(route_name='orders.optional', request_method="GET")
    @view_config(route_name='orders.optional', request_method="POST")
    def post(self):
        request = self.request
        patterns = get_patterns_info(request)
        slave_session = get_db_session(request, name="slave")
        organization_id = request.context.organization.id

        params = MultiDict(request.POST)
        params["order_no"] = " ".join(request.POST.getall("order_no"))
        if request.method == "GET":
            event_id = request.params['event_id'] if "event_id" in request.params else None
            if event_id:
                form_search = OrderSearchForm(params, organization_id=organization_id, event_id=event_id)
            else:
                form_search = OrderSearchForm(params, organization_id=organization_id)
                return {
                    'form_search': form_search,
                    'endpoints': self.endpoints,
                    'patterns': patterns
                }
        else:
            form_search = OrderSearchForm(params, organization_id=organization_id)
        orders = None
        page = int(request.GET.get('page', 0))

        from .download import OrderSummary
        if form_search.validate():
            query = OrderSummary(self.request,
                                 slave_session,
                                 organization_id,
                                 condition=form_search)
        else:
            return {
                'form': OrderForm(context=self.context),
                'form_search': form_search,
                'orders': orders,
                'page': page,
                'endpoints': self.endpoints,
                'patterns': patterns
            }

        if request.params.get('action') == 'checked':
            checked_orders = [o.lstrip('o:') for o in request.session.get('orders', []) if o.startswith('o:')]
            query.target_order_ids = checked_orders

        if request.params.get('action') in ['remind_mail', 'reserved_number', 'delivery_order', 'stop_point_grant']:
            ords = self.request.session.get("orders", [])
            ords = [o.lstrip("o:") for o in ords if o.startswith("o:")]
            qs = Order.query.filter(Order.organization_id == self.context.organization.id) \
                .filter(Order.id.in_(ords))
            exist_order_ids = set()
            remind_mail_fail_nos = []
            delivery_order_fail_nos = []
            reserved_number_fail_nos = []
            stop_point_grant_fail_nos = []

            # 一括配送済み
            if request.params.get('action') == 'delivery_order':
                for order in qs:
                    exist_order_ids.add(str(order.id))
                    no = order.order_no
                    status = order.delivered()
                    if not status:
                        delivery_order_fail_nos.append(no)

            # 一括リマインドメールメール送信済み
            if request.params.get('action') == 'remind_mail':
                for order in qs:
                    exist_order_ids.add(str(order.id))
                    no = order.order_no
                    if order.payment_status in ["refunding", "refunded"] or order.is_canceled():
                        # 払い戻し予約、払い戻し、キャンセルの場合エラー
                        remind_mail_fail_nos.append(no)
                    else:
                        if order.payment_status not in ["paid"] or not order.order_notification.payment_remind_at:
                            order.order_notification.payment_remind_at = datetime.now()
                        if not order.is_issued() or not order.order_notification.print_remind_at:
                            order.order_notification.print_remind_at = datetime.now()

            # 一括窓口入金
            if request.params.get('action') == 'reserved_number':
                for order in qs:
                    exist_order_ids.add(str(order.id))
                    no = order.order_no
                    if not order.change_payment_status("paid"):
                        reserved_number_fail_nos.append(no)

            # 一括ポイント付与停止(TKT-9767)
            if request.params.get('action') == 'stop_point_grant':
                for order in qs:
                    exist_order_ids.add(str(order.id))
                    no = order.order_no
                    if order.refund_id and order.is_refunded and order.is_canceled():
                        stop_point_grant_fail_nos.append(no)
                    else:
                        order.manual_point_grant = True

            request_ids = set(ords)
            lost_order_ids = request_ids - exist_order_ids

            if delivery_order_fail_nos:
                nos_str = ', '.join(delivery_order_fail_nos)
                self.request.session.flash(u'配送済みに変更できない注文が含まれていました。')
                self.request.session.flash(u'({0})'.format(nos_str))

            if remind_mail_fail_nos:
                nos_str = ', '.join(remind_mail_fail_nos)
                self.request.session.flash(u'リマインドメール送信済みに変更できない注文が含まれていました。')
                self.request.session.flash(u'({0})'.format(nos_str))

            if reserved_number_fail_nos:
                nos_str = ', '.join(reserved_number_fail_nos)
                self.request.session.flash(u'窓口支払を入金済みに変更できない注文が含まれていました。')
                self.request.session.flash(u'({0})'.format(nos_str))

            if stop_point_grant_fail_nos:
                nos_str = ', '.join(stop_point_grant_fail_nos)
                self.request.session.flash(u'ポイント付与停止できない注文が含まれていました。')
                self.request.session.flash(u'({0})'.format(nos_str))

            if lost_order_ids:
                ids_str = ', '.join(map(repr, lost_order_ids))
                self.request.session.flash(u'存在しない注文が含まれていました。')
                self.request.session.flash(u'({0})'.format(ids_str))

        count = query.count()
        orders = paginate.Page(
            query,
            page=page,
            item_count=count,
            items_per_page=40,
            url=paginate.PageURL_WebOb(request)
        )

        return {
            'form': OrderForm(context=self.context),
            'form_search': form_search,
            'orders': orders,
            'page': page,
            'endpoints': self.endpoints,
            'patterns': patterns
        }

@view_defaults(decorator=with_bootstrap, permission='sales_editor')
class OrderOptionalDownloadView(OrderBaseView):
    @view_config(route_name='orders.optional.download')
    def download(self):
        slave_session = get_db_session(self.request, name="slave")

        organization_id = self.context.organization.id
        query = slave_session.query(OrderSummary).filter(OrderSummary.organization_id==organization_id, OrderSummary.deleted_at==None)

        if self.request.params.get('action') == 'checked':
            checked_orders = [o.lstrip('o:') for o in self.request.session.get('orders', []) if o.startswith('o:')]
            if len(checked_orders) > 0:
                query = query.filter(Order.id.in_(checked_orders))
            else:
                raise HTTPFound(location=route_path('orders.optional', self.request))
        else:
            form_search = OrderSearchForm(self.request.params, organization_id=organization_id)
            form_search.sort.data = None
            try:
                builder = OrderSummarySearchQueryBuilder(form_search.data, lambda key: form_search[key].label.text,
                                                         sort=False)
                query = builder(
                    slave_session.query(OrderSummary).filter(OrderSummary.organization_id == organization_id,
                                                             OrderSummary.deleted_at == None))
            except QueryBuilderError as e:
                self.request.session.flash(e.message)
                raise HTTPFound(location=route_path('orders.optional', self.request))
            ordered_term = None
            if form_search.ordered_from.data and form_search.ordered_to.data:
                ordered_term = form_search.ordered_to.data - form_search.ordered_from.data
            if not form_search.performance_id.data and (ordered_term is None or ordered_term.days > 0):
                if query.count() >= 100000:
                    self.request.session.flash(u'対象件数が多すぎます。(予約期間を1日にするか、公演を指定すれば制限はありません)')
                    raise HTTPFound(location=route_path('orders.optional', self.request))

        query._request = self.request
        orders = query

        headers = [('Content-Type', 'application/octet-stream; charset=Windows-31J'),
                   ('Content-Disposition', 'attachment; filename=orders_{org_id}_{date}.csv'.format(org_id=organization_id,date=datetime.now().strftime('%Y%m%d%H%M%S')))]
        response = Response(headers=headers)

        export_type = int(self.request.params.get('export_type', OrderCSV.EXPORT_TYPE_ORDER))
        excel_csv = bool(self.request.params.get('excel_csv'))
        kwargs = {}
        if export_type:
            kwargs['export_type'] = export_type
        if excel_csv:
            kwargs['excel_csv'] = True
        option_columns = self.request.params.getall('download-option')

        order_csv = OrderOptionalCSV(self.request,
                                  organization_id=self.context.organization.id,
                                  localized_columns=get_ordered_ja_col(),
                                  session=slave_session,
                                  option_columns=option_columns,
                                  **kwargs)
        def _orders(orders):
            prev_order = None
            for order in orders:
                if prev_order is not None:
                    make_transient(prev_order)
                prev_order = order
                yield order

        def writer_factory(f):
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
            def writerow(columns):
                writer.writerow([encode_to_cp932(column) for column in columns])
            return writerow

        response.app_iter = order_csv(_orders(orders), writer_factory)
        return response

@view_defaults(decorator=with_bootstrap, renderer='altair.app.ticketing:templates/orders/optional_download_pattern.html', permission='order_viewer')
class OrderOptionalDownloadPatternView(BaseView):
    @view_config(route_name='orders.optional.pattern', request_method="GET")
    def index(self):
        japanese_columns = get_ordered_ja_col()
        patterns = get_patterns_info(self.request)

        return {
            'patterns': patterns,
            'japanese_columns': japanese_columns
        }

    def submit_validate(self, pattern_name, pattern_content, op_type):
        emsgs = []

        if not op_type or op_type not in ['add', 'update', 'del']:
            emsgs.append(u"操作タイプは認知できないため、テンプレートに関する操作はできません。")
            return emsgs

        ope = {'add': u'新規登録', 'update': u'更新', 'del': u'削除'}
        if not pattern_name:
            emsgs.append(u"{}するテンプレート名を記入ください。".format(ope[op_type]))

        if op_type in ['add', 'update'] and not pattern_content:
            emsgs.append(u"ダウンロード項目を選んでください。")

        return emsgs

    def create_or_update(self, form, pattern_object):
        emsgs = []
        if form.validate():
            form.populate_obj(pattern_object)

            try:
                pattern_object.save()
            except Exception, e:
                emsgs.append(str(e))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    emsgs.append(u"{0}: {1}".format(field, error))
        return emsgs

    @view_config(route_name='orders.optional.pattern.operate', request_method="POST", renderer="json")
    def operate(self):
        organization_id = self.context.organization.id
        pattern_name = escape(self.request.POST.get('pattern_name', None))
        pattern_content = self.request.POST.get('pattern_content', None)
        op_type = self.request.POST.get('op_type', None)

        emsgs = self.submit_validate(pattern_name, pattern_content, op_type)
        if emsgs:
            raise HTTPBadRequest(body=json.dumps({'emsgs': emsgs}))

        pattern_form = DownloadItemsPatternForm(self.request.POST)
        pattern_form.organization_id.data = organization_id

        pattern = DownloadItemsPattern.query.filter_by(organization_id=organization_id,
                                                       pattern_name=pattern_name)

        context = {}
        if op_type == 'add':
            if pattern.first():
                emsgs.append(u"保存したいパターン名はすでに存在していますので、別のパターン名を設定か「上書き保存」ボタンで保存してください。")
            else:
                pattern = DownloadItemsPattern()
                emsgs = self.create_or_update(pattern_form, pattern)

            if not emsgs:
                context = {pattern.pattern_name: filter(None, pattern.pattern_content.split(','))}

        elif op_type == 'update':
            pattern = pattern.first()
            emsgs = self.create_or_update(pattern_form, pattern)
            if not emsgs:
                context = {pattern.pattern_name: filter(None, pattern.pattern_content.split(','))}

        elif op_type == 'del':
            try:
                pattern.delete()
                context = {"pattern_name": pattern_name}
            except Exception, e:
                emsgs.append(str(e))
        else:
            emsgs.append(u"操作タイプを確定できないため、ダウンロードパターンに関する操作はできません。")


        if emsgs:
            raise HTTPBadRequest(body=json.dumps({'emsgs': emsgs}))
        else:
            return context



@view_defaults(decorator=with_bootstrap, permission='event_editor', renderer='altair.app.ticketing:templates/orders/refund/index.html')
class OrdersRefundIndexView(OrderBaseView):

    @view_config(route_name='orders.refund.index', request_method='GET')
    @view_config(route_name='orders.refund.index', request_method='POST')
    def index(self):
        organization_id = self.context.organization.id
        condition = MultiDict(self.request.params)
        if self.request.method == 'GET':
            status = self.request.params.get('status', None)
            if status == 'init':
                self.request.session['ticketing.refund.condition'] = []
            else:
                condition = MultiDict(self.request.session.get('ticketing.refund.condition', []))
        if self.request.method == 'POST':
            self.request.session['ticketing.refund.condition'] = self.request.params.items()
        search_form = OrderRefundIndexSearchForm(condition, organization_id=organization_id)
        query = Refund.query.filter(Refund.organization_id == organization_id
                                    ).options(undefer(Refund.updated_at),
                                              joinedload(Refund.payment_method),
                                              joinedload(Refund.performances)
                                              ).join(Refund_Performance).join(Performance).join(Event)
        if search_form.event_code.data is not None and search_form.event_code.data is not u'':
            query = query.filter(Event.code.in_(search_form.event_code.data.split(' ')))
        if search_form.performance_code.data is not None and search_form.performance_code.data is not u'':
            query = query.filter(Performance.code.in_(search_form.performance_code.data.split(' ')))
        if search_form.event_id.data is not None and search_form.event_id.data is not u'':
            query = query.filter(Event.id == search_form.event_id.data)
        if search_form.performance_id.data is not None and search_form.performance_id.data is not u'':
            query = query.filter(Performance.id == search_form.performance_id.data)
        if search_form.start_on_from.data is not None and search_form.start_on_from.data is not u'':
            query = query.filter(Performance.start_on >= search_form.start_on_from.data)
        if search_form.start_on_to.data is not None and search_form.start_on_to.data is not u'':
            query = query.filter(Performance.start_on <= search_form.start_on_to.data)
        query = query.order_by(desc(Refund.id))
        page = int(self.request.params.get('page', 0))
        refunds = paginate.Page(
            query,
            page=page,
            items_per_page=40,
            item_count=query.count(),
            url=paginate.PageURL_WebOb(self.request)
        )
        return dict(
            form=OrderRefundForm(context=self.context),
            search_form=search_form,
            refunds=refunds,
            page=page,
            core_helpers=core_helpers
            )

    @view_config(route_name='orders.refund.delete')
    def delete(self):
        refund_id = int(self.request.matchdict.get('refund_id', 0))
        refund = Refund.get(refund_id, organization_id=self.context.organization.id)
        if refund is None:
            return HTTPNotFound("")

        try:
            refund.delete()
            self.request.session.flash(u'払戻予約を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=self.request.route_path('orders.refund.index'))

        return HTTPFound(location=self.request.route_path('orders.refund.index'))


@view_defaults(decorator=with_bootstrap, permission='event_editor', renderer='altair.app.ticketing:templates/orders/refund/edit.html')
class OrdersRefundEditView(OrderBaseView):

    @view_config(route_name='orders.refund.edit', request_method='GET')
    def edit_get(self):
        refund_id = int(self.request.matchdict.get('refund_id', 0))
        refund = Refund.get(refund_id, organization_id=self.context.organization.id)
        if refund is None:
            return HTTPNotFound()

        f = OrderRefundForm(obj=refund, context=self.context)
        return dict(form=f, refund=refund)

    @view_config(route_name='orders.refund.edit', request_method='POST')
    def edit_post(self):
        refund_id = int(self.request.matchdict.get('refund_id', 0))
        refund = Refund.get(refund_id, organization_id=self.context.organization.id)
        if refund is None:
            return HTTPNotFound()

        f = OrderRefundForm(
                self.request.POST,
                orders=refund.orders,
                context=self.context
                )
        if f.validate():
            refund = merge_session_with_post(refund, f.data)
            refund.save()
            self.request.session.flash(u'払戻予約を保存しました')
            return HTTPFound(location=self.request.route_path('orders.refund.index', refund_id=refund.id))
        else:
            return dict(form=f, refund=refund)


@view_defaults(decorator=with_bootstrap, permission='event_editor', renderer='altair.app.ticketing:templates/orders/refund/show.html')
class OrdersRefundDetailView(OrderBaseView):

    @view_config(route_name='orders.refund.show')
    def index(self):
        refund_id = int(self.request.matchdict.get('refund_id', 0))
        refund = Refund.get(refund_id, organization_id=self.context.organization.id)
        if refund is None:
            return HTTPNotFound()

        form = OrderRefundForm(context=self.context)
        return dict(
            form=form,
            refund=refund,
            core_helpers=core_helpers
            )


@view_defaults(decorator=with_bootstrap, permission='event_editor', renderer='csv')
class OrdersRefundExportView(OrderBaseView):

    @view_config(route_name='orders.refund.export_result')
    def export_result(self):
        refund_id = long(self.request.matchdict.get('refund_id', 0))
        refund = Refund.get(refund_id, organization_id=self.context.organization.id)
        if refund is None:
            return HTTPNotFound()

        slave_session = get_db_session(self.request, name='slave')
        refund_tickets = RefundResultCSVExporter(slave_session, refund).all()
        if len(refund_tickets) == 0:
            self.request.session.flash(u'コンビニ払戻実績がありません')
            return HTTPFound(location=route_path('orders.refund.show', self.request, refund_id=refund_id))

        filename='refund_result-{}.csv'.format(refund_id)
        self.request.response.content_type = 'text/plain;charset=Shift_JIS'
        self.request.response.content_disposition = 'attachment; filename=' + filename
        return dict(data=list(refund_tickets), encoding='sjis', filename=filename)


@view_defaults(decorator=with_bootstrap, permission='event_editor', renderer='altair.app.ticketing:templates/orders/refund/new.html')
class OrdersRefundCreateView(OrderBaseView):

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.organization_id = int(self.context.organization.id)

    @view_config(route_name='orders.refund.new')
    def new(self):
        if self.request.session.get('orders'):
            del self.request.session['orders']
        if self.request.session.get('ticketing.refund.condition'):
            del self.request.session['ticketing.refund.condition']

        form_search = OrderRefundSearchForm(organization_id=self.organization_id)
        form_search.status.data = list(form_search.status.data or ()) + ['delivered']
        page = 0
        orders = []

        return {
            'form':OrderForm(context=self.context),
            'form_search':form_search,
            'page': page,
            'orders':orders,
        }

    @view_config(route_name='orders.refund.search')
    def search(self):
        slave_session = get_db_session(self.request, name="slave")
        if self.request.method == 'POST':
            refund_condition = MultiDict(self.request.params)
        else:
            refund_condition = MultiDict(self.request.session.get('ticketing.refund.condition', []))
        refund_condition["order_no"] = " ".join(self.request.POST.getall("order_no"))
        form_search = OrderRefundSearchForm(refund_condition, organization_id=self.organization_id)
        if form_search.validate():
            try:
                builder = OrderSummarySearchQueryBuilder(form_search.data, lambda key: form_search[key].label.text)
                query = builder(slave_session.query(OrderSummary).filter(OrderSummary.organization_id==self.organization_id, OrderSummary.deleted_at==None))
                query._request = self.request # XXX
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
                items_per_page=100,
                item_count=query.count(),
                url=paginate.PageURL_WebOb(self.request)
            )
        else:
            page = 0
            orders = []

        return {
            'form':OrderForm(context=self.context),
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
                builder = OrderSummarySearchQueryBuilder(form_search.data, lambda key: form_search[key].label.text)
                query = builder(slave_session.query(OrderSummary).filter(OrderSummary.organization_id==self.organization_id, OrderSummary.deleted_at==None))
            except QueryBuilderError as e:
                self.request.session.flash(e.message)

            checked_orders = [o.lstrip('o:') for o in self.request.session.get('orders', []) if o.startswith('o:')]
            query = query.filter(Order.id.in_(checked_orders))
            query._request = self.request # XXX

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
            'form':OrderForm(context=self.context),
            'form_search':form_search,
            'page': page,
            'orders':orders,
        }


@view_defaults(decorator=with_bootstrap, permission='event_editor', route_name='orders.refund.settings', renderer='altair.app.ticketing:templates/orders/refund/settings.html')
class OrdersRefundSettingsView(OrderBaseView):
    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.checked_orders = [o.lstrip('o:') for o in self.request.session.get('orders', []) if o.startswith('o:')]
        self.refund_condition = MultiDict(self.request.session.get('ticketing.refund.condition', []))
        self.organization_id = int(self.context.organization.id)
        self.form_search = OrderRefundSearchForm(self.refund_condition, organization_id=self.organization_id)

    @view_config(request_method='GET')
    def get(self):
        if not self.checked_orders:
            self.request.session.flash(u'払戻対象を選択してください')
            return HTTPFound(location=self.request.route_path('orders.refund.checked'))

        data = self.request.session.get('ticketing.refund.settings')
        if data is None:
            data = {}
            if self.form_search.payment_method.data:
                data['payment_method_id'] = self.form_search.payment_method.data
        form_refund = OrderRefundForm(_data=data, context=self.context)

        return {
            'orders':self.checked_orders,
            'refund_condition':self.refund_condition,
            'form_search':self.form_search,
            'form_refund':form_refund,
            }

    @view_config(request_method='POST')
    def post(self):
        if not self.checked_orders:
            self.request.session.flash(u'払戻対象を選択してください')
            return HTTPFound(location=route_path('orders.refund.checked', self.request))

        orders = Order.query.filter(Order.id.in_(self.checked_orders)).all()
        form_refund = OrderRefundForm(
            self.request.POST,
            context=self.context,
            orders=orders
        )
        if not form_refund.validate():
            return {
                'orders':self.checked_orders,
                'refund_condition':self.refund_condition,
                'form_search':self.form_search,
                'form_refund':form_refund,
                }

        errors = OrderedDict()
        # 未発券のコンビニ払戻を警告
        from altair.app.ticketing.core.models import PaymentMethod
        refund_pm = PaymentMethod.query.filter_by(id=form_refund.payment_method_id.data).one()
        if refund_pm.payment_plugin_id in [payments_plugins.SEJ_PAYMENT_PLUGIN_ID,payments_plugins.FAMIPORT_PAYMENT_PLUGIN_ID]:
            for order in orders:
                if not order.is_issued() and order.point_use_type is not PointUseTypeEnum.AllUse:
                    # TKT-6643 全額ポイント払いの場合はこのバリデーションをスキップ
                    errors_for_order = errors.get(order.order_no, )
                    if errors_for_order is None:
                        errors_for_order = errors[order.order_no] = []
                    errors_for_order.append(dict(type='error', message=u'未発券の予約をコンビニ払戻しようとしています'))
        self.request.session['ticketing.refund.settings'] = form_refund.data
        self.request.session['errors'] = errors
        return HTTPFound(location=self.request.route_path('orders.refund.confirm'))


@view_defaults(decorator=with_bootstrap, permission='event_editor', route_name='orders.refund.confirm', renderer='altair.app.ticketing:templates/orders/refund/confirm.html')
class OrdersRefundConfirmView(OrderBaseView):
    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.checked_orders = [o.lstrip('o:') for o in self.request.session.get('orders', []) if o.startswith('o:')]

    @view_config(request_method='GET')
    def get(self):
        # 払戻予約
        from altair.app.ticketing.core.models import PaymentMethod
        refund_settings = self.request.session['ticketing.refund.settings']
        payment_method = PaymentMethod.query.filter_by(id=refund_settings['payment_method_id']).one()
        errors_and_warnings = []
        error_count = 0
        warning_count = 0
        for order_no, errors in self.request.session['errors'].items():
            order = Order.query.filter_by(order_no=order_no).one()
            errors_for_order = (order, [])
            for error in errors:
                if error['type'] == 'error':
                    error_count += 1
                elif error['type'] == 'warning':
                    warning_count += 1
                errors_for_order[1].append(error)
            errors_and_warnings.append(errors_for_order)
        return dict(
            form_refund=OrderRefundForm(_data=refund_settings, context=self.context),
            form_search=OrderRefundSearchForm(
                MultiDict(self.request.session.get('ticketing.refund.condition', [])),
                organization_id=self.context.organization.id
                ),
            payment_method=payment_method,
            is_sej=(payment_method.payment_plugin_id == payments_plugins.SEJ_PAYMENT_PLUGIN_ID),
            is_famiport=(payment_method.payment_plugin_id == payments_plugins.FAMIPORT_PAYMENT_PLUGIN_ID),
            errors_and_warnings=errors_and_warnings,
            error_count=error_count,
            warning_count=warning_count,
            **refund_settings
            )

    @view_config(route_name='orders.refund.confirm', request_method='POST')
    def post(self):
        if self.request.session['errors']:
            self.request.session.flash(u'払戻できません')
            raise HTTPFound(location=self.request.route_path('orders.refund.settings'))
        # 払戻予約
        performances = []
        orders = Order.query.filter(Order.id.in_(self.checked_orders)).all()
        for o in orders:
            if o.performance not in performances:
                performances.append(o.performance)
        refund_params = dict(self.request.session['ticketing.refund.settings'])
        refund_params.update(
            organization=self.context.organization,
            orders=orders,
            order_count=len(orders),
            performances=performances,
            )
        refund = Order.reserve_refund(refund_params)

        mail_refund_to_user = self.context.organization.setting.mail_refund_to_user
        send_refund_reserve_mail(self.request, refund, mail_refund_to_user, orders)

        del self.request.session['orders']
        del self.request.session['errors']
        del self.request.session['ticketing.refund.settings']
        del self.request.session['ticketing.refund.condition']

        self.request.session.flash(u'払戻予約しました')
        return HTTPFound(location=route_path('orders.refund.index', self.request))


@view_defaults(decorator=with_bootstrap, permission='sales_counter')
class OrderDetailView(OrderBaseView):

    @view_config(route_name='orders.show_by_order_no')
    def show_by_order_no(self):
        order_no = self.request.matchdict.get('order_no', None)
        order = get_order_by_order_no(self.request, order_no)
        if order is None:
            raise HTTPNotFound('order no %s is not found' % order_no)
        return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

    @view_config(route_name='orders.show', renderer='altair.app.ticketing:templates/orders/show.html')
    def show(self):
        order = self.context.order
        if order is None:
            raise HTTPNotFound('order id %d is not found' % self.context.order_id)

        dependents = self.context.get_dependents_models()
        order_history = dependents.histories
        mail_magazines = dependents.mail_magazines
        default_ticket_format_id = self.context.default_ticket_format.id if self.context.default_ticket_format is not None else None

        joined_objects_for_product_item = dependents.describe_objects_for_product_item_provider(ticket_format_id=default_ticket_format_id)
        ordered_product_attributes = joined_objects_for_product_item.get_product_item_attributes()
        order_attributes = dependents.get_order_attributes()
        forms = self.context.get_dependents_forms()
        form_order_info = forms.get_order_info_form()
        form_shipping_address = forms.get_shipping_address_form()
        form_order = forms.get_order_form()
        form_refund = forms.get_order_refund_form()
        form_each_print = forms.get_each_print_form(default_ticket_format_id)
        payment_plugin_info, delivery_plugin_info = get_payment_delivery_plugin_info(self.request, order)
        is_orion = ORION_DELIVERY_PLUGIN_ID == order.delivery_plugin_id
        orion_ticket_phone = ""
        if is_orion:
            orion_ticket_phone = order.get_orion_ticket_phone_list
        return {
            'is_current_order': order.deleted_at is None,
            'order': order,
            'ordered_product_attributes': ordered_product_attributes,
            'order_attributes': order_attributes,
            'order_history': order_history,
            'point_grant_settings': loyalty_api.applicable_point_grant_settings_for_order(order),
            'payment_plugin_info': payment_plugin_info,
            'delivery_plugin_info': delivery_plugin_info,
            'mail_magazines': mail_magazines,
            'form_order_info': form_order_info,
            'form_shipping_address': form_shipping_address,
            'form_order': form_order,
            'form_refund': form_refund,
            'form_each_print': form_each_print,
            'form_order_edit_attribute': forms.get_order_edit_attribute(),
            "objects_for_describe_product_item": joined_objects_for_product_item(),
            'build_candidate_id': build_candidate_id,
            'endpoints': self.endpoints,
            'reservation': self.context.user.is_reservation,
            'laguna_reservation': order.organization.code == 'LG',
            'is_orion': is_orion,
            'orion_ticket_phone': orion_ticket_phone,
            }

    @view_config(route_name='orders.show.qr', permission='sales_editor', request_method='GET', renderer='altair.app.ticketing:templates/orders/_show_qr.html')
    def show_qr(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        qr_type = order.delivery_plugin_id
        url_builder = get_orderreview_qr_url_builder(self.request)
        qr_preferences = order.payment_delivery_pair.delivery_method.preferences.get(unicode(qr_type), {})
        single_qr_mode = qr_preferences.get('single_qr_mode', False)
        tickets = []
        if single_qr_mode and qr_type != payments_plugins.SKIDATA_QR_DELIVERY_PLUGIN_ID:  # SKIDATAは単一QRを許容しない
            if qr_type == payments_plugins.QR_AES_DELIVERY_PLUGIN_ID:
                qr_aes_plugin = lookup_qr_aes_plugin(self.request, self.context.organization.code)
                qr = qr_aes_plugin.build_qr_by_order(order)
            else:
                qr = build_qr_by_order(self.request, order)

            url = url_builder.build(self.request, qr, qr_type=qr_type)
            tickets.append({
                'token': None,
                'element': None,
                'item': None,
                'qr': qr,
                'url': url
                })
        else:
            tokens = [(token, element, item) for item in order.items for element in item.elements for token in
                      element.tokens]
            for token, element, item in tokens:
                if qr_type == payments_plugins.QR_AES_DELIVERY_PLUGIN_ID:
                    qr_aes_plugin = lookup_qr_aes_plugin(self.request, self.context.organization.code)
                    qr = qr_aes_plugin.build_qr_by_token(order.order_no, token)
                    url = url_builder.build(self.request, qr, qr_type=qr_type)
                elif qr_type == payments_plugins.SKIDATA_QR_DELIVERY_PLUGIN_ID:
                    qr = None  # orders/_show_qr.htmlでは'qr'を使用していない
                    url_builder = get_orderreview_skidata_qr_url_builder(self.request)
                    url = url_builder.build(self.request, token.skidata_barcode)
                else:
                    qr = build_qr_by_token(self.request, order.order_no, token)
                    url = url_builder.build(self.request, qr, qr_type=qr_type)
                tickets.append({
                    'token': token,
                    'element': element,
                    'item': item,
                    'qr': qr,
                    'url': url
                })
        return { 'order': order, 'tickets': tickets }

    @view_config(route_name='orders.edit.order_info', permission='sales_editor', request_method='POST', renderer='altair.app.ticketing:templates/orders/_modal_order_info.html')
    def edit_order_info(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        form = OrderInfoForm(self.request.POST)
        if form.validate():
            order.payment_due_at = form.payment_due_at.data
            order.issuing_start_at = form.issuing_start_at.data
            order.issuing_end_at = form.issuing_end_at.data
            payment_delivery_plugin, payment_plugin, delivery_plugin = lookup_plugin(self.request, order.payment_delivery_method_pair)
            try:
                if payment_delivery_plugin is not None:
                    payment_delivery_plugin.validate_order(self.request, order, update=True)
                else:
                    payment_plugin.validate_order(self.request, order, update=True)
                    delivery_plugin.validate_order(self.request, order, update=True)
                order.save()
                refresh_order(self.request, DBSession, order)
                self.request.session.flash(u'予約情報を保存しました')
            except OrderLikeValidationFailure as orderLikeValidationFailure:
                transaction.abort()
                self.request.session.flash(orderLikeValidationFailure.message)
            except (
                    FamiportPaymentDateNoneError,
                    FamiPortTicketingDateNoneError,
                    FamiPortAlreadyPaidError
            ) as dateNoneError:
                transaction.abort()
                self.request.session.flash(dateNoneError.message)
            except Exception as exception:
                exc_info = sys.exc_info()
                logger.error(u'[EMERGENCY] failed to update order %s' % order.order_no, exc_info=exc_info)
                transaction.abort()
                self.request.session.flash(exception.message)
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':form,
            }

    @view_config(route_name='orders.edit.regrant_number_due_at_info', permission='sales_editor', request_method='POST',
                 renderer='altair.app.ticketing:templates/orders/_modal_regrant_number_due_at_info.html')
    def edit_regrant_number_due_at_info(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id {} is not found'.format(order_id))

        form = OrderInfoForm(self.request.POST)
        regrant_number_due_at = form.regrant_number_due_at.data
        # 更新期限のバリデーション
        if not regrant_number_due_at:
            if not hasattr(form.regrant_number_due_at.errors, 'append'):
                form.regrant_number_due_at.errors = list(form.regrant_number_due_at.errors)
            form.regrant_number_due_at.errors.append(ValidationError(u"再付番期限日が更新可能な日付ではありません。"))
            return {
                'form': form,
            }

        if regrant_number_due_at < datetime.now() or regrant_number_due_at > datetime.now() + timedelta(days=364):
            if not hasattr(form.regrant_number_due_at.errors, 'append'):
                form.regrant_number_due_at.errors = list(form.regrant_number_due_at.errors)
            form.regrant_number_due_at.errors.append(ValidationError(u"再付番期限日が更新可能な日付ではありません。"))
            return {
                'form': form,
            }

        payment_delivery_plugin, payment_plugin, delivery_plugin = lookup_plugin(self.request,
                                                                                 order.payment_delivery_method_pair)
        try:
            if payment_delivery_plugin is not None:
                if isinstance(payment_delivery_plugin, SejPaymentDeliveryPlugin):
                    payment_delivery_plugin.validate_order(self.request, order, update=True)
                    payment_delivery_plugin.refresh(self.request, order, regrant_number_due_at=regrant_number_due_at)
                    self.request.session.flash(u'再付番発券日期限日情報を保存しました')
            else:
                if isinstance(delivery_plugin, SejDeliveryPlugin):
                    delivery_plugin.validate_order(self.request, order, update=True)
                    delivery_plugin.refresh(self.request, order, regrant_number_due_at=regrant_number_due_at)
                    self.request.session.flash(u'再付番発券日期限日情報を保存しました')
        except OrderLikeValidationFailure as orderLikeValidationFailure:
            transaction.abort()
            self.request.session.flash(orderLikeValidationFailure.message)
        except Exception as exception:
            exc_info = sys.exc_info()
            logger.error(u'[EMERGENCY] failed to update order %s' % order.order_no, exc_info=exc_info)
            transaction.abort()
            self.request.session.flash(exception.message)
        return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

    @view_config(route_name='orders.cancel', permission='sales_editor')
    def cancel(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        if order.cancel(self.request):
            notify_order_canceled(self.request, order)
            self.request.session.flash(u'予約(%s)をキャンセルしました' % order.order_no)
            return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))
        else:
            self.request.session.flash(u'予約(%s)をキャンセルできません' % order.order_no)
            raise HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

    @view_config(route_name='orders.sej_cancel', permission='administrator', request_method='GET'
                 , renderer='altair.app.ticketing:templates/orders/sej_cancel.html')
    def sej_cancel(self):
        form = SejOrderCancelForm()
        form.validated.data = False
        return {'form': form}

    @view_config(route_name='orders.sej_cancel', permission='administrator', request_method='POST'
                 , renderer='altair.app.ticketing:templates/orders/sej_cancel.html')
    def sej_confirm_cancel(self):
        form = SejOrderCancelForm(self.request.POST)
        order = get_order_by_order_no(self.request, form.order_no.data)
        if not form.validate({'order': order}):
            return {'form': form}
        form.validated.data = True
        return {'order': order, 'form': form}

    @view_config(route_name='orders.sej_cancel_complete', permission='administrator', request_method='POST'
                 , renderer='altair.app.ticketing:templates/orders/sej_cancel_complete.html')
    def sej_complete_cancel(self):
        form = SejOrderCancelForm(self.request.POST)
        if form.validated.data:
            order_no = self.request.matchdict.get('order_no', None)
            order = get_order_by_order_no(self.request, order_no)
            payment_plugin = get_payment_plugin(self.request, order.payment_delivery_pair.payment_method.payment_plugin_id)
            payment_plugin.cancel(self.request, order)
            order.release()
            order.mark_canceled()
            return {'order': order, 'form': form}

    @view_config(route_name='orders.famiport_cancel', permission='administrator', request_method='GET'
                 , renderer='altair.app.ticketing:templates/orders/famiport_cancel.html')
    def famiport_cancel(self):
        form = FamiPortOrderCancelForm()
        form.validated.data = False
        return {'form': form}

    @view_config(route_name='orders.famiport_cancel', permission='administrator', request_method='POST'
                 , renderer='altair.app.ticketing:templates/orders/famiport_cancel.html')
    def famiport_confirm_cancel(self):
        form = FamiPortOrderCancelForm(self.request.POST)
        order = get_order_by_order_no(self.request, form.order_no.data)
        if not form.validate({'order': order}):
            return {'form': form}
        form.validated.data = True
        return {'order': order, 'form': form}

    @view_config(route_name='orders.famiport_cancel_complete', permission='administrator', request_method='POST'
                 , renderer='altair.app.ticketing:templates/orders/famiport_cancel_complete.html')
    def famiport_complete_cancel(self):
        form = FamiPortOrderCancelForm(self.request.POST)
        if form.validated.data:
            order_no = self.request.matchdict.get('order_no', None)
            order = get_order_by_order_no(self.request, order_no)
            payment_plugin = get_payment_plugin(self.request, order.payment_delivery_pair.payment_method.payment_plugin_id)
            payment_plugin.cancel(self.request, order)
            order.release()
            order.mark_canceled()
            return {'order': order, 'form': form}

    @view_config(route_name='orders.delete', permission='sales_editor')
    def delete(self):

        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        try:
            order.delete()
        except Exception:
            self.request.session.flash(u'予約(%s)を非表示にできません' % order.order_no)
            raise HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

        self.request.session.flash(u'予約(%s)を非表示にしました' % order.order_no)
        return HTTPFound(location=route_path('orders.optional', self.request))

    @view_config(route_name='orders.refund.immediate', permission='sales_editor')
    def refund_immediate(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        f = OrderRefundForm(
            self.request.POST,
            context=self.context,
            orders=[order]
        )

        # 未発券のコンビニ払戻を警告
        from altair.app.ticketing.core.models import PaymentMethod
        refund_pm = PaymentMethod.query.filter_by(id=f.payment_method_id.data).one()
        if refund_pm.can_use_point() and order.point_use_type is PointUseTypeEnum.AllUse:
            # TKT-6643 払戻方法にポイント利用可能な支払方法が選択され、かつ全額ポイント払いの場合は以降のバリデーションをスキップ
            # ポイント利用可能な支払方法を判定する理由は、このバリデーションを通過してポイント利用を考慮していない決済プラグインの
            # refund_orderを実行させたくないため。つまり影響範囲を最小とするため。
            pass
        elif order.payment_plugin_id in [payments_plugins.SEJ_PAYMENT_PLUGIN_ID,
                                       payments_plugins.FAMIPORT_PAYMENT_PLUGIN_ID]:
            if not order.is_issued():
                self.request.session.flash(u'未発券の予約（予約番号：{}）をコンビニ払戻しようとしています。'.format(order.order_no))
                response = render_to_response('altair.app.ticketing:templates/orders/refund/_form.html', {'form': f},
                                              request=self.request)
                response.status_int = 400
                return response

        if f.validate():
            refund_param = f.data
            refund_param.update(dict(
                organization=self.context.organization,
                orders=[order],
                order_count=1,
                performances=[order.performance],
            ))
            refund = Order.reserve_refund(refund_param)
            if order.call_refund(self.request):
                order.refund.status = RefundStatusEnum.Refunded.v
                order.refund.save()
                refund_point_amount = order.refund_point_amount
                if refund_point_amount > 0:
                    # 払戻ポイント額が0ポイント以上の場合のみ保存
                    RefundPointEntry.create_refund_point_entry(order, refund_point_amount)
                self.request.session.flash(u'予約(%s)を払戻しました' % order.order_no)
                return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
            else:
                self.request.session.flash(u'予約(%s)を払戻できません' % order.order_no)

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
        if order.change_payment_status(status):
            self.request.session.flash(u'予約(%s)のステータスを変更しました' % order.order_no)
        else:
            self.request.session.flash(u'予約(%s)のステータスを変更できません' % order.order_no)
        return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

    @view_config(route_name='orders.delivered', permission='sales_editor')
    def delivered(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        if order.delivered():
            self.request.session.flash(u'予約(%s)を配送済みにしました' % order.order_no)
        else:
            self.request.session.flash(u'予約(%s)を配送済みにできません' % order.order_no)
        return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

    @view_config(route_name='orders.undelivered', permission='sales_editor')
    def undelivered(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        if order.undelivered():
            self.request.session.flash(u'予約(%s)を未配送にしました' % order.order_no)
        else:
            self.request.session.flash(u'予約(%s)を未配送済みにできません' % order.order_no)
        return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

    @view_config(route_name='orders.edit_delivered', permission='sales_editor', request_method='GET',
                 renderer='altair.app.ticketing:templates/orders/edit_delivered.html')
    def get_edit_delivered(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)
        form = DeliverdEditForm()
        form.delivered_at.data = order.delivered_at
        return {'order': order, 'form': form}

    @view_config(route_name='orders.edit_delivered', permission='sales_editor', request_method='POST',
                 renderer='altair.app.ticketing:templates/orders/edit_delivered.html')
    def post_edit_delivered(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)
        form = DeliverdEditForm(self.request.POST)
        if not form.validate():
            return {'order': order, 'form': form}
        order.delivered_at = form.delivered_at.data
        self.request.session.flash(u'配送時刻を変更しました')
        return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

    @view_config(route_name='orders.edit.shipping_address', request_method='POST', renderer='altair.app.ticketing:templates/orders/_modal_shipping_address.html')
    def edit_shipping_address_post(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        f = ClientOptionalForm(self.request.POST, context=self.context)
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

    def _new_order_from_order_form(self, f, order):
        new_order = ProtoOrder.create_from_order_like(order)
        new_order.system_fee = f.system_fee.data
        new_order.transaction_fee = f.transaction_fee.data
        new_order.delivery_fee = f.delivery_fee.data
        new_order.special_fee = f.special_fee.data
        new_order.special_fee_name = f.special_fee_name.data

        for op, nop in itertools.izip(order.items, new_order.items):
            # 個数が変更できるのは数受けのケースのみ
            if op.product.seat_stock_type.quantity_only:
                nop.quantity = f.products.data['products'].get(op.id) or 0

            for opi, nopi in itertools.izip(op.elements, nop.elements):
                nopi.price = f.products.data['product_items'].get(opi.id) or 0
                if op.product.seat_stock_type.quantity_only:
                    nopi.quantity = nop.quantity * nopi.product_item.quantity
                    for token in nopi.tokens:
                        make_transient(token)
                    nopi.tokens = [
                        OrderedProductItemToken(
                            serial=i,
                            seat=seat,
                            valid=True
                            )
                        for i, seat in core_api.iterate_serial_and_seat(nopi)
                        ]

            nop.price = sum(nopi.price * nopi.product_item.quantity for nopi in nop.elements)

        new_order.total_amount = recalculate_total_amount_for_order(self.request, new_order)
        if new_order.total_amount < order.total_amount:
            '''
            Orderの総額が減額されるパターン、この時ポイント充当額を再計算する。
            
            Orderのデータ整合のためポイントを除いた支払額は0以上を保証する。
            すなわちOrder.total_amount - Order.point_amount >= 0でこれはOrder.total_amount >= Order.point_amountと同じ
            
            減額後も総額がポイント充当額以上なら、Order.point_amountはそのままの値を採用
            減額後に総額がポイント充当額より小さい場合、Order.total_amount >= Order.point_amountに違反するので、
            ポイント充当額を変更後の総額に合わせる
            (ex 変更前:総額3000円・2000ポイント利用で、総額を1500円に減額 → 変更後のOrderは総額1500円・1500ポイント利用にする)
            '''
            new_order.point_amount = min(new_order.point_amount, new_order.total_amount)
        return new_order

    @view_config(route_name='orders.edit.product', request_method='POST')
    def edit_product_post(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = get_order_by_id(self.request, order_id)

        if order.status == 'canceled' or order.status == 'refunded':
            self.request.session.flash(u'キャンセル、または、払戻済みの為、商品の変更はできません')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

        if order is None or order.organization_id != self.context.organization.id:
            return HTTPNotFound('order id %d is not found' % order_id)

        f = OrderForm(self.request.POST, context=self.context)
        has_error = False

        try:
            if not f.validate():
                raise ValidationError()
            new_order = self._new_order_from_order_form(f, order)
            if len(order.used_discount_codes) > 0:
                logger.info('order.used_discount_codes=%s' % order.used_discount_codes[0].code)
                raise ValidationError(u'クーポン・割引コードの使用があるため、商品を変更できませんでした')

            if order.payment_status != 'unpaid':
                if order.total_amount != new_order.total_amount:
                    raise ValidationError(u'入金済みの為、合計金額は変更できません')

            # TKT-6590 金額変更によってポイント払いの状態が変わる(ex: 一部ポイント払い→全部ポイント払い or その逆)ような場合は
            # 決済方法が変わってしまう。決済まわりのデータ管理が煩雑になりリスクとなるため、このような金額変更は許容しない
            if order.point_use_type == PointUseTypeEnum.PartialUse and \
                    new_order.point_use_type == PointUseTypeEnum.AllUse:
                # 減額によって、全額ポイント払いになってしまうケース
                raise ValidationError(u'一部ポイント払いの場合、ご利用ポイント{}よりも合計金額を減額できません'
                                      .format(int(order.point_amount)))

            save_order_modifications_from_proto_orders(
                self.request,
                [(order, new_order)]
                )
        except ValidationError as e:
            if e.message:
                self.request.session.flash(e.message)
            has_error = True
        except NotEnoughStockException as e:
            logger.info("not enough stock quantity :%s" % e)
            self.request.session.flash(u'在庫がありません')
            has_error = True
        except (MassOrderCreationError, MassOrderModificationError) as e:
            for error in e.errors[order.order_no]:
                self.request.session.flash(error.message)
            has_error = True
        except Exception as e:
            logger.info('save error (%s)' % e.message, exc_info=sys.exc_info())
            self.request.session.flash(u'入力された金額および個数が不正です')
            has_error = True
        finally:
            if has_error:
                response = render_to_response('altair.app.ticketing:templates/orders/_form_product.html', {'form':f, 'order':order}, request=self.request)
                response.status_int = 400
                transaction.abort()
                return response

        self.request.session.flash(u'予約を保存しました')
        return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

    @view_config(route_name="orders.cover.preview", request_method="GET", renderer="altair.app.ticketing:templates/orders/_cover_preview_dialog.html")
    def cover_preview_dialog(self):
        order = self.context.order
        ticket_format_id = self.context.ticket_format.id
        if order is None:
            raise HTTPNotFound('order id %d is not found' % self.context.order_id)
        cover = TicketCover.get_from_order(order, ticket_format_id)
        if cover is None:
            raise HTTPNotFound('cover is not found. order id %d' % order.id)
        svg_builder = get_svg_builder(self.request)
        svg = svg_builder.build(cover.ticket, build_cover_dict_from_order(order))
        data = {"ticket_format": cover.ticket.ticket_format_id, "sx": "1", "sy": "1"}
        transformer = SVGTransformer(svg, data)
        svg = transformer.transform()
        preview = SVGPreviewCommunication.get_instance(self.request)
        imgdata_base64 = preview.communicate(self.request, svg, cover.ticket.ticket_format)
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
        return {
            "item": self.context.ordered_product_item,
            "ticket_format_id": self.context.ticket_format_id,
            }

    @view_config(route_name="orders.item.preview.getdata", request_method="GET", renderer="json")
    def order_item_get_data_for_preview(self):
        tickets = Ticket.query \
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(ProductItem.id==OrderedProductItem.product_item_id)\
            .filter(TicketBundle.id==ProductItem.ticket_bundle_id)\
            .filter(Ticket_TicketBundle.ticket_bundle_id==TicketBundle.id)\
            .filter(Ticket.id==Ticket_TicketBundle.ticket_id)\
            .filter(Ticket.ticket_format_id==self.context.ticket_format.id)\
            .filter(OrderedProductItem.id==self.context.ordered_product_item.id)\
            .all()
        dicts = build_dicts_from_ordered_product_item(self.context.ordered_product_item, ticket_number_issuer=NumberIssuer())
        data = dict(self.context.ticket_format.data)
        data["ticket_format_id"] = self.context.ticket_format.id
        results = []
        names = []
        svg_builder = get_svg_builder(self.request)
        for seat, dict_ in dicts:
            names.append(seat.name if seat else dict_["product"]["name"])
            preview_type = utils.guess_preview_type_from_ticket_format(self.context.ticket_format)

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
        order = get_order_by_id(self.request, order_id)
        if order is None or order.organization_id != self.context.organization.id:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'不正なデータです',
            }))
        ## todo:validation?
        params = {k.decode("utf-8"):v for k, v in self.request.POST.items() if not k.startswith("_")}
        for_ = 'lots' if order.created_from_lot_entry else 'cart'
        OrderAttributeIO(include_undefined_items=True, mode='any', for_=for_).unmarshal(self.request, order, params)
        order.save()
        self.request.session.flash(u'属性を変更しました')
        return HTTPFound(self.request.route_path(route_name="orders.show", order_id=order_id)+"#order_attributes")

    @view_config(route_name="orders.ordered_product_attribute_edit", request_method="POST")
    def edit_ordered_product_attribute(self):
        order_no = self.request.matchdict.get('order_no', None)
        update_list = self.create_update_ordered_product_item_list(self.request.POST.items())

        order = Order.query.filter(Order.order_no==order_no).first()
        if order.status == 'canceled' or order.status == 'refunded':
            self.request.session.flash(u'キャンセル、または、払戻済みの為、購入商品属性の更新は行えません')
            return HTTPFound(self.request.route_path(route_name="orders.show", order_id=order.id) + "#ordered_product_attributes")

        new_order = Order.clone(order, deep=True)

        for target_data in update_list:
            self.update_ordered_product_item_attribute(target_data['name'], target_data['value'], order, new_order)

        self.request.session.flash(u'購入商品属性を変更しました')
        return HTTPFound(self.request.route_path(route_name="orders.show", order_id=order.id) + "#ordered_product_attributes")

    def create_update_ordered_product_item_list(self, formitems):
        max = len(formitems)/3
        update_list = []
        for num in range(0, max):
            update_dict = {'order_product_item_id': formitems[num*3][1],
                           'name': formitems[num*3+1][1],
                           'value': formitems[num*3+2][1]
            }
            update_list.append(update_dict)
        return update_list

    def update_ordered_product_item_attribute(self, name, value, order, new_order):
        new_order_dict = {}
        for product in new_order.items:
            for item in product.elements:
                new_order_dict.update({(product.product_id, item.product_item_id) : item})

        target_ordered_product_item = None
        for product in order.items:
            for item in product.elements:
                if (product.product_id, item.product_item_id) in new_order_dict:
                    target_ordered_product_item = new_order_dict[(product.product_id, item.product_item_id)]

        assert target_ordered_product_item is not None
        target_ordered_product_item.attributes[name] = value

    @view_config(route_name="orders.memo_on_order", request_method="POST", renderer="json")
    def edit_memo_on_order(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = get_order_by_id(self.request, order_id)
        if order is None or order.organization_id != self.context.organization.id:
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

    @view_config(route_name="orders.orion_phones", request_method="POST", renderer="json")
    def edit_orion_phone_on_order(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = get_order_by_id(self.request, order_id)

        if order is None or order.organization_id != self.context.organization.id:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'不正なデータです',
            }))

        try:
            orion_ticket_phone = OrionTicketPhone.filter_by(order_no=order.order_no).one()
        except (NoResultFound, MultipleResultsFound):
            raise HTTPBadRequest(body=json.dumps({
                'message': u'不正なデータです',
            }))

        orion_phone_list = self.request.params.getall('orion-ticket-phone')
        orion_phone_errors = verify_orion_ticket_phone(orion_phone_list)

        if any(orion_phone_errors):
            raise HTTPBadRequest(body=json.dumps({
                'message': " ".join(orion_phone_errors),
            }))

        orion_phones = orion_ticket_phone.phones
        input_phones = ','.join([str(s) for s in orion_phone_list])

        if not input_phones == orion_phones:
            orion_ticket_phone.phones = input_phones
            orion_ticket_phone.save()
        return {}

    @view_config(route_name="orders.point_grant_mode", request_method="POST", renderer="json", permission="event_editor")
    def update_point_grant_mode(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = get_order_by_id(self.request, order_id)
        if order is None:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'不正なデータです',
            }))

        params = MultiDict(self.request.json_body)
        if params["point_grant_mode"] == "auto":
            order.manual_point_grant = False
        elif params["point_grant_mode"] == "manual":
            order.manual_point_grant = True

        order.save()
        return {}

    @view_config(route_name='orders.note', request_method='POST', renderer='json', permission='sales_counter')
    def note(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = get_order_by_id(self.request, order_id)
        if order is None or order.organization_id != self.context.organization.id:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'不正なデータです',
            }))

        f = OrderReserveForm(MultiDict(self.request.json_body), request=self.request)
        if not f.note.validate(f):
            raise HTTPBadRequest(body=json.dumps({
                'message':f.note.errors,
            }))

        order.note = f.note.data
        order.save()
        return {}

    @view_config(route_name='orders.sales_summary', renderer='altair.app.ticketing:templates/orders/_sales_summary.html', permission='sales_counter')
    def sales_summary(self):
        sales_segments = [self.context.sales_segment] if self.context.sales_segment is not None else self.context.sales_segments
        stock_types = {}
        for p in self.context.products:
            for pi in p.items:
                stock_data_for_stock_type = stock_types.get(pi.stock.stock_type)
                if stock_data_for_stock_type is None:
                    stock_data_for_stock_type = stock_types[pi.stock.stock_type] = {}
                stock_data_for_stock = stock_data_for_stock_type.get(pi.stock)
                if stock_data_for_stock is None:
                    stock_data_for_stock_type[pi.stock] = stock_data_for_stock = dict(
                        stock=pi.stock,
                        products=set()
                        )
                if p not in stock_data_for_stock['products']:
                    stock_data_for_stock['products'].add(p)

        sales_summary = []
        for stock_type in self.context.performance.event.stock_types: # ordered by display-order
            stock_data_for_stock_type = stock_types.get(stock_type)
            if stock_data_for_stock_type is None:
                continue
            stock_data = stock_data_for_stock_type.values()
            for s in stock_data:
                s['products'] = sorted(s['products'], key=lambda p: p.display_order)
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

        if not order.issued:
            ## printed_atをNULLにし直す
            order.printed_at = None
            for ordered_product in order.ordered_products:
                for ordered_product_item in ordered_product.ordered_product_items:
                    ordered_product_item.printed_at = None
                    #ordered_product_item.issued_at = None
                    for token in ordered_product_item.tokens:
                        #token.issued_at = None
                        token.printed_at = None
        return HTTPFound(location=self.request.route_path('orders.show', order_id=order.id))

    @view_config(route_name="orders.print.queue.dialog", request_method="GET", renderer="altair.app.ticketing:templates/orders/_print_queue_dialog.html")
    def print_queue_dialog(self):
        order = Order.query.get(self.request.matchdict["order_id"])
        return {
            "order": order,
            "form": TicketFormatSelectionForm(context=self.context)
            }

    @view_config(route_name="orders.checked.queue", request_method="GET", permission='sales_counter', renderer='altair.app.ticketing:templates/orders/_form_ticket_format.html', xhr=True)
    def show_enqueue_checked_order_form(self):
        if len(self.context.order_ids) == 0:
            return HTTPBadRequest(text=u"発券対象を選択してください");
        return {
            'form': TicketFormatSelectionForm(context=self.context),
            'action': self.request.current_route_path(),
            }

    @view_config(route_name="orders.checked.queue", request_method="POST", permission='sales_counter')
    def enqueue_checked_order(self):
        form = TicketFormatSelectionForm(self.request.params, context=self.context)
        if not form.validate():
            return HTTPBadRequest()
        ticket_format_id = form.ticket_format_id.data
        qs = DBSession.query(Order)\
            .filter(Order.deleted_at==None).filter(Order.canceled_at==None).filter(Order.id.in_(self.context.order_ids))\
            .filter(Order.issued==False)\

        will_removes = []
        break_p = False
        count = 0
        total = 0
        for order in qs:
            will_removes.append(order)
            if not self.context.user.is_member_of_organization(order):
                if not break_p:
                    self.request.session.flash(u'異なる組織({operator.organization.name})の管理者で作業したようです。「{order.organization.name}」の注文を対象にした操作はスキップされました。'.format(order=order, operator=self.context.user))
                    break_p = True
            elif not order.queued:
                utils.enqueue_cover(self.request, operator=self.context.user, order=order, ticket_format_id=ticket_format_id)
                utils.enqueue_for_order(self.request, operator=self.context.user, order=order, ticket_format_id=ticket_format_id)
                count += 1
            total += 1

        logger.info("*ticketing print queue many* clean session")
        session_values = self.request.session.get("orders", [])
        for order in will_removes:
            session_values.remove("o:%s" % order.id)
        self.request.session["orders"] = session_values

        if not break_p:
            self.request.session.flash(u'%d個中%d個の注文を印刷キューに追加しました. (既に印刷済みの注文とキャンセル済みの注文は印刷キューに追加されません)' % (total, count))
            if self.request.POST.get("redirect_url"):
                return HTTPFound(location=self.request.POST.get("redirect_url"))

        return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

    @view_config(route_name="orders.print.queue.each", request_method="GET", renderer="altair.app.ticketing:templates/orders/_show_product_table.html")
    def order_tokens_print_queue_form(self):
        order = self.context.order
        if order is None:
            raise HTTPNotFound('order id %d is not found' % self.context.order_id)
        form_each_print = TicketFormatSelectionForm(self.request.GET, context=self.context)
        if form_each_print.ticket_format_id.data is None:
            if self.context.default_ticket_format is not None:
                form_each_print.ticket_format_id.data = self.context.default_ticket_format.id
        if not form_each_print.validate():
            return HTTPBadRequest()

        dependents = self.context.get_dependents_models()
        joined_objects_for_product_item = dependents.describe_objects_for_product_item_provider(ticket_format_id=form_each_print.ticket_format_id.data)

        return {
            'order': order,
            'form': form_each_print,
            "objects_for_describe_product_item": joined_objects_for_product_item(),
            'build_candidate_id': build_candidate_id,
            }

    @view_config(route_name="orders.print.queue.each", request_method="POST", request_param="submit=print")
    def order_tokens_print_queue(self):
        order = self.context.order
        if order is None:
            raise HTTPNotFound('order id %d is not found' % self.context.order_id)
        form_each_print = TicketFormatSelectionForm(self.request.GET, context=self.context)
        if not form_each_print.validate():
            self.request.session.flash(u'券面を印刷キューに追加できませんでした')
            return HTTPFound(location=self.request.route_path('orders.show', order_id=order.id))

        ticket_format_id = form_each_print.ticket_format_id.data
        candidate_id_list = self.request.POST.getall('candidate_id')
        #token@seat@ticket.id
        actions = self.context.get_dependents_actions(order, ticket_format_id)
        candidates_action = actions.get_print_candidate_action(candidate_id_list)
        candidates_action.enqueue(self.request, operator=self.context.user)
        self.request.session.flash(u'券面を印刷キューに追加しました')
        return HTTPFound(location=self.request.route_path('orders.show', order_id=order.id))

    #print.queueの操作ではなくrefreshする操作
    @view_config(route_name="orders.print.queue.each", request_method="POST", request_param="submit=refresh")
    def order_tokens_refresh(self):
        from .helpers import decode_candidate_id
        now = datetime.now()

        order = self.context.order
        if order is None:
            raise HTTPNotFound('order id %d is not found' % self.context.order_id)

        candidate_id_list = self.request.POST.getall("candidate_id")
        token_id_list = [decode_candidate_id(e)[0] for e in candidate_id_list]
        token_id_list = [t for t in token_id_list if t is not None]
        self.context.refresh_tokens(order, token_id_list, now)
        self.request.session.flash(u'再発券許可しました')
        return HTTPFound(location=self.request.route_path('orders.show', order_id=order.id))

    @view_config(route_name='orders.print.queue')
    def order_print_queue(self):
        form = TicketFormatSelectionForm(self.request.params, context=self.context)
        if not form.validate():
            return HTTPBadRequest()
        ticket_format_id = form.ticket_format_id.data
        utils.enqueue_cover(self.request, operator=self.context.user, order=self.context.order, ticket_format_id=ticket_format_id)
        utils.enqueue_for_order(self.request, operator=self.context.user, order=self.context.order, ticket_format_id=ticket_format_id)
        self.request.session.flash(u'券面を印刷キューに追加しました')
        return HTTPFound(location=self.request.route_path('orders.show', order_id=self.context.order.id))

    @view_config(route_name='orders.fraud.clear', permission='sales_editor')
    def fraud_clear(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = get_order_by_id(self.request, order_id)
        if order is None or order.organization_id != self.context.organization.id:
            return HTTPNotFound('order id %d is not found' % order_id)

        order.fraud_suspect = 0
        order.save()

        self.request.session.flash(u'不正アラートを解除しました')
        return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

    @view_config(route_name='orders.release_stocks', permission='sales_editor')
    def release_stocks(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id, self.context.organization.id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        if order.release_stocks():
            self.request.session.flash(u'予約(%s)の在庫を解放しました' % order.order_no)
        else:
            self.request.session.flash(u'予約(%s)の在庫を解放できません' % order.order_no)
        return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))


@view_defaults(decorator=with_bootstrap, permission='sales_counter')
class OrdersReserveView(OrderBaseView):

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

    @view_config(route_name='orders.reserve.form', request_method='POST', renderer='altair.app.ticketing:templates/orders/_form_reserve.html')
    def reserve_form(self):
        post_data = self.request.POST
        logger.debug('order reserve post_data=%s' % post_data)

        # 古いカートのセッションが残っていたら削除
        api.remove_cart(self.request, release=True, async=False)

        form_reserve = self.context.form

        seat_l0_ids = self.context.seats_form.seats.data

        # 選択されたSeatがあるならステータスをKeepにして確保する
        seats = None
        if seat_l0_ids:
            try:
                reserving = api.get_reserving(self.request)
                seats = reserving.reserve_selected_seats(
                   [(stock.stock_status, 0) for stock in self.context.stocks],
                   self.context.performance.id,
                   seat_l0_ids,
                   reserve_status=SeatStatusEnum.Keep
                   )
            except InvalidSeatSelectionException:
                logger.info("seat selection is invalid.")
                self.context.raise_error(u'既に予約済か選択できない座席です。画面を最新の情報に更新した上で再度座席を選択してください。')
            except Exception, e:
                logger.exception('save error (%s)' % e.message)
                self.context.raise_error(u'エラーが発生しました')

        return {
            'form':form_reserve,
            'form_order_edit_attribute': OrderMemoEditFormFactory(3)(),
            'performance': self.context.performance,
        }

    @view_config(route_name='orders.reserve.form.reload', request_method='POST', renderer='altair.app.ticketing:templates/orders/_form_reserve.html')
    def reserve_form_reload(self):
        return {
            'form': self.context.form,
            'form_order_edit_attribute': OrderMemoEditFormFactory(3)(self.request.POST),
            'performance': self.context.performance,
        }

    @view_config(route_name='orders.reserve.confirm', request_method='POST', renderer='altair.app.ticketing:templates/orders/_form_reserve_confirm.html')
    def reserve_confirm(self):
        # 古いカートのセッションが残っていたら削除
        api.remove_cart(self.request, release=True, async=False)
        post_data = self.request.POST
        performance_id = post_data.get('performance_id', 0)
        self.electing_stock_check(performance_id)
        try:
            if not self.context.form.validate():
                self.context.raise_error(self.context.form.errors)
            ## memo
            form_order_edit_attribute = OrderMemoEditFormFactory(3)(post_data)
            if not form_order_edit_attribute.validate():
                self.context.raise_error(form_order_edit_attribute.get_error_messages())

            seats = self.context.seats_form.seats.data
            order_items = []
            total_quantity = 0
            for product_id, product_name in self.context.form.products.choices:
                quantity = post_data.get('product_quantity-%d' % product_id)
                if not quantity or quantity == u'0':
                    continue
                quantity = quantity.encode('utf-8')
                if not quantity.isdigit():
                    self.context.raise_error(u'個数が不正です')
                product_quantity = int(quantity)
                product = DBSession.query(Product).filter_by(id=product_id).one()
                # 「予約する」モーダルウィンドウでは連席を商品の数量倍率で割って表示しているため、ここで実際に押さえている席数に戻す TKT-2822
                power = product.get_quantity_power(product.seat_stock_type, self.context.performance.id)
                total_quantity += product_quantity * power
                order_items.append((product, product_quantity))

            if not total_quantity:
                self.context.raise_error(u'個数を入力してください')
            elif seats and total_quantity != len(seats):
                self.context.raise_error(u'個数の合計（{}席）を選択した座席数（{}席）にしてください'.format(total_quantity, len(seats)))

            # 選択されたSeatのステータスをいったん戻してカートデータとして再確保する
            self.release_seats(self.context.performance.venue, seats)

            # create cart
            cart = api.order_products(self.request, self.context.sales_segment, order_items, selected_seats=seats)
            pdmp = DBSession.query(PaymentDeliveryMethodPair).filter_by(id=self.context.form.payment_delivery_method_pair_id.data).one()
            if pdmp.payment_method.payment_plugin.id in [payments_plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID,
                                                         payments_plugins.PGW_CREDIT_CARD_PAYMENT_PLUGIN_ID]:
                self.context.raise_error(u'クレジットカード以外の決済方法を選択してください')
            cart.payment_delivery_pair = pdmp
            cart.channel = ChannelEnum.INNER.v
            cart.operator = self.context.user

            cart.shipping_address = ShippingAddress(
                first_name=self.context.form.first_name.data,
                last_name=self.context.form.last_name.data,
                first_name_kana=self.context.form.first_name_kana.data,
                last_name_kana=self.context.form.last_name_kana.data,
                country=u'日本',
                zip=self.context.form.zip.data,
                prefecture=self.context.form.prefecture.data,
                city=self.context.form.city.data,
                address_1=self.context.form.address_1.data,
                address_2=self.context.form.address_2.data,
                email_1=self.context.form.email_1.data,
                tel_1=self.context.form.tel_1.data,
                tel_2=""
            )

            try:
                validate_order_like(self.request, cart)
            except OrderLikeValidationFailure as e:
                self.context.raise_error(e.message)

            DBSession.add(cart)
            DBSession.flush()
            api.set_cart(self.request, cart)

            return {
                'cart':cart,
                'form': self.context.form,
                'performance': self.context.performance,
                'form_order_edit_attribute': form_order_edit_attribute
            }
        except ValidationError as e:
            self.context.raise_error(e.message)
        except NotEnoughAdjacencyException:
            logger.info("not enough adjacency")
            raise self.context.raise_error(u'連席で座席を確保できません。座席を直接指定するか、席数を減らして確保してください。')
        except InvalidSeatSelectionException:
            logger.info("seat selection is invalid.")
            self.context.raise_error(u'既に予約済か選択できない座席です。画面を最新の情報に更新した上で再度座席を選択してください。')
        except NotEnoughStockException as e:
            logger.info("not enough stock quantity :%s" % e)
            self.context.raise_error(
                u'在庫がありません。 {holder}「{stock_type_name}」 必要席数: {required} 残席数: {actual}'.format(
                    holder=e.stock_holder_name,
                    stock_type_name=e.stock_type_name,
                    required=e.required,
                    actual=e.actualy)
            )
        except InnerCartSessionException as e:
            logger.exception("oops :%s" % e)
            self.context.raise_error(u'エラーが発生しました。もう一度選択してください。')
        except SilentOrderLikeValidationFailure as e:
            logger.info("silent order like validation failure :%s" % e)
            self.context.raise_error(e.message_to_users)
        except OrderLikeValidationFailure as e:
            logger.exception("oops :%s" % e)
            self.context.raise_error(e.message)
        except Exception as e:
            if isinstance(e, Response):
                raise
            else:
                logger.exception('save error (%s)' % e.message)
                self.context.raise_error(u'エラーが発生しました')

    @view_config(route_name='orders.reserve.complete', request_method='POST', renderer='json')
    def reserve_complete(self):
        post_data = self.request.POST
        with_enqueue = post_data.get('with_enqueue', False)
        with_cover = post_data.get('with_cover', False)
        performance_id = post_data.get('performance_id', 0)
        self.electing_stock_check(performance_id)

        try:
            # create order
            cart = api.get_cart_safe(self.request)
            note = post_data.get('note')
            try:
                order = create_inner_order(self.request, cart, note)
            except Exception as e:
                logger.exception('call payment/delivery plugin error')
                self.context.raise_error(u'決済・配送プラグインでエラーが発生しました (%s)' % e, HTTPInternalServerError)

            pdmp = order.payment_delivery_pair
            # 窓口での決済方法
            attr = 'sales_counter_payment_method_id'
            sales_counter_id = int(post_data.get(attr, 0))
            if sales_counter_id:
                order.attributes[attr] = sales_counter_id

                # 窓口で決済済みなら決済済みにする (コンビニ決済以外)
                if not pdmp.payment_method.pay_at_store():
                    order.paid_at = datetime.now()
            # memo
            form_order_edit_attribute = OrderMemoEditFormFactory(3)(post_data)
            if not form_order_edit_attribute.validate():
                self.context.raise_error(u"文言・メモの設定でエラーが発生しました")
            for k, v in form_order_edit_attribute.get_result():
                if v:
                    order.attributes[k] = v

            # 入金済みでSkidata連携する必要がある場合はSkidataへWhitelistを送信する
            send_whitelist_if_necessary(request=self.request, order=order, fail_silently=True)

            # 当日窓口発券モードは窓口受取と配送の引取方法のみキューに追加する
            if with_enqueue and pdmp.delivery_method.delivery_plugin_id in INNER_DELIVERY_PLUGIN_IDS:
                try:
                    ticket_format_id = int(post_data.get('ticket_format_id'))
                except (TypeError, ValueError):
                    ticket_format_id = None
                    self.request.session.flash(u'チケット様式が選択されていないため発券されませんでした。', allow_duplicate=False)

                if ticket_format_id:
                    if with_cover:
                        utils.enqueue_cover(self.request, operator=self.context.user,
                                            order=order, ticket_format_id=ticket_format_id)
                    utils.enqueue_for_order(
                        self.request, operator=self.context.user, order=order,
                        delivery_plugin_ids=INNER_DELIVERY_PLUGIN_IDS, ticket_format_id=ticket_format_id)
            elif with_enqueue:
                self.request.session.flash(u'窓口受取と配送以外の引取方法のため発券されませんでした。', allow_duplicate=False)

            # clear session
            api.disassociate_cart_from_session(self.request)
            if self.request.session.get('altair.app.ticketing.inner_cart'):
                del self.request.session['altair.app.ticketing.inner_cart']

            return dict(order_id=order.id)
        except NoCartError, e:
            logger.info("%s" % e.message)
            self.context.raise_error(u'エラーが発生しました。もう一度選択してください。', HTTPInternalServerError)
        except Exception, e:
            logger.exception('save error (%s)' % e.message)
            self.context.raise_error(u'エラーが発生しました', HTTPInternalServerError)

    @view_config(route_name='orders.reserve.reselect', request_method='POST', renderer='json')
    def reserve_reselect(self):
        try:
            # release cart
            self.release_seats(self.context.performance.venue, self.context.seats_form.seats.data)
            api.remove_cart(self.request, release=True, async=False)
            return {}
        except Exception, e:
            logger.exception('save error (%s)' % e.message)
            self.context.raise_error(u'エラーが発生しました', HTTPInternalServerError)

    def electing_stock_check(self, performance_id):
        session = get_db_session(self.request, 'slave')
        if self.context.organization.id:
            from altair.app.ticketing.lots.models import Lot
            performance_lots = session.query(Lot) \
                .join(Event, Event.id == Lot.event_id) \
                .join(Performance, Event.id == Performance.event_id)\
                .filter(Event.organization_id == self.context.organization.id).filter(Performance.id == performance_id).all()
            if performance_lots:
                lot_ids = [Lot.id for Lot in performance_lots]
                electing = session.query(LotElectedEntry).join(LotEntry,
                                                               LotEntry.id == LotElectedEntry.lot_entry_id).filter(
                    LotElectedEntry.completed_at == None).filter(LotEntry.lot_id.in_(lot_ids)).first()
                if electing:
                    raise HTTPBadRequest(body=json.dumps({
                        'message': u'大規模当選処理(テスト版)を使用しています。在庫数確定がされていない抽選があります',
                    }))

@view_defaults(decorator=with_bootstrap, permission='sales_counter')
class OrdersEditAPIView(OrderBaseView):

    def _get_order_by_seat(self, performance_id, l0_id):
        logger.debug('call get order api (seat l0_id = %s)' % l0_id)
        return Order.filter_by(organization_id=self.context.organization.id)\
            .filter(Order.performance_id==performance_id)\
            .filter(Order.canceled_at==None)\
            .filter(Order.released_at==None)\
            .join(Order.items)\
            .join(OrderedProduct.elements)\
            .join(OrderedProductItem.seats)\
            .filter(Seat.l0_id==l0_id).first()

    def _get_order_dicts(self, order):
        return dict(
            id=order.id,
            order_no=order.order_no,
            performance_id=order.performance_id,
            sales_segment_id=order.sales_segment_id,
            transaction_fee=int(order.transaction_fee),
            delivery_fee=int(order.delivery_fee),
            system_fee=int(order.system_fee),
            special_fee=int(order.special_fee),
            total_amount=int(order.total_amount),
            point_amount=int(order.point_amount),
            payment_amount=int(order.payment_amount),
            special_fee_name=order.special_fee_name,
            ordered_products=[
            dict(
                id=op.id,
                price=int(op.price),
                quantity=op.quantity,
                sales_segment_id=op.product.sales_segment.id,
                sales_segment_name=op.product.sales_segment.name,
                product_id=op.product.id,
                product_name=op.product.name,
                stock_type_id=op.product.seat_stock_type_id,
                ordered_product_items=[
                dict(
                    id=opi.id,
                    quantity=opi.quantity,
                    product_item=dict(
                        id=long(opi.product_item.id),
                        name=opi.product_item.name,
                        price=int(opi.product_item.price),
                        quantity=opi.product_item.quantity,
                        stock_holder_name=opi.product_item.stock.stock_holder.name,
                        stock_type_id=opi.product_item.stock.stock_type_id,
                        is_seat=opi.product_item.stock.stock_type.is_seat,
                        quantity_only=opi.product_item.stock.stock_type.quantity_only,
                    ),
                    seats=[
                    dict(
                        id=seat.l0_id,
                        name=seat.name,
                        stock_type_id=seat.stock.stock_type_id
                    )
                    for seat in opi.seats
                    ],
                )
                for opi in op.elements
                ]
            )
            for op in order.items
            ]
        )

    def _validate_order_data(self):
        order_data = self.request.json_body
        logger.info('order data=%s' % order_data)

        order_id = order_data.get('id')
        order = get_order_by_id(self.request, order_id)
        if order is None or order.organization_id != self.context.organization.id:
            raise HTTPBadRequest(body=json.dumps(dict(message=u'予約データが見つかりません。既に更新されている可能性があります。')))

        if len(order.used_discount_codes) > 0:
            logger.info('order.used_discount_codes=%s' % order.used_discount_codes[0].code)
            raise HTTPBadRequest(body=json.dumps(dict(message=u'クーポン・割引コードの使用があるため、商品を変更できませんでした')))

        if not order.is_inner_channel:
            if order.payment_status != 'paid' or order.is_issued():
                logger.info('order.payment_status=%s, order.is_issued=%s' % (order.payment_status, order.is_issued()))
                raise HTTPBadRequest(body=json.dumps(dict(message=u'未決済または発券済みの予約は変更できません')))
            if order.total_amount < long(order_data.get('total_amount')):
                raise HTTPBadRequest(body=json.dumps(dict(message=u'決済金額が増額となる変更はできません')))

        if order.point_use_type is PointUseTypeEnum.AllUse \
                and order.total_amount > long(order_data.get('total_amount')):
            raise HTTPBadRequest(body=json.dumps(dict(message=u'全額ポイント払いの場合は決済金額が減額となる変更はできません')))
        if order.point_use_type is PointUseTypeEnum.PartialUse \
                and order.point_amount >= long(order_data.get('total_amount')):
            _msg = u'一部ポイント払いの場合、ご利用ポイント{}よりも合計金額を減額できません'.format(int(order.point_amount))
            raise HTTPBadRequest(body=json.dumps(dict(message=_msg)))

        payment_plugin_id = order.payment_delivery_pair.payment_method.payment_plugin_id
        if order.payment_status == 'paid' and \
                payment_plugin_id in (payments_plugins.SEJ_PAYMENT_PLUGIN_ID,
                                      payments_plugins.FAMIPORT_PAYMENT_PLUGIN_ID):
            raise HTTPBadRequest(body=json.dumps(dict(message=u'コンビニ決済で入金済みの場合は金額変更できません')))

        op_data = order_data.get('ordered_products')
        sales_segments = set()
        for i, op in enumerate(op_data):
            if (not op.get('id') and op.get('quantity') == 0) or not op.get('product_id'):
                op_data.pop(i)
                continue
            if op.get('quantity') > 0:
                sales_segments.add(long(op.get('sales_segment_id')))
        order_data['ordered_products'] = op_data
        logger.info('sales_segments=%s' % sales_segments)
        if len(sales_segments) > 1:
            raise HTTPBadRequest(body=json.dumps(dict(message=u'予約内の販売区分は同じでなければいけません')))
        logger.info('validate order data=%s' % order_data)

        return order_data

    @view_config(route_name='orders.api.get', renderer='json')
    def api_get(self):
        l0_id = self.request.params.get('l0_id', 0)
        performance_id = self.request.params.get('performance_id', 0)
        order = self._get_order_by_seat(performance_id, l0_id)
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

    @view_config(route_name='orders.api.get.html', renderer='altair.app.ticketing:templates/orders/_tiny_order.html')
    def api_get_html(self):
        l0_id = self.request.params.get('l0_id', 0)
        order_no = self.request.params.get('order_no')
        performance_id = self.request.params.get('performance_id', 0)
        order = None
        if l0_id:
            order = self._get_order_by_seat(performance_id, l0_id)
        elif order_no:
            order = Order.query.filter(Order.order_no==order_no, Order.organization_id==self.context.organization.id).first()
        if order is None:
            raise HTTPBadRequest(body=json.dumps({'message':u'予約がありません' }))
        elif order.performance_id != long(performance_id):
            self.request.session.flash(u'異なる公演の予約番号です')
        return {
            'order':order,
            'performance_id':performance_id,
            'options':dict(
                data_source=dict(
                    order_template_url='/static/tiny_order.html'
                    )
                )
            }

    @view_config(route_name='orders.api.performance', request_method='GET', renderer='json')
    def api_performance(self):
        performance_id = self.request.matchdict.get('performance_id', 0)
        performance = Performance.get(performance_id, self.context.organization.id)
        if performance is None:
            raise HTTPNotFound('performance id %d is not found' % performance_id)

        return dict(
            id=performance_id,
            sales_segments=[
            dict(
                id=ss.id,
                name=ss.name,
                products=[
                dict(
                    id=p.id,
                    name=p.name,
                    price=int(p.price),
                    stock_type_id=p.seat_stock_type_id,
                    stock_type_name=p.seat_stock_type.name,
                    quantity_only=p.seat_stock_type.quantity_only,
                    product_items=[
                    dict(
                        id=long(pi.id),
                        name=pi.name,
                        price=int(pi.price),
                        quantity=pi.quantity,
                        stock_holder_name=pi.stock.stock_holder.name,
                        stock_type_id=pi.stock.stock_type_id,
                        is_seat=pi.stock.stock_type.is_seat,
                        quantity_only=pi.stock.stock_type.quantity_only,
                    )
                    for pi in p.items
                    ]
                )
                for p in ss.products
                ]
            )
            for ss in performance.sales_segments
            ]
        )

    @view_config(route_name='orders.api.edit', request_method='GET', renderer='json')
    def api_edit_get(self):
        order_id = self.request.matchdict.get('order_id', 0)
        order = get_order_by_id(self.request, order_id)
        if order is None or order.organization_id != self.context.organization.id:
            raise HTTPNotFound('order id %s is not found' % order_id)
        if order.is_canceled():
            raise HTTPBadRequest(body=json.dumps(dict(message=u'既にキャンセルされています')))
        return self._get_order_dicts(order)

    @view_config(route_name='orders.api.edit_confirm', request_method='POST', renderer='json')
    def api_edit_confirm(self):
        order_data = self._validate_order_data()
        order_id = order_data.get('id')
        order = get_order_by_id(self.request, order_id)
        if order is None or order.organization_id != self.context.organization.id:
            raise HTTPNotFound('order id %s is not found' % order_id)
        prev_data = self._get_order_dicts(order)
        if order_data == prev_data:
            raise HTTPBadRequest(body=json.dumps(dict(message=u'変更がありません')))

        # 手数料を再計算して返す
        sales_segment = None
        products_for_get_amount = []
        products_for_fee_calculator = []
        order_data['special_fee_name'] = order.special_fee_name
        for op_data in order_data.get('ordered_products'):
            if sales_segment is None:
                sales_segment_id = op_data.get('sales_segment_id')
                sales_segment = SalesSegment.query.filter_by(id=sales_segment_id).first()
            product = Product.query.filter_by(id=op_data.get('product_id')).first()
            quantity = op_data.get('quantity')
            products_for_get_amount.append((product, product.price, quantity))
            products_for_fee_calculator.append((product, quantity))

        try:
            order_data['transaction_fee'] = int(sales_segment.get_transaction_fee(order.payment_delivery_pair, products_for_fee_calculator))
            order_data['delivery_fee'] = int(sales_segment.get_delivery_fee(order.payment_delivery_pair, products_for_fee_calculator))
            order_data['system_fee'] = int(sales_segment.get_system_fee(order.payment_delivery_pair, products_for_fee_calculator))
            order_data['special_fee'] = int(sales_segment.get_special_fee(order.payment_delivery_pair, products_for_fee_calculator))
            order_data['total_amount'] = int(sales_segment.get_amount(order.payment_delivery_pair, products_for_get_amount))
            order_data['payment_amount'] = order_data['total_amount'] - order_data['point_amount']
        except Exception:
            logger.exception('fee calculation error')
            raise HTTPBadRequest(body=json.dumps(dict(message=u'手数料計算できません。変更内容を確認してください。')))

        return order_data

    @view_config(route_name='orders.api.edit', request_method='POST', renderer='json')
    def api_edit_post(self):
        order_data = MultiDict(self._validate_order_data())
        order_id = order_data.get('id')
        order = get_order_by_id(self.request, order_id)
        if order is None or order.organization_id != self.context.organization.id:
            raise HTTPNotFound('order id %s is not found' % order_id)

        try:
            modiry_order, warnings = save_order_modification(self.request, order, order_data)
        except OrderCreationError as e:
            logger.warn(u'save error (%s)' % unicode(e))
            raise HTTPBadRequest(body=json.dumps(dict(message=unicode(e.message))))
        except Exception as e:
            logger.exception('save error (%s)' % e.message)
            raise HTTPBadRequest(body=json.dumps(dict(message=u'システムエラーが発生しました。')))

        self.request.session.flash(u'変更を保存しました')
        return self._get_order_dicts(modiry_order)


@view_defaults(decorator=with_bootstrap, permission="sales_counter", route_name="orders.mailinfo")
class MailInfoView(OrderBaseView):
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
        order = get_order_by_id(self.request, order_id)
        if order is None or order.organization_id != self.context.organization.id:
            return HTTPNotFound('order id %d is not found' % order_id)
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


@view_defaults(decorator=with_bootstrap, permission='order_viewer')
class CartView(BaseView):
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
            query = slave_session.query(Cart).filter(Cart.organization_id == organization_id, Cart.deleted_at.is_(None))
            try:
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

        return {'form_search': form, 'carts': carts, 'url': self.request.path}

    @view_config(route_name='cart.show', renderer="altair.app.ticketing:templates/carts/show.html")
    def show(self):
        slave_session = get_db_session(self.request, name="slave")

        organization_id = self.context.organization.id
        order_no = self.request.matchdict['order_no']
        try:
            cart = slave_session.query(Cart) \
                .filter(Cart.organization_id == organization_id) \
                .filter(Cart.deleted_at.is_(None)) \
                .filter(Cart.order_no == order_no).one()
        except NoResultFound:
            return HTTPNotFound('cart (order_no=%s) not found' % order_no)
        multicheckout_records = []
        multicheckout_api = get_multicheckout_3d_api(self.request,
                                                     self.context.organization.setting.multicheckout_shop_name)
        standard_info, secure3d_info = multicheckout_api.get_transaction_info(order_no)
        for standard_info_rec in standard_info:
            standard_info_rec['status_description'] = get_multicheckout_status_description(standard_info_rec['status'])
            standard_info_rec['message'] = u'%s / %s' % (
                    get_multicheckout_error_message(standard_info_rec['error_cd']),
                    get_multicheckout_card_error_message(standard_info_rec['card_error_cd']),
                    )
            standard_info_rec['secure3d_ret_cd'] = None
            multicheckout_records.append(standard_info_rec)

        for secure3d_info_rec in secure3d_info:
            secure3d_info_rec['status'] = None
            secure3d_info_rec['approval_no'] = None
            secure3d_info_rec['ahead_com_cd'] = None
            secure3d_info_rec['card_error_cd'] = None
            secure3d_info_rec['card_no'] = None
            secure3d_info_rec['card_limit'] = None
            secure3d_info_rec['secure_kind'] = None
            secure3d_info_rec['card_brand'] = None
            secure3d_info_rec['status_description'] = None
            secure3d_info_rec['message'] = get_multicheckout_error_message(secure3d_info_rec['error_cd'])
            multicheckout_records.append(secure3d_info_rec)

        checkout_records = []  # 楽天Payの注文番号をオーダー番号から取得する。
        if cart.payment_delivery_pair and \
                cart.payment_delivery_pair.payment_method.payment_plugin_id == CHECKOUT_PAYMENT_PLUGIN_ID:
            checkout_records.extend(slave_session.query(Checkout).filter(Checkout.orderCartId == cart.order_no)
                                    .filter(Checkout.orderId.isnot(None)))

        pgw_info = get_pgw_info(cart)
        pgw_records = []
        pgw_transaction_records = PGWResponseLog.get_pgw_response_log(order_no)
        for pgw_transaction_rec in pgw_transaction_records:
            comm_cd = pgw_transaction_rec.card_comm_error_code
            detail_cd = pgw_transaction_rec.card_detail_error_code
            pgw_transaction = {
                'status': pgw_api.get_pgw_status(
                    pgw_transaction_rec.transaction_status,
                    pgw_transaction_rec.transaction_type),
                'ahead_com_cd': pgw_info.get('ahead_com_cd'),
                'error_cd': comm_cd,
                'card_error_cd': detail_cd,
                'message': pgw_api.get_pgw_status_message(comm_cd, detail_cd)
            }
            pgw_records.append(pgw_transaction)

        return {
            'cart': cart,
            'multicheckout_records': multicheckout_records,
            'checkout_records': checkout_records,
            'pgw_records': pgw_records
        }


def verify_orion_ticket_phone(data):
    errors = []
    for phone in data:
        phone = phone.strip()
        error = u''
        if phone:
            if len(phone) != 11:
                error = u'電話番号の桁数が11桁ではありません'
            if not phone.isdigit():
                error = ', '.join([error, u'数字以外の文字は入力できません']) if error else u'数字以外の文字は入力できません'
            if not re.match('^(070|080|090)', phone):
                error = ', '.join([error, u'[070,080,090]で始まる携帯電話番号を入力してください']) if error else u'[070,080,090]で始まる携帯電話番号を入力してください'
            errors.append(error)

    return errors
