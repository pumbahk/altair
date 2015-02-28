# -*- coding:utf-8 -*-
import logging
import re
import json
import transaction
import time
from datetime import datetime, timedelta
from urlparse import urlparse

import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from markupsafe import Markup
from zope.interface import provider, implementer

from pyramid.httpexceptions import HTTPNotFound, HTTPFound, HTTPBadRequest, HTTPMovedPermanently
from pyramid.response import Response
from pyramid.view import view_defaults, view_config
from pyramid.threadlocal import get_current_request
from webob.multidict import MultiDict

from altair.pyramid_boto.s3.assets import IS3KeyProvider
from altair.request.adapters import UnicodeMultiDictAdapter

from altair.mobile.api import is_mobile_request
from altair.pyramid_dynamic_renderer import lbr_view_config

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.core import api as c_api
from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.mailmags.api import get_magazines_to_subscribe, multi_subscribe
from altair.app.ticketing.views import mobile_request
from altair.app.ticketing.fanstatic import with_jquery, with_jquery_tools
from altair.app.ticketing.payments.api import set_confirm_url, lookup_plugin
from altair.app.ticketing.payments.payment import Payment
from altair.app.ticketing.payments.exceptions import OrderLikeValidationFailure
from altair.app.ticketing.users.models import UserPointAccountTypeEnum
from altair.app.ticketing.venues.api import get_venue_site_adapter
from altair.mobile.interfaces import IMobileRequest
from altair.sqlahelper import get_db_session
from altair.app.ticketing.temp_store import TemporaryStoreError

from . import api
from . import helpers as h
from . import schemas
from .api import set_rendered_event, is_smartphone, is_point_input_required, is_fc_auth_organization, enable_auto_input_form
from altair.mobile.api import set_we_need_pc_access, set_we_invalidate_pc_access
from .events import notify_order_completed
from .reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from .stocker import InvalidProductSelectionException, NotEnoughStockException
from .rendering import selectable_renderer
from .view_support import (
    IndexViewMixin,
    get_amount_without_pdmp,
    get_seat_type_dicts,
    assert_quantity_within_bounds,
    build_dynamic_form,
    get_extra_form_data_pair_pairs,
    back,
    back_to_top,
    gzip_preferred,
    is_booster_or_fc_cart_pred,
    render_view_to_response_with_derived_request,
    coerce_extra_form_data,
    )
from .exceptions import (
    NoSalesSegment,
    NoCartError, 
    NoPerformanceError,
    InvalidCSRFTokenException, 
    CartCreationException,
    InvalidCartStatusError,
    PaymentMethodEmptyError,
    OutTermSalesException,
    TooManyCartsCreated,
    PaymentError,
    QuantityOutOfBoundsError,
    ProductQuantityOutOfBoundsError,
    PerStockTypeQuantityOutOfBoundsError,
    PerStockTypeProductQuantityOutOfBoundsError,
    PerProductProductQuantityOutOfBoundsError,
    CompletionPageNotRenderered,
)
from .resources import EventOrientedTicketingCartResource, PerformanceOrientedTicketingCartResource, CompleteViewTicketingCartResource
from .limiting import LimiterDecorators
from . import flow
from .interfaces import IPageFlowPredicate, IPageFlowAction

logger = logging.getLogger(__name__)

limiter = LimiterDecorators('altair.cart.limit_per_unit_time', TooManyCartsCreated)

def back_to_product_list_for_mobile(request):
    cart = api.get_cart_safe(request)
    api.remove_cart(request)
    return HTTPFound(
        request.route_url(
            route_name='cart.products',
            event_id=cart.performance.event_id,
            performance_id=cart.performance_id,
            sales_segment_id=cart.sales_segment_id,
            seat_type_id=cart.items[0].product.items[0].stock.stock_type_id))

@provider(IPageFlowPredicate)
def flow_predicate_extra_form(pe, flow_context, context, request):
    return bool(context.sales_segment.setting.extra_form_fields)

@provider(IPageFlowPredicate)
def flow_predicate_point_input_required(pe, flow_context, context, request):
    return is_point_input_required(context, request)

@provider(IPageFlowPredicate)
def flow_predicate_prepared(pe, flow_context, context, request):
    return flow_context['prepared']

@provider(IPageFlowPredicate)
def flow_predicate_non_booster_cart(pe, flow_context, context, request):
    return not is_booster_or_fc_cart_pred(context, request)

@implementer(flow.IPageFlowAction)
class PaymentAction(flow.PageFlowActionBase):
    def __call__(self, flow_context, context, request):
        response = Payment(context.cart, request).call_prepare()
        if response is not None:
            assert isinstance(response, HTTPFound)
            flow_context['prepared'] = True 
            return flow.Transition(context, request, url_or_path=response.location)
        else:
            flow_context['prepared'] = True 


# 画面フローの定義
flow_graph = flow.PageFlowGraph(
    flow_context_factory=lambda context, request: { 'prepared': False },
    actions=[
        # 購入者情報 => ポイント入力
        flow.SimpleTransitionAction(
            # 遷移条件
            predicates=[
                flow.RouteIs('cart.payment'),
                flow.Not(flow_predicate_extra_form),
                flow_predicate_point_input_required,
                ],
            route_name='cart.point'
            ),
        # 追加情報入力 => ポイント入力
        flow.SimpleTransitionAction(
            # 遷移条件
            predicates=[
                flow.RouteIs('cart.extra_form'),
                flow_predicate_point_input_required,
                ],
            route_name='cart.point'
            ),
        # 購入者情報 => 追加情報入力
        flow.SimpleTransitionAction(
            # 遷移条件
            predicates=[
                flow.RouteIs('cart.payment'),
                flow_predicate_extra_form,
                flow_predicate_non_booster_cart,
                ],
            route_name='cart.extra_form'
            ),
        # 購入者情報 => 決済情報入力
        PaymentAction(
            # 遷移条件
            predicates=[
                flow.RouteIs('cart.payment'),
                flow.Not(flow_predicate_prepared),
                flow.Not(flow_predicate_point_input_required),
                flow.Not(flow_predicate_extra_form),
                ]
            ),
        # ポイント入力 => 決済情報入力
        PaymentAction(
            # 遷移条件
            predicates=[
                flow.RouteIs('cart.point'),
                flow.Not(flow_predicate_prepared),
                flow_predicate_point_input_required,
                ]
            ),
        # 追加情報入力 => 決済情報入力
        PaymentAction(
            # 遷移条件
            predicates=[
                flow.RouteIs('cart.extra_form'),
                flow.Not(flow_predicate_prepared),
                flow.Not(flow_predicate_point_input_required),
                ]
            ),
        # 決済情報入力 => 確認画面
        flow.SimpleTransitionAction(
            # 遷移条件
            predicates=[
                flow_predicate_prepared,
                ],
            route_name='payment.confirm'
            ),
        ]
    )

