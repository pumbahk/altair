# -*- coding:utf-8 -*-
import logging
import re
import json
import transaction
import time
from datetime import datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from markupsafe import Markup

from pyramid.httpexceptions import HTTPNotFound, HTTPFound, HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from pyramid.threadlocal import get_current_request
from webob.multidict import MultiDict

from altair.pyramid_boto.s3.assets import IS3KeyProvider

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.core import api as c_api
from altair.app.ticketing.mailmags.api import get_magazines_to_subscribe, multi_subscribe
from altair.app.ticketing.views import mobile_request
from altair.app.ticketing.fanstatic import with_jquery, with_jquery_tools
from altair.app.ticketing.payments.payment import Payment
from altair.app.ticketing.payments.exceptions import PaymentDeliveryMethodPairNotFound
from altair.app.ticketing.users.models import UserPointAccountTypeEnum
from altair.app.ticketing.users.api import (
    get_user,
    get_or_create_user,
    get_or_create_user_from_point_no,
    create_user_point_account_from_point_no,
    get_user_point_account,
    get_or_create_user_profile
    )
from altair.app.ticketing.venues.api import get_venue_site_adapter
from altair.mobile.interfaces import IMobileRequest
from altair.sqlahelper import get_db_session
from altair.app.ticketing.temp_store import TemporaryStoreError

from . import api
from . import helpers as h
from . import schemas
from .api import set_rendered_event, is_mobile, is_smartphone, is_smartphone_organization, is_point_input_organization
from altair.mobile.api import set_we_need_pc_access, set_we_invalidate_pc_access
from .events import notify_order_completed
from .reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from .stocker import InvalidProductSelectionException, NotEnoughStockException
from .selectable_renderer import selectable_renderer
from .view_support import IndexViewMixin, get_amount_without_pdmp, get_seat_type_dicts, assert_quantity_within_bounds
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
from .resources import EventOrientedTicketingCartResource, PerformanceOrientedTicketingCartResource
from .limiting import LimiterDecorators

logger = logging.getLogger(__name__)

limiter = LimiterDecorators('altair.cart.limit_per_unit_time', TooManyCartsCreated)

def back_to_product_list_for_mobile(request):
    cart = api.get_cart_safe(request)
    api.release_cart(request, cart)
    api.remove_cart(request)
    return HTTPFound(
        request.route_url(
            route_name='cart.products',
            event_id=cart.performance.event_id,
            performance_id=cart.performance_id,
            sales_segment_id=cart.sales_segment_id,
            seat_type_id=cart.items[0].product.items[0].stock.stock_type_id))

def back_to_top(request):
    event_id = None
    performance_id = None

    try:
        event_id = long(request.matchdict.get('event_id'))
    except (ValueError, TypeError):
        pass
    if isinstance(request.context, PerformanceOrientedTicketingCartResource) and \
       request.context.performance:
        performance_id = request.context.performance.id
    else:
        try:
            performance_id = long(request.params.get('pid') or request.params.get('performance'))
        except (ValueError, TypeError):
            pass

    if event_id is None:
        if performance_id is None:
            cart = api.get_cart(request)
            if cart is not None:
                performance_id = cart.performance.id
                event_id = cart.performance.event_id
        else:
            try:
                event_id = DBSession.query(c_models.Performance).filter_by(id=performance_id).one().event_id
            except:
                pass
 
    extra = {}
    if performance_id is not None:
        extra['_query'] = { 'performance': performance_id }

    ReleaseCartView(request)()

    return HTTPFound(event_id and request.route_url('cart.index', event_id=event_id, **extra) or request.context.host_base_url or "/", headers=request.response.headers)

def back(pc=back_to_top, mobile=None):
    if mobile is None:
        mobile = pc

    def factory(func):
        def retval(*args, **kwargs):
            request = get_current_request()
            if request.params.has_key('back'):
                if IMobileRequest.providedBy(request):
                    return mobile(request)
                else:
                    return pc(request)
            return func(*args, **kwargs)
        return retval
    return factory

def gzip_preferred(request, response):
    if 'gzip' in request.accept_encoding:
        response.encode_content('gzip')