@view_defaults(
    route_name='cart.agreement',
    decorator=(with_jquery + with_jquery_tools).not_when(mobile_request), 
    renderer=selectable_renderer("agreement.html"),
    xhr=False, permission="buy")
class PerEventAgreementView(IndexViewMixin):
    """ 規約表示画面 """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(request_method="GET")
    def get(self):
        sales_segments = self.context.available_sales_segments
        performance_id = self.request.GET.get('pid') or self.request.GET.get('performance')
        selected_sales_segment = None
        if not performance_id:
            # GETパラメータ指定がなければ、選択肢の1つ目を採用
            selected_sales_segment = sales_segments[0]
        else:
            # パフォーマンスIDから販売区分の解決を試みる
            # performance_id で指定される Performance は
            # available_sales_segments に関連するものでなければならない

            # 数が少ないのでリニアサーチ
            for sales_segment in sales_segments:
                if sales_segment.performance.id == performance_id:
                    # 複数個の SalesSegment が該当する可能性があるが
                    # 最初の 1 つを採用することにする。実用上問題ない。
                    selected_sales_segment = sales_segment
                    break
            else:
                # 該当する物がないので、デフォルト (選択肢の1つ目)
                selected_sales_segment = sales_segments[0]

        if not selected_sales_segment.setting.disp_agreement:
            return HTTPFound(self.request.route_url('cart.index', event_id=self.context.event.id, _query=self.request.GET))
        return dict(agreement_body=Markup(selected_sales_segment.setting.agreement_body))

    @lbr_view_config(request_method="POST")
    def post(self):
        agree = self.request.params.get('agree')
        if not agree:
            self.request.session.flash(u"注意事項を確認、同意し、公演に申し込んでください。")
            return HTTPFound(self.request.current_route_path(_query=self.request.GET))
        else:
            return HTTPFound(self.request.route_url('cart.index', event_id=self.context.event.id, _query=self.request.GET))


@view_defaults(
    route_name='cart.agreement2',
    decorator=(with_jquery + with_jquery_tools).not_when(mobile_request),
    renderer=selectable_renderer("agreement.html"),
    xhr=False, permission="buy")
class PerPerformanceAgreementView(object):
    """ 規約表示画面 """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(request_method="GET")
    def get(self):
        sales_segments = self.context.available_sales_segments
        selected_sales_segment = sales_segments[0]
        if not selected_sales_segment.setting.disp_agreement:
            return HTTPFound(performance_id and self.request.route_url('cart.index2', performance_id=self.context.performance.id, _query=self.request.GET))
        return dict(agreement_body=Markup(selected_sales_segment.setting.agreement_body))

    @lbr_view_config(request_method="POST")
    def post(self):
        agree = self.request.params.get('agree')
        if not agree:
            self.request.session.flash(u"注意事項を確認、同意し、公演に申し込んでください。")
            return HTTPFound(self.request.current_route_path(_query=self.request.GET))
        else:
            return HTTPFound(self.request.route_url('cart.index2', performance_id=self.context.performance.id, _query=self.request.GET))


@view_defaults(xhr=False, permission="buy")
class CompatAgreementView(object):
    """ 規約表示画面 """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(request_method="GET", route_name='cart.agreement.compat')
    def get_agreement(self):
        return HTTPMovedPermanently(self.request.route_path('cart.agreement', _query=self.request.GET, **self.request.matchdict))

    @lbr_view_config(request_method="POST", route_name='cart.agreement.compat')
    def post_agreement(self):
        return PerEventAgreementView(self.request).post()

    @lbr_view_config(request_method="GET", route_name='cart.agreement2.compat')
    def get_agreement2(self):
        return HTTPMovedPermanently(self.request.route_path('cart.agreement2', _query=self.request.GET, **self.request.matchdict))

    @lbr_view_config(request_method="POST", route_name='cart.agreement2.compat')
    def post_agreement2(self):
        return PerPerformanceAgreementView(self.request).post()


@view_defaults(decorator=(with_jquery + with_jquery_tools).not_when(mobile_request), xhr=False, permission="buy")
class IndexView(IndexViewMixin):
    """ 座席選択画面 """
    def __init__(self, context, request):
        IndexViewMixin.__init__(self)
        self.context = context
        self.request = request
        self.prepare()

    @lbr_view_config(route_name='cart.index',
                 renderer=selectable_renderer("index.html"))
    @lbr_view_config(route_name='cart.index',
                 request_type="altair.mobile.interfaces.ISmartphoneRequest", 
                 renderer=selectable_renderer("index.html"))
    def event_based_landing_page(self):
        # 会場
        try:
            performance_id = long(self.request.params.get('pid') or self.request.params.get('performance'))
        except (ValueError, TypeError):
            performance_id = None

        sales_segments = self.context.available_sales_segments
        selector_name = self.context.event.performance_selector

        performance_selector = api.get_performance_selector(self.request, selector_name)
        sales_segments_selection = performance_selector()
        #logger.debug("sales_segments: %s" % sales_segments_selection)

        selected_sales_segment = None
        preferred_performance = None
        if not performance_id:
            # GETパラメータ指定がなければ、選択肢の1つ目を採用
            selected_sales_segment = sales_segments[0]
        else:
            # パフォーマンスIDから販売区分の解決を試みる
            # performance_id で指定される Performance は
            # available_sales_segments に関連するものでなければならない

            # 数が少ないのでリニアサーチ
            for sales_segment in sales_segments:
                if sales_segment.performance.id == performance_id:
                    # 複数個の SalesSegment が該当する可能性があるが
                    # 最初の 1 つを採用することにする。実用上問題ない。
                    selected_sales_segment = sales_segment
                    break
            else:
                # 該当する物がないので、デフォルト (選択肢の1つ目)
                selected_sales_segment = sales_segments[0]
                preferred_performance = c_models.Performance.query.filter_by(id=performance_id, public=True).first()
                if preferred_performance is not None:
                    if preferred_performance.event_id != self.context.event.id:
                        preferred_performance = None 

        set_rendered_event(self.request, self.context.event)

        return dict(
            event=dict(
                id=self.context.event.id,
                code=self.context.event.code,
                title=self.context.event.title,
                abbreviated_title=self.context.event.abbreviated_title,
                sales_start_on=str(self.context.event.sales_start_on),
                sales_end_on=str(self.context.event.sales_end_on),
                venues=set(p.venue.name for p in self.context.event.performances),
                product=self.context.event.products
                ),
            dates=sorted(list(set([p.start_on.strftime("%Y-%m-%d %H:%M") for p in self.context.event.performances]))),
            cart_release_url=self.request.route_url('cart.release'),
            selected=Markup(
                json.dumps([
                    performance_selector.select_value(selected_sales_segment),
                    selected_sales_segment.id])),
            sales_segments_selection=Markup(json.dumps(sales_segments_selection)),
            event_extra_info=self.event_extra_info.get("event") or [],
            selection_label=performance_selector.label,
            second_selection_label=performance_selector.second_label,
            preferred_performance=preferred_performance,
            performance=performance_id
            )

    # パフォーマンスベースのランディング画面
    @lbr_view_config(route_name='cart.index2',
                 renderer=selectable_renderer("index.html"))
    @lbr_view_config(route_name='cart.index2',
                 request_type="altair.mobile.interfaces.ISmartphoneRequest", 
                 renderer=selectable_renderer("index.html"))
    def performance_based_landing_page(self):
        sales_segments = self.context.available_sales_segments
        selector_name = self.context.event.performance_selector

        performance_selector = api.get_performance_selector(self.request, selector_name)
        sales_segments_selection = performance_selector()
        #logger.debug("sales_segments: %s" % sales_segments_selection)

        set_rendered_event(self.request, self.context.event)

        selected_sales_segment = sales_segments[0]

        return dict(
            event=dict(
                id=self.context.event.id,
                code=self.context.event.code,
                title=self.context.event.title,
                abbreviated_title=self.context.event.abbreviated_title,
                sales_start_on=str(self.context.event.sales_start_on),
                sales_end_on=str(self.context.event.sales_end_on),
                venues=set(p.venue.name for p in self.context.event.performances),
                product=self.context.event.products
                ),
            dates=sorted(list(set([p.start_on.strftime("%Y-%m-%d %H:%M") for p in self.context.event.performances]))),
            cart_release_url=self.request.route_url('cart.release'),
            selected=Markup(
                json.dumps([
                    performance_selector.select_value(selected_sales_segment),
                    selected_sales_segment.id])),
            sales_segments_selection=Markup(json.dumps(sales_segments_selection)),
            event_extra_info=self.event_extra_info.get("event") or [],
            selection_label=performance_selector.label,
            second_selection_label=performance_selector.second_label,
            preferred_performance=None
            )