@view_defaults(decorator=with_jquery.not_when(mobile_request))
class IndexView(IndexViewMixin):
    """ 座席選択画面 """
    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.prepare()

    @view_config(decorator=with_jquery_tools, route_name='cart.index',
                  renderer=selectable_renderer("%(membership)s/pc/index.html"), xhr=False, permission="buy")
    @view_config(decorator=with_jquery_tools, route_name='cart.index',request_type="altair.mobile.interfaces.ISmartphoneRequest", 
                 custom_predicates=(is_smartphone_organization, ), renderer=selectable_renderer("%(membership)s/smartphone/index.html"), xhr=False, permission="buy")
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
            preferred_performance=preferred_performance
            )

    # パフォーマンスベースのランディング画面
    @view_config(decorator=with_jquery_tools, route_name='cart.index2',
                  renderer=selectable_renderer("%(membership)s/pc/index.html"), xhr=False, permission="buy")
    @view_config(decorator=with_jquery_tools, route_name='cart.index2',request_type="altair.mobile.interfaces.ISmartphoneRequest", 
                 custom_predicates=(is_smartphone_organization, ), renderer=selectable_renderer("%(membership)s/smartphone/index.html"), xhr=False, permission="buy")
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


class IndexAjaxView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    def get_frontend_drawing_urls(self, venue):
        sales_segment = self.request.context.sales_segment
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
                        event_id=self.request.context.event.id,
                        performance_id=sales_segment.performance.id,
                        venue_id=sales_segment.performance.venue.id,
                        part=name)
                retval[name] = url
        return retval

    @view_config(route_name='cart.seat_types2', renderer="json")
    def get_seat_types(self):
        sales_segment = self.request.context.sales_segment # XXX: matchdict から取得していることを期待

        order_separate_seats_url = u''
        organization = c_api.get_organization(self.request)
        if organization.setting.entrust_separate_seats:
            qs = {'separate_seats': 'true'}
            order_separate_seats_url = self.request.route_url('cart.order', sales_segment_id=sales_segment.id, _query=qs)

        seat_type_dicts = get_seat_type_dicts(self.request, sales_segment)

        data = dict(
            seat_types=[
                dict(
                    products_url=self.request.route_url(
                        'cart.products2',
                        event_id=self.request.context.event.id,
                        performance_id=sales_segment.performance.id,
                        sales_segment_id=sales_segment.id,
                        seat_type_id=_dict['id']),
                    seats_url=self.request.route_url(
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
            event_id=self.request.context.event.id,
            venue_id=sales_segment.performance.venue.id,
            data_source=dict(
                venue_drawing=self.request.route_url(
                    'cart.venue_drawing',
                    event_id=self.request.context.event.id,
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

    @view_config(route_name='cart.products', renderer="json")
    @view_config(route_name='cart.products2', renderer="json")
    def get_products(self):
        """ 席種別ごとの購入単位
        SeatType -> ProductItem -> Product
        """
        seat_type_id = long(self.request.matchdict['seat_type_id'])
        product_dicts = get_seat_type_dicts(self.request, self.context.sales_segment, seat_type_id)[0]['products']
        return dict(products=product_dicts)

    @view_config(route_name='cart.info', renderer="json")
    @view_config(route_name='cart.info.obsolete', renderer="json")
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

    @view_config(route_name='cart.seats', renderer="json")
    @view_config(route_name='cart.seats.obsolete', renderer="json")
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

    @view_config(route_name='cart.seat_adjacencies', renderer="json")
    @view_config(route_name='cart.seat_adjacencies.obsolete', renderer="json")
    def get_seat_adjacencies(self):
        """連席情報"""
        try:
            venue_id = long(self.request.matchdict.get('venue_id'))
        except (ValueError, TypeError):
            venue_id = None

        length_or_range = self.request.matchdict['length_or_range']
        return dict(
            seat_adjacencies={
                length_or_range: [
                    [seat.l0_id for seat in seat_adjacency.seats_filter_by_venue(venue_id)]
                    for seat_adjacency_set in \
                        DBSession.query(c_models.SeatAdjacencySet)\
                            .filter_by(site_id=performance.venue.site_id, seat_count=length_or_range)
                    for seat_adjacency in seat_adjacency_set.adjacencies
                    ]
                }
            )

    @view_config(route_name="cart.venue_drawing", request_method="GET")
    @view_config(route_name="cart.venue_drawing.obsolete", request_method="GET")
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


@view_defaults(decorator=with_jquery)
class ReserveView(object):
    """ 座席選択完了画面(おまかせ) """

    product_id_regex = re.compile(r'product-(?P<product_id>\d+)')

    def __init__(self, request):
        self.request = request
        self.context = request.context


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
    @view_config(route_name='cart.order', request_method="POST", renderer='json')
    def reserve(self):
        h.form_log(self.request, "received order")
        ordered_items = self.ordered_items
        if not ordered_items:
            return dict(result='NG', reason="no products")

        selected_seats = self.request.params.getall('selected_seat')
        separate_seats = True if self.request.params.get('separate_seats') == 'true' else False
        logger.debug('ordered_items %s' % ordered_items)

        sales_segment = self.context.sales_segment

        try:
            assert_quantity_within_bounds(sales_segment, ordered_items)
            cart = api.order_products(
                self.request,
                sales_segment.id,
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
                                             seats=p.seats if sales_segment.seat_choice else [],
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
    @view_config(route_name='cart.release', request_method="POST", renderer="json")
    def __call__(self):
        try:
            cart = self.request.context.cart
            api.release_cart(self.request, cart)
            api.remove_cart(self.request)
        except NoCartError:
            import sys
            logger.info('exception ignored', exc_info=sys.exc_info())
        return dict()


@view_defaults(decorator=with_jquery.not_when(mobile_request))
class PaymentView(object):
    """ 支払い方法、引き取り方法選択 """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @property
    def sales_segment(self):
        # contextから取れることを期待できないので
        # XXX: 会員区分からバリデーションしなくていいの?
        return c_models.SalesSegment.query.filter(c_models.SalesSegment.id==self.request.matchdict['sales_segment_id']).one()

    @view_config(route_name='cart.payment', request_method="GET", renderer=selectable_renderer("%(membership)s/pc/payment.html"))
    @view_config(route_name='cart.payment', request_method="GET", request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("%(membership)s/mobile/payment.html"))
    @view_config(route_name='cart.payment', request_method="GET", request_type="altair.mobile.interfaces.ISmartphoneRequest", renderer=selectable_renderer("%(membership)s/smartphone/payment.html"), custom_predicates=(is_smartphone_organization, ))
    def __call__(self):
        """ 支払い方法、引き取り方法選択
        """
        start_on = self.request.context.cart.performance.start_on
        sales_segment = self.request.context.sales_segment
        payment_delivery_methods = [pdmp
                                    for pdmp in self.context.available_payment_delivery_method_pairs(sales_segment)
                                    if pdmp.payment_method.public]
        
        if 0 == len(payment_delivery_methods):
            raise PaymentMethodEmptyError.from_resource(self.context, self.request)

        user = get_or_create_user(self.context.authenticated_user())
        user_profile = None
        if user is not None:
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

        form = schemas.ClientForm(formdata=formdata)
        return dict(form=form,
            payment_delivery_methods=payment_delivery_methods,
            #user=user, user_profile=user.user_profile,
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

    def get_point_data(self):
        form = self.form
        return dict(
            accountno=form.data['accountno'],
            )

    def _validate_extras(self, cart, payment_delivery_pair, shipping_address_params):
        if not payment_delivery_pair or shipping_address_params is None:
            if not payment_delivery_pair:
                self.request.session.flash(u"お支払／引取方法をお選びください")
                logger.debug("invalid : %s" % 'payment_delivery_method_pair_id')
            else:
                logger.debug("invalid : %s" % self.form.errors)

            return False
        return True

    @back(back_to_top, back_to_product_list_for_mobile)
    @view_config(route_name='cart.payment', request_method="POST", renderer=selectable_renderer("%(membership)s/pc/payment.html"))
    @view_config(route_name='cart.payment', request_method="POST", request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("%(membership)s/mobile/payment.html"))
    @view_config(route_name='cart.payment', request_method="POST", request_type="altair.mobile.interfaces.ISmartphoneRequest", renderer=selectable_renderer("%(membership)s/smartphone/payment.html"), custom_predicates=(is_smartphone_organization, ))
    def post(self):
        """ 支払い方法、引き取り方法選択
        """
        cart = self.request.context.cart
        user = get_or_create_user(self.context.authenticated_user())

        payment_delivery_method_pair_id = self.request.params.get('payment_delivery_method_pair_id', 0)
        payment_delivery_pair = c_models.PaymentDeliveryMethodPair.query.filter_by(id=payment_delivery_method_pair_id).first()


        self.form = schemas.ClientForm(formdata=self.request.params)
        shipping_address_params = self.get_validated_address_data()
        if not self._validate_extras(cart, payment_delivery_pair, shipping_address_params):
            start_on = cart.performance.start_on
            sales_segment = self.request.context.sales_segment
            
            payment_delivery_methods = [pdmp
                                        for pdmp in self.context.available_payment_delivery_method_pairs(sales_segment)
                                        if pdmp.payment_method.public]
        
            if 0 == len(payment_delivery_methods):
                raise PaymentMethodEmptyError.from_resource(self.context, self.request)
        

            return dict(form=self.form, payment_delivery_methods=payment_delivery_methods)

        sales_segment = cart.sales_segment
        cart.payment_delivery_pair = payment_delivery_pair
        cart.shipping_address = self.create_shipping_address(user, shipping_address_params)
        self.context.check_order_limit()

        DBSession.add(cart)

        order = api.new_order_session(
            self.request,
            client_name=self.get_client_name(),
            payment_delivery_method_pair_id=payment_delivery_method_pair_id,
            email_1=cart.shipping_address.email_1,
        )

        self.request.session['payment_confirm_url'] = self.request.route_url('payment.confirm')

        if is_point_input_organization(context=self.context, request=self.request):
            if user:
                get_or_create_user_profile(user, shipping_address_params)
            return HTTPFound(self.request.route_path('cart.point'))

        payment = Payment(cart, self.request)
        result = payment.call_prepare()
        if callable(result):
            return result
        else:
            return HTTPFound(self.request.route_url("payment.confirm"))

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

    @back(back_to_top, back_to_product_list_for_mobile)
    @view_config(route_name='cart.point', request_method="GET", renderer=selectable_renderer("%(membership)s/pc/point.html"))
    @view_config(route_name='cart.point', request_method="GET", request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("%(membership)s/mobile/point.html"))
    @view_config(route_name='cart.point', request_method="GET", request_type="altair.mobile.interfaces.ISmartphoneRequest", renderer=selectable_renderer("%(membership)s/smartphone/point.html"), custom_predicates=(is_smartphone_organization, ))
    def point(self):

        formdata = MultiDict(
            accountno=""
            )
        form = schemas.PointForm(formdata=formdata)

        asid = self.request.altair_pc_asid
        if is_mobile(self.request):
            asid = self.request.altair_mobile_asid

        if is_smartphone(self.request):
            asid = self.request.altair_smartphone_asid

        accountno = self.request.params.get('account')
        if accountno:
            form['accountno'].data = accountno.replace('-', '')
        else:
            user = get_or_create_user(self.context.authenticated_user())
            if user:
                acc = get_user_point_account(user.id)
                form['accountno'].data = acc.account_number.replace('-', '') if acc else ""

        return dict(
            form=form,
            asid=asid
        )

    @back(back_to_top, back_to_product_list_for_mobile)
    @view_config(route_name='cart.point', request_method="POST", renderer=selectable_renderer("%(membership)s/pc/point.html"))
    @view_config(route_name='cart.point', request_method="POST", request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("%(membership)s/mobile/point.html"))
    @view_config(route_name='cart.point', request_method="POST", request_type="altair.mobile.interfaces.ISmartphoneRequest", renderer=selectable_renderer("%(membership)s/smartphone/point.html"), custom_predicates=(is_smartphone_organization, ))
    def point_post(self):
        self.form = schemas.PointForm(formdata=self.request.params)

        cart = self.request.context.cart
        user = self.context.user_object

        form = self.form
        if not form.validate():
            asid = None
            if is_mobile(self.request):
                asid = self.request.altair_mobile_asid

            if is_smartphone(self.request):
                asid = self.request.altair_smartphone_asid
            return dict(form=form, asid=asid)

        point_params = self.get_point_data()

        if is_point_input_organization(self.context, self.request):
            point = point_params.pop("accountno", None)
            if point:
                if not user:
                    user = get_or_create_user_from_point_no(point)
                    cart.shipping_address.user = user
                    DBSession.add(cart)
                create_user_point_account_from_point_no(
                    user.id,
                    type=UserPointAccountTypeEnum.Rakuten,
                    account_number=point
                    )

        payment = Payment(cart, self.request)
        result = payment.call_prepare()
        if callable(result):
            return result
        else:
            return HTTPFound(self.request.route_url("payment.confirm"))
        return {}


@view_defaults(decorator=with_jquery.not_when(mobile_request))
class ConfirmView(object):
    """ 決済確認画面 """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='payment.confirm', request_method="GET", renderer=selectable_renderer("%(membership)s/pc/confirm.html"))
    @view_config(route_name='payment.confirm', request_method="GET", request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("%(membership)s/mobile/confirm.html"))
    @view_config(route_name='payment.confirm', request_method="GET", request_type="altair.mobile.interfaces.ISmartphoneRequest", renderer=selectable_renderer("%(membership)s/smartphone/confirm.html"), custom_predicates=(is_smartphone_organization, ))
    def get(self):

        form = schemas.CSRFSecureForm(csrf_context=self.request.session)
        cart = self.request.context.cart
        if cart.shipping_address is None:
            raise InvalidCartStatusError(cart.id)

        acc = get_user_point_account(cart.shipping_address.user_id)

        magazines_to_subscribe = get_magazines_to_subscribe(cart.performance.event.organization, cart.shipping_address.emails)

        payment = Payment(cart, self.request)
        try:
            payment.call_validate()
            delegator = payment.call_delegator()
        except PaymentDeliveryMethodPairNotFound:
            raise HTTPFound(self.request.route_path("cart.payment", sales_segment_id=cart.sales_segment_id))
        return dict(
            cart=cart,
            mailmagazines_to_subscribe=magazines_to_subscribe,
            form=form,
            delegator=delegator,
            accountno=acc.account_number if acc else ""
        )


@view_defaults(decorator=with_jquery.not_when(mobile_request))
class CompleteView(object):
    """ 決済完了画面"""
    def __init__(self, request):
        self.request = request
        self.context = request.context
        # TODO: Orderを表示？

    @limiter.release
    @back(back_to_top, back_to_product_list_for_mobile)
    @view_config(route_name='payment.finish', request_method="POST", renderer=selectable_renderer("%(membership)s/pc/completion.html"))
    @view_config(route_name='payment.finish', request_method="POST", request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("%(membership)s/mobile/completion.html"))
    @view_config(route_name='payment.finish', request_method="POST", request_type="altair.mobile.interfaces.ISmartphoneRequest", renderer=selectable_renderer("%(membership)s/smartphone/completion.html"), custom_predicates=(is_smartphone_organization, ))
    def complete_post(self):
        try:
            form = schemas.CSRFSecureForm(formdata=self.request.params, csrf_context=self.request.session)
            if not form.validate():
                logger.info('invalid csrf token: %s' % form.errors)
                raise InvalidCSRFTokenException

            # セッションからCSRFトークンを削除して再利用不可にしておく
            if 'csrf' in self.request.session:
                del self.request.session['csrf']
                self.request.session.persist()

            cart = self.request.context.cart
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
                        return self.complete_get()
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

        notify_order_completed(self.request, order)

        # メール購読でエラーが出てロールバックされても困る
        transaction.commit()

        cart = api.get_cart(self.request) # これは get_cart でよい

        # メール購読
        user = get_user(self.context.authenticated_user()) # これも読み直し
        emails = cart.shipping_address.emails
        magazine_ids = self.request.params.getall('mailmagazine')
        multi_subscribe(user, emails, magazine_ids)

        api.logout(self.request)

        self.request.response.expires = datetime.now() + timedelta(seconds=3600)
        api.get_temporary_store(self.request).set(self.request, order_no)
        if IMobileRequest.providedBy(self.request):
            api.remove_cart(self.request)
            # モバイルの場合はHTTPリダイレクトの際のSet-Cookieに対応していないと
            # 思われるので、直接ページをレンダリングする
            # transaction をコミットしたので、再度読み直し
            order = c_models.Order.query.filter_by(id=order_id).one()
            return dict(order=order)
        else:
            # PC/スマートフォンでは、HTTPリダイレクト時にクッキーをセット
            return HTTPFound(self.request.current_route_path(), headers=self.request.response.headers)

    @view_config(route_name='payment.finish', request_method="GET", renderer=selectable_renderer("%(membership)s/pc/completion.html"))
    @view_config(route_name='payment.finish', request_method="GET", request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("%(membership)s/mobile/completion.html"))
    @view_config(route_name='payment.finish', request_method="GET", request_type="altair.mobile.interfaces.ISmartphoneRequest", renderer=selectable_renderer("%(membership)s/smartphone/completion.html"), custom_predicates=(is_smartphone_organization, ))
    def complete_get(self):
        try:
            order_no = api.get_temporary_store(self.request).get(self.request)
        except:
            raise CompletionPageNotRenderered()
        return self.render_complete_page(order_no)

    def render_complete_page(self, order_no):
        api.remove_cart(self.request)
        order = api.get_order_for_read_by_order_no(self.request, order_no)
        if order is None:
            raise CompletionPageNotRenderered()
        self.request.response.expires = datetime.utcnow() + timedelta(seconds=3600) # XXX
        self.request.response.cache_control = 'max-age=3600'
        return dict(order=order)

@view_defaults(decorator=with_jquery.not_when(mobile_request))
class InvalidMemberGroupView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(context='.authorization.InvalidMemberGroupException')
    def __call__(self):
        event_id = self.context.event.id
        event = c_models.Event.query.filter(c_models.Event.id==event_id).one()
        location = api.get_valid_sales_url(self.request, event)
        logger.debug('url: %s ' % location)
        return HTTPFound(location=location)



@view_defaults(decorator=with_jquery.not_when(mobile_request), context='.exceptions.OutTermSalesException')
class OutTermSalesView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/pc/out_term_sales_event.html'),
                 custom_predicates=(lambda context, _: issubclass(context.type_, EventOrientedTicketingCartResource), ))
    def pc_event(self):
        return self._render_event()

    @view_config(renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/out_term_sales_event.html'),
                 request_type='altair.mobile.interfaces.IMobileRequest',
                 custom_predicates=(lambda context, _: issubclass(context.type_, EventOrientedTicketingCartResource), ))
    def mobile_event(self):
        return self._render_event()

    @view_config(renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/pc/out_term_sales_performance.html'),
                 custom_predicates=(lambda context, _: not issubclass(context.type_, EventOrientedTicketingCartResource), ))
    def pc_performance(self):
        return self._render_performance()

    @view_config(renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/out_term_sales_performance.html'),
                 request_type='altair.mobile.interfaces.IMobileRequest',
                 custom_predicates=(lambda context, _: not issubclass(context.type_, EventOrientedTicketingCartResource), ))
    def mobile_performance(self):
        return self._render_performance()

    def _render_event(self):
        api.logout(self.request)
        if self.context.next is None:
            datum = self.context.last
            which = 'last'
        else:
            datum = self.context.next
            which = 'next'
        return dict(which=which, outer=self.context, **datum)

    def _render_performance(self):
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

@view_config(decorator=with_jquery.not_when(mobile_request), request_method="POST", route_name='cart.logout')
@limiter.release
def logout(request):
    api.logout(request)
    return back_to_top(request)

def _create_response(request, param):
    event_id = request.matchdict.get('event_id')
    response = HTTPFound(event_id and request.route_url('cart.index', event_id=event_id) + param or '/')
    return response

@view_config(route_name='cart.switchpc')
def switch_pc(context, request):
    ReleaseCartView(request)()
    response = _create_response(request=request, param="")
    set_we_need_pc_access(response)
    return response

@view_config(route_name='cart.switchsp')
def switch_sp(context, request):
    ReleaseCartView(request)()
    response = _create_response(request=request, param="")
    set_we_invalidate_pc_access(response)
    return response

@view_config(route_name='cart.switchpc.perf')
def switch_pc_performance(context, request):
    ReleaseCartView(request)()
    performance = request.matchdict.get('performance')
    param = _create_performance_param(performance=performance)
    response = _create_response(request=request, param=param)
    set_we_need_pc_access(response)
    return response

@view_config(route_name='cart.switchsp.perf')
def switch_sp_performance(context, request):
    ReleaseCartView(request)()
    performance = request.matchdict.get('performance')
    param = _create_performance_param(performance=performance)
    response = _create_response(request=request, param=param)
    set_we_invalidate_pc_access(response)
    return response

def _create_performance_param(performance):
    param = ""
    if performance:
        param = "?performance=" + str(performance)
    return param