@view_defaults(xhr=True, permission="buy", renderer="json")
class IndexAjaxView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_frontend_drawing_urls(self, venue):
        sales_segment = self.context.sales_segment
        retval = {}
        drawings = get_venue_site_adapter(self.request, venue.site).get_frontend_drawings()
        if drawings:
            for name, drawing in drawings.items():
                if IS3KeyProvider.providedBy(drawing):
                    key = drawing.get_key()
                    headers = {}
                    if re.match('^.+\.(svgz|gz)$', drawing.path):
                        headers['response-content-encoding'] = 'gzip'
                    cache_minutes = 30
                    expire_date = datetime.now() + timedelta(minutes=cache_minutes)
                    expire_date = expire_date.replace(minute=(expire_date.minute/cache_minutes*cache_minutes), second=0)
                    expire_epoch = time.mktime(expire_date.timetuple())
                    url = key.generate_url(expires_in=expire_epoch, expires_in_absolute=True, response_headers=headers)
                else:
                    url = self.request.route_url(
                        'cart.venue_drawing',
                        event_id=self.context.event.id,
                        performance_id=sales_segment.performance.id,
                        venue_id=sales_segment.performance.venue.id,
                        part=name)
                retval[name] = url
        return retval

    @lbr_view_config(route_name='cart.seat_types2')
    def get_seat_types(self):
        sales_segment = self.context.sales_segment # XXX: matchdict から取得していることを期待

        order_separate_seats_url = u''
        organization = api.get_organization(self.request)
        if organization.setting.entrust_separate_seats:
            qs = {'separate_seats': 'true'}
            order_separate_seats_url = self.request.route_url('cart.order', sales_segment_id=sales_segment.id, _query=qs)

        seat_type_dicts = get_seat_type_dicts(self.request, sales_segment)

        data = dict(
            seat_types=[
                dict(
                    products_url=self.request.route_url(
                        'cart.products2',
                        event_id=self.context.event.id,
                        performance_id=sales_segment.performance.id,
                        sales_segment_id=sales_segment.id,
                        seat_type_id=_dict['id']),
                    seats_url=self.request.route_url(
                        'cart.seats',
                        performance_id=sales_segment.performance_id,
                        sales_segment_id=sales_segment.id,
                        _query=dict(seat_type_id=_dict['id'])
                        ),
                    seats_url2=self.request.route_url(
                        'cart.seats',
                        performance_id=sales_segment.performance_id,
                        sales_segment_id=sales_segment.id,
                        _query=dict(stock_id='__stock_id__')
                        ),
                    **_dict
                    )
                for _dict in seat_type_dicts
                ],
            event_name=sales_segment.performance.event.title,
            performance_name=sales_segment.performance.name,
            performance_start=h.performance_date(sales_segment.performance),
            performance_id=sales_segment.performance.id,
            sales_segment_id=sales_segment.id,
            order_url=self.request.route_url("cart.order", sales_segment_id=sales_segment.id),
            order_separate_seats_url=order_separate_seats_url,
            venue_name=sales_segment.performance.venue.name,
            event_id=self.context.event.id,
            venue_id=sales_segment.performance.venue.id,
            data_source=dict(
                venue_drawing=self.request.route_url(
                    'cart.venue_drawing',
                    event_id=self.context.event.id,
                    performance_id=sales_segment.performance.id,
                    venue_id=sales_segment.performance.venue.id,
                    part='__part__'),
                venue_drawings=self.get_frontend_drawing_urls(sales_segment.performance.venue),
                info=self.request.route_url(
                    'cart.info',
                    performance_id=sales_segment.performance_id,
                    sales_segment_id=sales_segment.id,
                    ),
                seats=self.request.route_url(
                    'cart.seats',
                    performance_id=sales_segment.performance_id,
                    sales_segment_id=sales_segment.id,
                    ),
                seat_adjacencies=self.request.application_url \
                    + api.get_route_pattern(
                      self.request.registry,
                      'cart.seat_adjacencies')
                )
            )
        return data

    @lbr_view_config(route_name='cart.products')
    @lbr_view_config(route_name='cart.products2')
    def get_products(self):
        """ 席種別ごとの購入単位
        SeatType -> ProductItem -> Product
        """
        seat_type_id = long(self.request.matchdict['seat_type_id'])
        product_dicts = get_seat_type_dicts(self.request, self.context.sales_segment, seat_type_id)[0]['products']
        return dict(products=product_dicts)

    @lbr_view_config(route_name='cart.info', renderer="json")
    def get_info(self):
        """会場情報"""
        venue = self.context.performance.venue

        self.request.add_response_callback(gzip_preferred)
        slave_session = get_db_session(self.request, name="slave")

        return dict(
            areas=dict(
                (area.id, { 'id': area.id, 'name': area.name })\
                for area in slave_session.query(c_models.VenueArea) \
                            .join(c_models.VenueArea_group_l0_id) \
                            .filter(c_models.VenueArea_group_l0_id.venue_id==venue.id)
                ),
            info=dict(
                available_adjacencies=[
                    adjacency_set.seat_count
                    for adjacency_set in\
                        slave_session.query(c_models.SeatAdjacencySet) \
                        .filter_by(site_id=venue.site_id)
                    ]
                ),
            pages=get_venue_site_adapter(self.request, venue.site).get_frontend_pages()
            )

    @lbr_view_config(route_name='cart.seats')
    def get_seats(self):
        """会場&座席情報"""
        venue = self.context.performance.venue
        stock_type_id = self.request.params.get('seat_type_id')
        stock_id = self.request.params.get('stock_id')

        if stock_type_id is not None and stock_id is not None:
            raise HTTPBadRequest()

        slave_session = get_db_session(self.request, name="slave")
        sales_segment = slave_session.query(c_models.SalesSegment).filter(c_models.SalesSegment.id==self.context.sales_segment.id).one()
        sales_stocks = sales_segment.stocks
        seats_query = None
        if sales_segment.seat_choice:
            seats_query = c_models.Seat.query_sales_seats(sales_segment, slave_session)\
                .options(joinedload('areas'), joinedload('status_'))\
                .join(c_models.SeatStatus)\
                .join(c_models.Stock)\
                .filter(c_models.Seat.venue_id==venue.id)\
                .filter(c_models.SeatStatus.status==int(c_models.SeatStatusEnum.Vacant))
            seat_groups_queries = [
                slave_session.query(c_models.SeatGroup.l0_id, c_models.SeatGroup.name, c_models.Seat.l0_id, include_deleted=True) \
                    .join(c_models.Seat, c_models.SeatGroup.l0_id == l0_id_column) \
                    .join(c_models.Stock, c_models.Seat.stock_id == c_models.Stock.id) \
                    .filter(c_models.SeatGroup.site_id == venue.site_id) \
                    .filter(c_models.Seat.venue_id == venue.id) \
                    .filter(c_models.Stock.deleted_at == None) \
                    for l0_id_column in [c_models.Seat.row_l0_id, c_models.Seat.group_l0_id]
                    ]
            if stock_id is not None:
                stock_id_list = stock_id.split(',')
                seats_query = seats_query.filter(c_models.Stock.id.in_(stock_id_list))
                seat_groups_queries = [
                    seat_groups_query.filter(c_models.Stock.id.in_(stock_id_list))
                    for seat_groups_query in seat_groups_queries
                    ]
            elif stock_type_id is not None:
                seats_query = seats_query.filter(c_models.Stock.stock_type_id == stock_type_id)
                seat_groups_queries = [
                    seat_groups_query.filter(c_models.Stock.stock_type_id == stock_type_id) 
                    for seat_groups_query in seat_groups_queries
                    ]
            seats = seats_query.all()
            seat_groups = {}
            for seat_group_l0_id, seat_group_name, seat_l0_id in seat_groups_queries[0].union_all(*seat_groups_queries[1:]):
                seat_group = seat_groups.get(seat_group_l0_id)
                if seat_group is None:
                    seat_group = seat_groups[seat_group_l0_id] = {
                        'name': seat_group_name,
                        'seats': [],
                        }
                seat_group['seats'].append(seat_l0_id) 
        else:
            seats = []
            seat_groups = {}

        stock_map = dict([(s.id, s) for s in sales_stocks])

        self.request.add_response_callback(gzip_preferred)
                

        return dict(
            seats=dict(
                (
                    seat.l0_id,
                    dict(
                        id=seat.l0_id,
                        stock_type_id=stock_map[seat.stock_id].stock_type_id,
                        stock_holder_id=stock_map[seat.stock_id].stock_holder_id,
                        status=seat.status,
                        areas=[area.id for area in seat.areas],
                        is_hold=seat.stock_id in stock_map,
                        )
                    )
                for seat in seats),
            seat_groups=seat_groups
            )

    @lbr_view_config(route_name='cart.seat_adjacencies')
    def get_seat_adjacencies(self):
        """連席情報"""
        try:
            venue_id = long(self.request.matchdict.get('venue_id'))
        except (ValueError, TypeError):
            venue_id = None

        if venue_id is None:
            raise HTTPNotFound()

        venue = DBSession.query(c_models.Venue).filter_by(id=venue_id).one()
        length_or_range = self.request.matchdict['length_or_range']
        return dict(
            seat_adjacencies={
                length_or_range: [
                    [seat.l0_id for seat in seat_adjacency.seats_filter_by_venue(venue_id)]
                    for seat_adjacency_set in \
                        DBSession.query(c_models.SeatAdjacencySet)\
                            .filter_by(site_id=venue.site_id, seat_count=length_or_range)
                    for seat_adjacency in seat_adjacency_set.adjacencies
                    ]
                }
            )

    @lbr_view_config(route_name="cart.venue_drawing", request_method="GET")
    def get_venue_drawing(self):
        try:
            venue_id = long(self.request.matchdict.get('venue_id'))
        except (ValueError, TypeError):
            venue_id = None

        part = self.request.matchdict.get('part')
        venue = c_models.Venue.get(venue_id)
        drawing = get_venue_site_adapter(self.request, venue.site).get_frontend_drawing(part)
        if not drawing:
            raise HTTPNotFound()
        content_encoding = None
        if re.match('^.+\.(svgz|gz)$', drawing.path):
            content_encoding = 'gzip'
        resp = Response(body=drawing.stream().read(), content_type='text/xml; charset=utf-8', content_encoding=content_encoding)
        if resp.content_encoding is None:
            resp.encode_content()
        return resp


@view_defaults(permission="buy", renderer="json")
class ReserveView(object):
    """ 座席選択完了画面(おまかせ) """

    product_id_regex = re.compile(r'product-(?P<product_id>\d+)')

    def __init__(self, context, request):
        self.context = context
        self.request = request


    def iter_ordered_items(self):
        for key, value in self.request.params.iteritems():
            m = self.product_id_regex.match(key)
            if m is None:
                continue
            quantity = int(value)
            logger.debug("key = %s, value = %s" % (key, value))
            if quantity == 0:
                continue
            yield m.groupdict()['product_id'], quantity

    @property
    def ordered_items(self):
        """ リクエストパラメータから(プロダクトID,数量)タプルのリストを作成する
        :return: list of tuple(altair.app.ticketing.products.models.Product, int)
        """

        controls = list(self.iter_ordered_items())
        logger.debug('order %s' % controls)
        if len(controls) == 0:
            return []

        products = dict(
            (p.id, p)
            for p in DBSession.query(c_models.Product) \
                    .options(joinedload(c_models.Product.seat_stock_type)) \
                    .filter(c_models.Product.id.in_([c[0] for c in controls]))
            )
        logger.debug('order %s' % products)

        return [(products.get(int(c[0])), c[1]) for c in controls]


    @limiter.acquire
    @lbr_view_config(route_name='cart.order', request_method="POST")
    def reserve(self):
        h.form_log(self.request, "received order")
        ordered_items = self.ordered_items
        if not ordered_items:
            return dict(result='NG', reason="no products")

        selected_seats = self.request.params.getall('selected_seat')
        separate_seats = True if self.request.params.get('separate_seats') == 'true' else False
        logger.debug('ordered_items %s' % ordered_items)

        sales_segment = self.context.sales_segment
        if not sales_segment.in_term(self.context.now):
            transaction.abort()
            logger.debug("out of term")
            return dict(result='NG', reason="out_of_term")

        try:
            assert_quantity_within_bounds(sales_segment, ordered_items)
            cart = api.order_products(
                self.request,
                sales_segment,
                ordered_items,
                selected_seats=selected_seats,
                separate_seats=separate_seats)
            cart.sales_segment = sales_segment
            if cart is None:
                transaction.abort()
                return dict(result='NG')
        except QuantityOutOfBoundsError as e:
            transaction.abort()
            logger.debug("quantity limit")
            if e.min_quantity is not None and e.quantity_given < e.min_quantity:
                return dict(
                    result='NG',
                    reason="ticket_count_below_lower_bound",
                    message="枚数は合計{.min_quantity}以上で選択してください".format(e)
                    )
            else:
                return dict(
                    result='NG',
                    reason="ticket_count_over_upper_bound",
                    message="枚数は合計{.max_quantity}以内で選択してください".format(e)
                    )
        except ProductQuantityOutOfBoundsError as e:
            transaction.abort()
            logger.debug("product limit")
            if e.min_quantity is not None and e.quantity_given < e.min_quantity:
                return dict(
                    result='NG',
                    reason="product_count_below_lower_bound",
                    message="商品個数は合計{.min_quantity}以上で選択してください".format(e)
                    )
            else:
                return dict(
                    result='NG',
                    reason="product_count_over_upper_bound",
                    message="商品個数は合計{.max_quantity}以内で選択してください".format(e)
                    )
        except PerStockTypeQuantityOutOfBoundsError as e:
            transaction.abort()
            logger.debug("per-stock-type quantity limit")
            if e.min_quantity is not None and e.quantity_given < e.min_quantity:
                return dict(
                    result='NG',
                    reason="ticket_count_below_lower_bound",
                    message="枚数は合計{.min_quantity}以上で選択してください".format(e)
                    )
            else:
                return dict(
                    result='NG',
                    reason="ticket_count_over_upper_bound",
                    message="枚数は合計{.max_quantity}以内で選択してください".format(e)
                    )
        except (PerStockTypeProductQuantityOutOfBoundsError, PerProductProductQuantityOutOfBoundsError) as e:
            transaction.abort()
            logger.debug("per-stock-type product limit")
            if e.min_quantity is not None and e.quantity_given < e.min_quantity:
                return dict(
                    result='NG',
                    reason="product_count_below_lower_bound",
                    message="商品個数は合計{.min_quantity}以上で選択してください".format(e)
                    )
            else:
                return dict(
                    result='NG',
                    reason="product_count_over_upper_bound",
                    message="商品個数は合計{.max_quantity}以内で選択してください".format(e)
                    )
        except NotEnoughAdjacencyException:
            transaction.abort()
            logger.debug("not enough adjacency")
            return dict(result='NG', reason="adjacency")
        except InvalidSeatSelectionException:
            transaction.abort()
            logger.debug("seat selection is invalid.")
            return dict(result='NG', reason="invalid seats")
        except InvalidProductSelectionException:
            transaction.abort()
            logger.debug("product selection is invalid.")
            return dict(result='NG', reason="invalid products")
        except NotEnoughStockException:
            transaction.abort()
            logger.debug("not enough stock quantity.")
            return dict(result='NG', reason="stock")
        except CartCreationException:
            transaction.abort()
            logger.debug("cannot create cart.")
            return dict(result='NG', reason="unknown")

        DBSession.add(cart)
        DBSession.flush()
        api.set_cart(self.request, cart)
        return dict(result='OK', 
                    payment_url=self.request.route_url("cart.payment", sales_segment_id=sales_segment.id),
                    cart=dict(products=[dict(name=p.product.name, 
                                             quantity=p.quantity,
                                             price=int(p.product.price),
                                             seats=p.seats if sales_segment.setting.display_seat_no else [],
                                             unit_template=h.build_unit_template(p.product.items),
                                        )
                                        for p in cart.items],
                              total_amount=h.format_number(get_amount_without_pdmp(cart)),
                              separate_seats=separate_seats
                             )
                    )



@view_defaults(decorator=with_jquery.not_when(mobile_request))
class ReleaseCartView(object):
    def __init__(self, request):
        self.request = request

    @limiter.release
    @lbr_view_config(route_name='cart.release', request_method="POST", renderer="json")
    def __call__(self):
        api.remove_cart(self.request)
        return dict()


@view_defaults(route_name='cart.payment', decorator=with_jquery.not_when(mobile_request), renderer=selectable_renderer("payment.html"), permission="buy")
class PaymentView(object):
    """ 支払い方法、引き取り方法選択 """

    class ValidationFailed(Exception):
        pass

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_payment_delivery_method_pairs(self, sales_segment):
        return [
            pdmp
            for pdmp in self.context.available_payment_delivery_method_pairs(sales_segment)
            if pdmp.payment_method.public
            ]

    @lbr_view_config(request_method="GET")
    def get(self):
        """ 支払い方法、引き取り方法選択
        """
        start_on = self.context.cart.performance.start_on
        sales_segment = self.context.sales_segment
        cart = self.context.read_only_cart
        payment_delivery_methods = self.get_payment_delivery_method_pairs(sales_segment)
        payment_delivery_methods = [
            payment_delivery_pair
            for payment_delivery_pair in payment_delivery_methods
            if api.check_if_payment_delivery_method_pair_is_applicable(
                self.request, 
                cart,
                payment_delivery_pair
                )
            ]
        if 0 == len(payment_delivery_methods):
            raise PaymentMethodEmptyError.from_resource(self.context, self.request)

        user = api.get_or_create_user(self.context.authenticated_user())
        user_profile = None
        if enable_auto_input_form(user):
            user_profile = user.user_profile

        if user_profile is not None:
            formdata = MultiDict(
                last_name=user_profile.last_name,
                last_name_kana=user_profile.last_name_kana,
                first_name=user_profile.first_name,
                first_name_kana=user_profile.first_name_kana,
                tel_1=user_profile.tel_1,
                fax=getattr(user_profile, "fax", None), 
                zip=user_profile.zip,
                prefecture=user_profile.prefecture,
                city=user_profile.city,
                address_1=user_profile.address_1,
                address_2=user_profile.address_2,
                email_1=user_profile.email_1,
                email_2=user_profile.email_2
                )
        else:
            formdata = None

        form = schemas.ClientForm(
            formdata=formdata,
            context=self.context,
            flavors=(self.context.cart_setting.flavors or {})
            )
        default_prefecture = self.context.cart_setting.default_prefecture
        if default_prefecture is not None:
            form['prefecture'].data = default_prefecture
        return dict(
            form=form,
            payment_delivery_methods=payment_delivery_methods
            )

    def get_validated_address_data(self):
        """フォームから ShippingAddress などの値を取りたいときはこれで"""
        form = self.form
        if form.validate():
            return dict(
                first_name=form.data['first_name'],
                last_name=form.data['last_name'],
                first_name_kana=form.data['first_name_kana'],
                last_name_kana=form.data['last_name_kana'],
                zip=form.data['zip'],
                prefecture=form.data['prefecture'],
                city=form.data['city'],
                address_1=form.data['address_1'],
                address_2=form.data['address_2'],
                country=u"日本国",
                email_1=form.data['email_1'],
                email_2=form.data['email_2'],
                tel_1=form.data['tel_1'],
                tel_2=None,
                fax=form.data['fax'],
                )
        else:
            return None

    def _validate_extras(self, cart, payment_delivery_pair, shipping_address_params):
        if not payment_delivery_pair or shipping_address_params is None:
            if not payment_delivery_pair:
                logger.debug("invalid : %s" % 'payment_delivery_method_pair_id')
                raise self.ValidationFailed(u"お支払／引取方法をお選びください")
            else:
                logger.debug("invalid : %s" % self.form.errors)
                raise self.ValidationFailed(u'購入者情報の入力内容を確認してください')

    @back(back_to_top, back_to_product_list_for_mobile)
    @lbr_view_config(request_method="POST")
    def post(self):
        """ 支払い方法、引き取り方法選択
        """
        cart = self.context.cart
        user = api.get_or_create_user(self.context.authenticated_user())

        payment_delivery_method_pair_id = self.request.params.get('payment_delivery_method_pair_id', 0)
        payment_delivery_pair = c_models.PaymentDeliveryMethodPair.query.filter_by(id=payment_delivery_method_pair_id).first()

        self.form = schemas.ClientForm(formdata=self.request.params, context=self.context)
        shipping_address_params = self.get_validated_address_data()

        try:
            self._validate_extras(cart, payment_delivery_pair, shipping_address_params)
            sales_segment = cart.sales_segment
            cart.payment_delivery_pair = payment_delivery_pair
            cart.shipping_address = self.create_shipping_address(user, shipping_address_params)
            self.context.check_order_limit()

            DBSession.add(cart)

            try:
                plugins = lookup_plugin(self.request, cart.payment_delivery_pair)
                for plugin in plugins:
                    if plugin is not None:
                        plugin.validate_order(self.request, cart)
            except OrderLikeValidationFailure as e:
                if e.path == 'order.total_amount':
                    raise self.ValidationFailed(u'合計金額が選択された決済方法では取り扱えない金額となっています。他の決済方法を選択してください')
                else:
                    raise self.ValidationFailed(u'現在の予約内容では選択された決済 / 引取方法で購入を進めることができません。他の決済・引取方法を選択してください。')
        except self.ValidationFailed as e:
            self.request.session.flash(e.message)
            start_on = cart.performance.start_on
            sales_segment = self.context.sales_segment
            
            payment_delivery_methods = [pdmp
                                        for pdmp in self.context.available_payment_delivery_method_pairs(sales_segment)
                                        if pdmp.payment_method.public]
        
            if 0 == len(payment_delivery_methods):
                raise PaymentMethodEmptyError.from_resource(self.context, self.request)
            return dict(
                form=self.form,
                payment_delivery_methods=payment_delivery_methods
                )


        order = api.new_order_session(
            self.request,
            client_name=self.get_client_name(),
            payment_delivery_method_pair_id=payment_delivery_method_pair_id,
            email_1=cart.shipping_address.email_1,
        )

        set_confirm_url(self.request, self.request.route_url('payment.confirm'))

        if is_fc_auth_organization(context=self.context, request=self.request):
            if user:
                api.get_or_create_user_profile(user, shipping_address_params)

        t = flow_graph(self.context, self.request)
        if t is None:
            logger.error('no flow action defined!')
            response = Payment(cart, self.request).call_prepare()
            if response is not None:
                return response
            else:
                return HTTPFound(location=self.request.route_path('payment.confirm'))
        else:
            return HTTPFound(location=t(url_wanted=False))

    def get_client_name(self):
        return self.request.params['last_name'] + self.request.params['first_name']

    def create_shipping_address(self, user, data):
        logger.debug('shipping_address=%r', data)
        return c_models.ShippingAddress(
            first_name=data['first_name'],
            last_name=data['last_name'],
            first_name_kana=data['first_name_kana'],
            last_name_kana=data['last_name_kana'],
            zip=data['zip'],
            prefecture=data['prefecture'],
            city=data['city'],
            address_1=data['address_1'],
            address_2=data['address_2'],
            country=data['country'],
            email_1=data['email_1'],
            email_2=data['email_2'],
            tel_1=data['tel_1'],
            tel_2=data['tel_2'],
            fax=data['fax'],
            sex=data.get("sex"),
            user=user
        )


@view_defaults(route_name='cart.extra_form', renderer=selectable_renderer("extra_form.html"), decorator=with_jquery.not_when(mobile_request), permission="buy")
class ExtraFormView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(request_method="GET")
    def get(self):
        extra_form_field_descs = self.context.sales_segment.setting.extra_form_fields
        if extra_form_field_descs is None:
            logger.error('no extra form is specified')
            return HTTPFound(location=flow_graph(self.context, self.request)(url_wanted=False))

        form, form_fields = build_dynamic_form(
            self.request,
            extra_form_field_descs
            )
        return dict(form=form, form_fields=form_fields)

    @lbr_view_config(request_method="POST")
    def post(self):
        form = form_fields = None
        extra_form_field_descs = self.context.sales_segment.setting.extra_form_fields
        if extra_form_field_descs is None:
            logger.error('no extra form is specified')
            return HTTPFound(location=flow_graph(self.context, self.request)(url_wanted=False))

        form, form_fields = build_dynamic_form(
            self.request,
            extra_form_field_descs,
            UnicodeMultiDictAdapter(self.request.params, 'utf-8', 'replace')
            )
        if not form.validate():
            return dict(form=form, form_fields=form_fields)
        api.store_extra_form_data(self.request, form.data)
        return HTTPFound(location=flow_graph(self.context, self.request)(url_wanted=False))


@view_defaults(route_name='cart.point', renderer=selectable_renderer("point.html"), decorator=with_jquery.not_when(mobile_request), permission="buy")
class PointAccountEnteringView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_point_data(self):
        form = self.form
        return dict(
            accountno=form.data['accountno'],
            )

    @back(back_to_top, back_to_product_list_for_mobile)
    @lbr_view_config(request_method="GET")
    def point(self):
        cart = self.context.cart
        if cart.payment_delivery_pair is None or cart.shipping_address is None:
            # 不正な画面遷移
            raise NoCartError()

        formdata = MultiDict(
            accountno=""
            )
        form = schemas.PointForm(formdata=formdata)

        asid = self.context.asid
        if is_mobile_request(self.request):
            asid = self.context.asid_mobile

        if is_smartphone(self.request):
            asid = self.context.asid_smartphone

        accountno = self.request.params.get('account')
        user = api.get_or_create_user(self.context.authenticated_user())
        if accountno:
            form['accountno'].data = accountno.replace('-', '')
        else:
            if enable_auto_input_form(user) and user:
                acc = api.get_user_point_account(user.id)
                form['accountno'].data = acc.account_number.replace('-', '') if acc else ""

        return dict(
            form=form,
            asid=asid
        )

    @back(back_to_top, back_to_product_list_for_mobile)
    @lbr_view_config(request_method="POST")
    def point_post(self):
        self.form = schemas.PointForm(formdata=self.request.params)

        cart = self.context.cart
        if cart.payment_delivery_pair is None or cart.shipping_address is None:
            # 不正な画面遷移
            raise NoCartError()

        user = self.context.user_object

        form = self.form
        if not form.validate():
            asid = self.context.asid
            if is_mobile_request(self.request):
                asid = self.context.asid_mobile

            if is_smartphone(self.request):
                asid = self.context.asid_smartphone
            return dict(form=form, asid=asid)

        point_params = self.get_point_data()

        if is_point_input_required(self.context, self.request):
            point = point_params.pop("accountno", None)
            if point:
                if not user:
                    user = api.get_or_create_user_from_point_no(point)
                    cart.shipping_address.user = user
                    DBSession.add(cart)
                api.create_user_point_account_from_point_no(
                    user.id,
                    type=UserPointAccountTypeEnum.Rakuten,
                    account_number=point
                    )

        return HTTPFound(location=flow_graph(self.context, self.request)(url_wanted=False))


@view_defaults(
    route_name='payment.confirm',
    decorator=with_jquery.not_when(mobile_request),
    renderer=selectable_renderer("confirm.html"),
    permission="buy")
class ConfirmView(object):
    """ 決済確認画面 """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(request_method="GET")
    def get(self):
        form = schemas.CSRFSecureForm(csrf_context=self.request.session)
        cart = self.context.cart
        if cart.shipping_address is None:
            raise InvalidCartStatusError(cart.id)

        acc = api.get_user_point_account(cart.shipping_address.user_id)

        magazines_to_subscribe = get_magazines_to_subscribe(cart.performance.event.organization, cart.shipping_address.emails)

        payment = Payment(cart, self.request)
        payment.call_validate()
        delegator = payment.call_delegator()

        raw_extra_form_data = api.load_extra_form_data(self.request)
        extra_form_data = None
        if raw_extra_form_data is not None:
            extra_form_data = get_extra_form_data_pair_pairs(
                self.context,
                self.request,
                self.context.sales_segment,
                raw_extra_form_data
                )
        return dict(
            cart=cart,
            mailmagazines_to_subscribe=magazines_to_subscribe,
            form=form,
            delegator=delegator,
            extra_form_data=extra_form_data,
            accountno=acc.account_number if acc else ""
        )


@view_defaults(route_name='payment.finish', decorator=with_jquery.not_when(mobile_request), renderer=selectable_renderer("completion.html"))
class CompleteView(object):
    """ 決済完了画面"""
    """permisson="buy" 不要"""
    def __init__(self, context, request):
        self.context = context
        self.request = request
        # TODO: Orderを表示？

    @limiter.release
    @back(back_to_top, back_to_product_list_for_mobile)
    @lbr_view_config(route_name='payment.finish.mobile', request_method="POST")
    @lbr_view_config(route_name='payment.confirm', request_method="POST")
    def post(self):
        try:
            form = schemas.CSRFSecureForm(formdata=self.request.params, csrf_context=self.request.session)
            if not form.validate():
                logger.info('invalid csrf token: %s' % form.errors)
                raise InvalidCSRFTokenException

            # セッションからCSRFトークンを削除して再利用不可にしておく
            if 'csrf' in self.request.session:
                del self.request.session['csrf']
                self.request.session.persist()

            cart = self.context.cart
            if not cart.is_valid():
                raise NoCartError()
        except (InvalidCSRFTokenException, NoCartError):
            # 後で再度raiseするときに、現在の例外の状態をtry-exceptで
            # 撹乱されたくないので、副作用を呼び出しフレームの中に閉じ込める
            def _():
                try:
                    _cart = api.get_cart(self.request, for_update=False)
                    if _cart is not None:
                        return self.render_complete_page(_cart.order_no)
                    else:
                        return render_view_to_response_with_derived_request(
                            context_factory=CompleteViewTicketingCartResource,
                            request=self.request,
                            route=('payment.finish',{})
                            )
                except:
                    return None
            retval = _()
            if retval is not None:
                return retval
            else:
                raise

        self.context.check_order_limit()

        payment = Payment(cart, self.request)
        order = payment.call_payment()
        order_id = order.id
        order_no = order.order_no

        extra_form_data = api.load_extra_form_data(self.request)
        if extra_form_data is not None:
            order.attributes = coerce_extra_form_data(self.request, extra_form_data)

        notify_order_completed(self.request, order)

        # メール購読でエラーが出てロールバックされても困る
        transaction.commit()

        cart = api.get_cart(self.request) # これは get_cart でよい

        # メール購読
        user = api.get_user(self.context.authenticated_user()) # これも読み直し
        emails = cart.shipping_address.emails
        magazine_ids = self.request.params.getall('mailmagazine')
        multi_subscribe(user, emails, magazine_ids)

        api.logout(self.request)

        self.request.response.expires = datetime.now() + timedelta(seconds=3600)
        api.get_temporary_store(self.request).set(self.request, order_no)
        if IMobileRequest.providedBy(self.request):
            api.disassociate_cart_from_session(self.request)
            # モバイルの場合はHTTPリダイレクトの際のSet-Cookieに対応していないと
            # 思われるので、直接ページをレンダリングする
            return render_view_to_response_with_derived_request(
                context_factory=CompleteViewTicketingCartResource,
                request=self.request,
                route=('payment.finish', {})
                )
        else:
            # PC/スマートフォンでは、HTTPリダイレクト時にクッキーをセット
            return HTTPFound(self.request.route_path('payment.finish'), headers=self.request.response.headers)

    @lbr_view_config(context=CompleteViewTicketingCartResource)
    def get(self):
        try:
            order_no = api.get_temporary_store(self.request).get(self.request)
        except:
            raise CompletionPageNotRenderered()
        return self.render_complete_page(order_no)

    def render_complete_page(self, order_no):
        api.disassociate_cart_from_session(self.request)
        order = api.get_order_for_read_by_order_no(self.request, order_no)
        if order is None:
            raise CompletionPageNotRenderered()
        self.request.response.expires = datetime.utcnow() + timedelta(seconds=3600) # XXX
        self.request.response.cache_control = 'max-age=3600'
        return dict(order=order)


@view_defaults(decorator=with_jquery.not_when(mobile_request))
class InvalidMemberGroupView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(context='.authorization.InvalidMemberGroupException')
    def __call__(self):
        event_id = self.context.event.id
        event = c_models.Event.query.filter(c_models.Event.id==event_id).one()
        location = api.get_valid_sales_url(self.request, event)
        logger.debug('url: %s ' % location)
        return HTTPFound(location=location)


def is_kt_organization(out_term_exception, request):
    from .api import get_organization
    organization = get_organization(request)
    return organization.code == 'KT'

@view_defaults(
    decorator=with_jquery.not_when(mobile_request),
    context='.exceptions.OutTermSalesException')
class OutTermSalesView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(
        custom_predicates=(lambda context, _: issubclass(context.type_, EventOrientedTicketingCartResource), ),
        renderer=selectable_renderer('out_term_sales_event.html'))
    def for_event(self):
        api.logout(self.request)
        if self.context.next is None:
            datum = self.context.last
            which = 'last'
        else:
            datum = self.context.next
            which = 'next'
        return dict(which=which, outer=self.context, **datum)

    @lbr_view_config(
        custom_predicates=(lambda context, _: issubclass(context.type_, PerformanceOrientedTicketingCartResource), ),
        renderer=selectable_renderer('out_term_sales_performance.html'),
        )
    def for_performance(self):
        if self.context.next is None:
            datum = self.context.last
            which = 'last'
        else:
            datum = self.context.next
            which = 'next'
        event_context = EventOrientedTicketingCartResource(self.request, self.context.performance.event_id)
        available_sales_segments = None
        try:
            available_sales_segments = event_context.available_sales_segments
        except (NoSalesSegment, OutTermSalesException):
            pass
        api.logout(self.request)
        return dict(which=which, outer=self.context, available_sales_segments=available_sales_segments, **datum)

@lbr_view_config(decorator=with_jquery.not_when(mobile_request), request_method="POST", route_name='cart.logout')
@limiter.release
def logout(request):
    api.logout(request)
    return back_to_top(request)

def _create_response(request, params=None):
    event_id = request.matchdict.get('event_id')
    response = HTTPFound(event_id and request.route_url('cart.index', event_id=event_id, _query=params) or '/')
    return response

def _create_response_perf(request, params=None):
    performance_id = request.matchdict.get('performance_id')
    response = HTTPFound(performance_id and request.route_url('cart.index2', performance_id=performance_id, _query=params) or '/')
    return response

@view_config(route_name='cart.switchpc')
def switch_pc(context, request):
    api.remove_cart(request)
    response = _create_response(request=request, params=request.GET)
    set_we_need_pc_access(response)
    return response

@view_config(route_name='cart.switchpc.perf')
def switch_pc_perf(context, request):
    api.remove_cart(request)
    response = _create_response_perf(request=request, params=request.GET)
    set_we_need_pc_access(response)
    return response

@view_config(route_name='cart.switchsp')
def switch_sp(context, request):
    api.remove_cart(request)
    response = _create_response(request=request, params=request.GET)
    set_we_invalidate_pc_access(response)
    return response

@view_config(route_name='cart.switchsp.perf')
def switch_sp_perf(context, request):
    api.remove_cart(request)
    response = _create_response_perf(request=request, params=request.GET)
    set_we_invalidate_pc_access(response)
    return response
