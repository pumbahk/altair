
# -*- coding:utf-8 -*-
import logging
import transaction
import json
from datetime import datetime, timedelta
import re
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import or_
from markupsafe import Markup
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.exceptions import NotFound
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.threadlocal import get_current_request
from pyramid import security
from js.jquery_tools import jquery_tools
from urllib2 import urlopen
from zope.deprecation import deprecate
from ..models import DBSession
from ..core import models as c_models
from ..users import models as u_models
from .models import Cart
from . import helpers as h
from . import schemas
from .exceptions import CartException, NoCartError, NoEventError, InvalidCSRFTokenException, OverQuantityLimitError, ZeroQuantityError, CartCreationExceptoion
from .rakuten_auth.api import authenticated_user
from .events import notify_order_completed
from webob.multidict import MultiDict
from . import api
from .reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from .stocker import NotEnoughStockException
import transaction
from ticketing.cart.selectable_renderer import selectable_renderer
logger = logging.getLogger(__name__)

def back(func):
    def retval(*args, **kwargs):
        request = get_current_request()
        if request.params.has_key('back'):
            ReleaseCartView(request)()
            return HTTPFound(request.route_url('cart.index', event_id=request.params.get('event_id')))
        return func(*args, **kwargs)
    return retval

def get_seat_type_triplets(event_id, performance_id, sales_segment_id):
    segment_stocks = DBSession.query(c_models.ProductItem.stock_id).filter(
        c_models.ProductItem.product_id==c_models.Product.id).filter(
        c_models.Product.sales_segment_id==sales_segment_id)

    seat_type_triplets = DBSession.query(c_models.StockType, c_models.Stock.quantity, c_models.StockStatus.quantity).filter(
            c_models.Stock.id==c_models.StockStatus.stock_id).filter(
            c_models.Performance.event_id==event_id).filter(
            c_models.Performance.id==performance_id).filter(
            c_models.Performance.event_id==c_models.StockHolder.event_id).filter(
            c_models.StockHolder.id==c_models.Stock.stock_holder_id).filter(
            c_models.Stock.stock_type_id==c_models.StockType.id).filter(
            c_models.Stock.id.in_(segment_stocks)).filter(
            c_models.ProductItem.stock_id==c_models.Stock.id).filter(
            c_models.ProductItem.performance_id==performance_id).order_by(
            c_models.StockType.display_order).all()
    return seat_type_triplets

class IndexView(object):
    """ 座席選択画面 """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    #@view_config(route_name='cart.index', renderer=selectable_renderer("carts/%(membership)s/select_sales.html"), xhr=False, permission="buy")
    #def redirect_sale(self):
    #    """
    #    .. todo::

    #       - [x] イベントで利用可能な販売区分を取得する
    #       - [x] 複数の場合は選択画面を表示
    #       - [x] １つの場合はその販売区分ページにリダイレクト

    #       - [ ] performance指定の場合、そのperformanceが当日だったら、当日販売区分に遷移する
    #       - そうでない場合は、当日販売区分以外の販売区分が１つの場合その販売区分に遷移する
    #       -     販売区分が複数の場合は選択画面を表示する

    #       - URLから販売区分をはずす
    #       - 日付・会場・公演選択の裏データとして、販売区分をひもづける
    #       - 販売区分を表示する
    #       - フォームに販売区分を入れる
    #       - cartに販売区分を追加する
    #       - 決済ページ以降から販売区分をURLに復活


    #    """

    #    event = self.request.context.event
    #    if event is None:
    #        raise HTTPNotFound()

    #    # イベントで利用可能な販売区分を取得する
    #    sales_segments = self.context.sales_segments

    #    performance = None
    #    performance_id = self.request.params.get('performance')
    #    if performance_id:
    #        performance = c_models.Performance.query.filter(c_models.Performance.id==performance_id).one()
    #        if performance.on_the_day:
    #            # performance指定の場合、そのperformanceが当日だったら、当日販売区分に遷移する
    #            # 処理変更：当日の公演だった場合は、販売区分を当日のみにする
    #            # 上記処理の結果、販売区分が０個になってしまったら、元の販売区分を使う
    #            on_the_day_sales_segments = [s for s in sales_segments if s.kind == 'sales_counter'] # 当日
    #            if on_the_day_sales_segments:
    #                sales_segments = on_the_day_sales_segments
    #        else:
    #            # 当日でない場合、当日以外の販売区分が１つならそこに遷移する
    #            # 処理変更：当日以外の公演だった場合は、販売区分から当日をはずす
    #            # 上記処理の結果、販売区分が０個になってしまったら、元の販売区分を使う
    #            non_the_day_sales_segments = [s for s in sales_segments if s.kind != 'sales_counter'] # 当日以外
    #            if non_the_day_sales_segments:
    #                sales_segments = non_the_day_sales_segments

    #    if not sales_segments:
    #        logger.debug("No matching sales_segment")
    #        raise NoEventError("No matching sales_segment")
    #    if len(sales_segments) == 1:
    #        # １つの場合はその販売区分ページにリダイレクト

    #        logger.debug("one sales_segment is matched")
    #        sales_segment = sales_segments[0]
    #        event_id = self.request.matchdict['event_id']
    #        location = self.request.route_url('cart.index.sales', 
    #            event_id=event_id,
    #            sales_segment_id=sales_segment.id,
    #            _query=self.request.GET)
    #        return HTTPFound(location=location)
    #    logger.debug("multiple sales_segments are matched")

    #    # 複数の場合は選択画面を表示
    #    return dict(sales_segments=sales_segments,
    #        event=event)

    #@view_config(route_name='cart.index.sales', renderer=selectable_renderer('carts/%(membership)s/index.html'), xhr=False, permission="buy")
    @view_config(route_name='cart.index', renderer=selectable_renderer("carts/%(membership)s/index.html"), xhr=False, permission="buy")
    def __call__(self):
        event = self.request.context.event
        if event is None:
            raise HTTPNotFound()
        jquery_tools.need()
        context = self.request.context
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.params.get('performance')

        
        #sales_segment = self.context.get_sales_segument()
        normal_sales_segment = self.context.normal_sales_segment
        sales_counter_sales_segment = self.context.sales_counter_sales_segment
        if normal_sales_segment is None:
            logger.debug("No matching sales_segment")
            raise NoEventError("No matching sales_segment")

        from .api import get_event_info_from_cms
        event_extra_info = get_event_info_from_cms(self.request, event_id)
        logger.info(event_extra_info)

        e = DBSession.query(c_models.Event).filter_by(id=event_id).first()
        if e is None:
            raise NoEventError("No such event (%d)" % event_id)
        # 日程,会場,検索項目のコンボ用
        dates = sorted(list(set([p.start_on.strftime("%Y-%m-%d %H:%M") for p in e.performances])))
        logger.debug("dates:%s" % dates)
        performances = api.performance_names(self.request, context.event, context.normal_sales_segment)
        if not performances:
            raise NoEventError # NoPerformanceを作る

        from collections import OrderedDict
        select_venues = OrderedDict()
        for pname, pvs in performances:
            select_venues[pname] = []
        event = self.request.context.event
        for pname, pvs in performances:
            for pv in pvs:
                #select_venues[pname] = select_venues.get(pname, [])
                logger.debug("performance %s" % pv)
                sales_segment_id = (sales_counter_sales_segment.id 
                            if pv['on_the_day'] else normal_sales_segment.id)
                select_venues[pname].append(dict(
                    id=pv['pid'],
                    name=u'{start:%Y-%m-%d %H:%M}開始 {vname} {on_the_day}'.format(**pv),
                    order_url=self.request.route_url("cart.order", 
                        sales_segment_id=sales_segment_id),
                    seat_types_url=self.request.route_url('cart.seat_types',
                        performance_id=pv['pid'],
                        sales_segment_id=sales_segment_id,
                        event_id=event.id)))
            
        logger.debug("venues %s" % select_venues)

        # 会場
        venues = set([p.venue.name for p in e.performances])


        logger.debug('performance selections : %s' % performances)
        if not performance_id:
            # GETパラメータ指定がなければ、選択肢の1つ目を採用
            performance_id = performances[0][1][0]['pid']
        selected_performance = c_models.Performance.query.filter(
            c_models.Performance.id==performance_id
        ).filter(
            c_models.Performance.event_id==event_id
        ).first()
        if selected_performance is None and 'performance' in self.request.params:
            return HTTPFound(location=self.request.path_url)


        event = dict(id=e.id, code=e.code, title=e.title, abbreviated_title=e.abbreviated_title,
            sales_start_on=str(e.sales_start_on), sales_end_on=str(e.sales_end_on), venues=venues, product=e.products, )

        return dict(event=event,
                    dates=dates,
                    cart_release_url=self.request.route_url('cart.release'),
                    selected=Markup(json.dumps([selected_performance.name, selected_performance.id])),
                    venues_selection=Markup(json.dumps(select_venues.items())),
                    sales_segment=Markup(json.dumps(dict(id=normal_sales_segment.id, seat_choice=normal_sales_segment.seat_choice))),
                    products_from_selected_date_url = self.request.route_url("cart.date.products", event_id=event_id), 
                    order_url=self.request.route_url("cart.order", sales_segment_id=normal_sales_segment.id),
                    upper_limit=normal_sales_segment.upper_limit,
                    event_extra_info=event_extra_info.get("event") or []
        )

    @view_config(route_name='cart.seat_types', renderer="json")
    def get_seat_types(self):
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        sales_segment_id = self.request.matchdict['sales_segment_id']

        seat_type_triplets = get_seat_type_triplets(event_id, performance_id, sales_segment_id)
        performance = c_models.Performance.query.filter_by(id=performance_id).one()
        data = dict(seat_types=[
                dict(id=s.id, name=s.name,
                    style=s.style,
                    products_url=self.request.route_url('cart.products',
                        event_id=event_id, performance_id=performance_id, sales_segment_id=sales_segment_id, seat_type_id=s.id),
                    availability=available > 0,
                    availability_text=h.get_availability_text(available),
                    quantity_only=s.quantity_only,
                    )
                for s, total, available in seat_type_triplets
                ],
                event_name=performance.event.title,
                performance_name=performance.name,
                performance_start=h.performance_date(performance),
                performance_id=performance_id,
                order_url=self.request.route_url("cart.order", 
                        sales_segment_id=sales_segment_id),
                venue_name=performance.venue.name,
                event_id=event_id,
                venue_id=performance.venue.id,
                data_source=dict(
                    venue_drawing=self.request.route_url(
                        'cart.venue_drawing',
                        event_id=event_id,
                        performance_id=performance_id,
                        venue_id=performance.venue.id,
                        part='__part__'),
                    seats=self.request.route_url(
                        'cart.seats',
                        event_id=event_id,
                        performance_id=performance_id,
                        venue_id=performance.venue.id),
                    seat_adjacencies=self.request.application_url \
                        + api.get_route_pattern(
                          self.request.registry,
                          'cart.seat_adjacencies')
                    )
                )
        return data

    @view_config(route_name="cart.date.products", renderer="json")
    def get_products_with_date(self):
        """ 公演日ごとの購入単位
        (event_id, venue, date) -> [performance] -> [productitems] -> [product]

        need: request.GET["selected_date"] # e.g. format: 2011-11-11
        """

        selected_date_string = self.request.GET["selected_date"]
        event_id = self.request.matchdict["event_id"]

        logger.debug("event_id = %(event_id)s, selected_date = %(selected_date)s"
            % dict(event_id=event_id, selected_date=selected_date_string))

        selected_date = datetime.strptime(selected_date_string, "%Y-%m-%d %H:%M")

        ## selected_dateが==で良いのはself.__call__で指定された候補を元に選択されるから
        q = DBSession.query(c_models.ProductItem.product_id)
        q = q.filter(c_models.Performance.event_id==event_id)
        q = q.filter(c_models.Performance.start_on==selected_date)
        q = q.filter(c_models.Performance.id == c_models.ProductItem.performance_id)


        query = DBSession.query(c_models.Product)
        query = query.filter(c_models.Product.id.in_(q)).order_by(sa.desc("display_order, price"))
        ### filter by salessegment
        salessegment = self.context.get_sales_segument()
        query = h.products_filter_by_salessegment(query, salessegment)


        products = [dict(name=p.name, price=h.format_number(p.price, ","), id=p.id)
                    for p in query]
        return dict(selected_date=selected_date_string, 
                    products=products)

    @view_config(route_name='cart.products', renderer="json")
    def get_products(self):
        """ 席種別ごとの購入単位 
        SeatType -> ProductItem -> Product
        """
        seat_type_id = self.request.matchdict['seat_type_id']
        performance_id = self.request.matchdict['performance_id']
        sales_segment_id = self.request.matchdict['sales_segment_id']
       
        logger.debug("seat_typeid = %(seat_type_id)s, performance_id = %(performance_id)s"
            % dict(seat_type_id=seat_type_id, performance_id=performance_id))

        seat_type = DBSession.query(c_models.StockType).filter_by(id=seat_type_id).one()

        q = DBSession.query(c_models.ProductItem.product_id)
        q = q.filter(c_models.ProductItem.stock_id==c_models.Stock.id)
        q = q.filter(c_models.Stock.stock_type_id==seat_type_id)
        q = q.filter(c_models.ProductItem.performance_id==performance_id)

        query = DBSession.query(c_models.Product)
        query = query.filter(c_models.Product.id.in_(q)).order_by(sa.desc("display_order, price"))
        ### filter by salessegment
        salessegment = DBSession.query(c_models.SalesSegment).filter_by(id=sales_segment_id).one()
        query = h.products_filter_by_salessegment(query, salessegment)

        products = [dict(id=p.id, 
                         name=p.name, 
                         price=h.format_number(p.price, ","), 
                         unit_template=h.build_unit_template(p, performance_id),
                         quantity_power=p.get_quantity_power(seat_type, performance_id))
            for p in query]

        return dict(products=products,
                    seat_type=dict(id=seat_type.id, name=seat_type.name),
                    sales_segment=dict(
                        start_at=salessegment.start_at.strftime("%Y-%m-%d %H:%M"),
                        end_at=salessegment.end_at.strftime("%Y-%m-%d %H:%M")
                    ))

    @view_config(route_name='cart.seats', renderer="json")
    def get_seats(self):
        """会場&座席情報""" 
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        venue_id = self.request.matchdict['venue_id']
        stock_holder = api.get_stock_holder(self.request, event_id)
        logger.debug("stock holder is %s:%s" % (stock_holder.id, stock_holder.name))
        venue = c_models.Venue.get(venue_id)
        return dict(
            seats=dict(
                (
                    seat.l0_id,
                    dict(
                        id=seat.l0_id,
                        stock_type_id=seat.stock.stock_type_id,
                        stock_holder_id=seat.stock.stock_holder_id,
                        status=seat.status,
                        areas=[area.id for area in seat.areas],
                        is_hold=seat.stock.stock_holder_id==stock_holder.id,
                        )
                    ) 
                for seat in DBSession.query(c_models.Seat) \
                            .options(joinedload('areas'),
                                     joinedload('status_')) \
                            .filter_by(venue_id=venue_id)
                ),
            areas=dict(
                (area.id, { 'id': area.id, 'name': area.name }) \
                for area in DBSession.query(c_models.VenueArea) \
                            .join(c_models.VenueArea_group_l0_id) \
                            .filter(c_models.VenueArea_group_l0_id.venue_id==venue_id)
                ),
            info=dict(
                available_adjacencies=[
                    adjacency_set.seat_count
                    for adjacency_set in \
                        DBSession.query(c_models.SeatAdjacencySet) \
                        .filter_by(venue_id=venue_id)
                    ]
                ),
            pages=venue.site._metadata and venue.site._metadata.get('pages')
            )

    @view_config(route_name='cart.seat_adjacencies', renderer="json")
    def get_seat_adjacencies(self):
        """連席情報""" 
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        venue_id = self.request.matchdict['venue_id']
        length_or_range = self.request.matchdict['length_or_range']
        return dict(
            seat_adjacencies={
                length_or_range: [
                    [seat.l0_id for seat in seat_adjacency.seats]
                    for seat_adjacency_set in \
                        DBSession.query(c_models.SeatAdjacencySet) \
                        .options(joinedload("adjacencies"),
                                 joinedload('adjacencies.seats')) \
                        .filter_by(venue_id=venue_id,
                                   seat_count=length_or_range)
                    for seat_adjacency in seat_adjacency_set.adjacencies 
                    ]
                }
            )

    @view_config(route_name="cart.venue_drawing", request_method="GET")
    def get_venue_drawing(self):
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        venue_id = self.request.matchdict.get('venue_id')
        if not venue_id:
            raise HTTPNotFound()
        part = self.request.matchdict.get('part')
        venue = c_models.Venue.get(venue_id)
        return Response(body=venue.site.get_drawing(part).stream().read(), content_type='text/xml; charset=utf-8')

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
        :return: list of tuple(ticketing.products.models.Product, int)
        """

        controls = list(self.iter_ordered_items())
        logger.debug('order %s' % controls)
        if len(controls) == 0:
            return []

        products = dict([(p.id, p) for p in DBSession.query(c_models.Product).filter(c_models.Product.id.in_([c[0] for c in controls]))])
        logger.debug('order %s' % products)

        return [(products.get(int(c[0])), c[1]) for c in controls]

    @view_config(route_name='cart.order', request_method="POST", renderer='json')
    def reserve(self):
        order_items = self.ordered_items
        if not order_items:
            return dict(result='NG', reason="no products")

        performance = c_models.Performance.get(self.request.params['performance_id'])
        if not order_items:
            return dict(result='NG', reason="no performance")

        selected_seats = self.request.params.getall('selected_seat')
        logger.debug('order_items %s' % order_items)

        sum_quantity = 0
        if selected_seats:
            sum_quantity = len(selected_seats)
        else:
            for product, quantity in order_items:
                sum_quantity += quantity
        logger.debug('sum_quantity=%s' % sum_quantity)

        self.context.event_id = performance.event_id
        sales_segment = self.context.get_sales_segument()
        if sales_segment.upper_limit < sum_quantity:
            logger.debug('upper_limit over')
            return dict(result='NG', reason="upper_limit")

        try:
            cart = api.order_products(self.request, self.request.params['performance_id'], order_items, selected_seats=selected_seats)
            if cart is None:
                transaction.abort()
                return dict(result='NG')
        except NotEnoughAdjacencyException:
            transaction.abort()
            logger.debug("not enough adjacency")
            return dict(result='NG', reason="adjacency")
        except InvalidSeatSelectionException:
            transaction.abort()
            logger.debug("seat selection is invalid.")
            return dict(result='NG', reason="invalid seats")
        except NotEnoughStockException as e:
            transaction.abort()
            logger.debug("not enough stock quantity :%s" % e)
            return dict(result='NG', reason="stock")

        DBSession.add(cart)
        DBSession.flush()
        api.set_cart(self.request, cart)
        return dict(result='OK', 
                    payment_url=self.request.route_url("cart.payment", sales_segment_id=sales_segment.id),
                    cart=dict(products=[dict(name=p.product.name, 
                                             quantity=p.quantity,
                                             price=int(p.product.price),
                                             seats=p.seats,
                                        ) 
                                        for p in cart.products],
                              total_amount=h.format_number(cart.tickets_amount),
                    ))

    @view_config(route_name='cart.order', request_method="GET", renderer=selectable_renderer('carts_mobile/%(membership)s/reserve.html'), request_type=".interfaces.IMobileRequest")
    def reserve_mobile(self):
        cart = api.get_cart(self.request)
        if not cart:
            raise NotFound

        performance_id = self.request.params.get('performance_id')
        seat_type_id = self.request.params.get('seat_type_id')
        sales_segment_id = self.request.matchdict["sales_segment_id"]

        # セールスセグメント必須
        sales_segment = c_models.SalesSegment.filter_by(id=sales_segment_id).first()

        performance = c_models.Performance.query.filter(
            c_models.Performance.id==performance_id).first()
        if performance:
            event = performance.event
        else:
            event = None

        data = dict(
            event=event,
            performance=performance, 
            seat_type_id=seat_type_id,
            sales_segment_id=sales_segment_id, 
            payment_url=self.request.route_url("cart.payment", sales_segment_id=sales_segment.id),
            cart=dict(products=[dict(name=p.product.name, 
                                     quantity=p.quantity,
                                     price=int(p.product.price),
                                     seats=p.seats,
                                ) 
                                for p in cart.products],
                      total_amount=h.format_number(cart.tickets_amount),
            ))
        return data

    @view_config(route_name='cart.products', renderer=selectable_renderer('carts_mobile/%(membership)s/products.html'), xhr=False, request_type=".interfaces.IMobileRequest", request_method="POST")
    def products_form(self):
        """商品の値検証とおまかせ座席確保とカート作成
        """
        performance_id = self.request.params.get('performance_id')
        seat_type_id = self.request.params.get('seat_type_id')
        sales_segment_id = self.request.matchdict["sales_segment_id"]

        # セールスセグメント必須
        sales_segment = c_models.SalesSegment.filter_by(id=sales_segment_id).first()
        if sales_segment is None:
            raise NoEventError("No matching sales_segment")

        # パフォーマンス
        performance = c_models.Performance.query.filter(
            c_models.Performance.id==performance_id).first()
        if performance is None:
            raise NoEventError("No such performance (%d)" % performance_id)

        # CSRFトークンの確認
        form = schemas.CSRFSecureForm(
            formdata=self.request.params,
            csrf_context=self.request.session)
        if not form.validate():
            raise InvalidCSRFTokenException
        # セッションからCSRFトークンを削除して再利用不可にしておく
        if 'csrf' in self.request.session:
            del self.request.session['csrf']

        order_items = self.ordered_items

        # 購入枚数の制限
        sum_quantity = sum(num for product, num in order_items)
        logger.debug('sum_quantity=%s' % sum_quantity)
        if sum_quantity > sales_segment.upper_limit:
            raise OverQuantityLimitError(sales_segment.upper_limit)

        if sum_quantity == 0:
            raise ZeroQuantityError

        # 古いカートを削除
        old_cart = api.get_cart(self.request)
        if old_cart:
            old_cart.release()
            api.remove_cart(self.request)

        try:
            # カート生成(席はおまかせ)
            cart = api.order_products(
                self.request,
                performance_id,
                order_items)
            if cart is None:
                transaction.abort()
                logger.debug("cart is None. aborted.")
                raise CartCreationExceptoion
        except NotEnoughAdjacencyException as e:
            transaction.abort()
            logger.debug("not enough adjacency")
            raise e
        except InvalidSeatSelectionException as e:
            # モバイルだとここにはこないかも
            transaction.abort()
            logger.debug("seat selection is invalid.")
            raise e
        except NotEnoughStockException as e:
            transaction.abort()
            logger.debug("not enough stock quantity :%s" % e)
            raise e

        DBSession.add(cart)
        DBSession.flush()
        api.set_cart(self.request, cart)
        # 購入確認画面へ
        query = dict(
            performance_id=performance_id,
            event_id=performance.event_id,
            seat_type_id=seat_type_id,
        )
        return HTTPFound(self.request.route_url('cart.order', sales_segment_id=sales_segment.id, _query=query))

    def __call__(self):
        """
        TODO: 使われていない？
        座席情報から座席グループを検索する
        """
        sales_segment = self.context.get_sales_segument()

        #seat_type_id = self.request.matchdict['seat_type_id']
        cart = self.context.order_products(self.request.params['performance_id'], self.ordered_items)
        if cart is None:
            return dict(result='NG')
        api.set_cart(self.request, cart)
        #self.request.session['ticketing.cart_id'] = cart.id
        #self.cart = cart
        return dict(result='OK', 
                    payment_url=self.request.route_url("cart.payment", sales_segment_id=sales_segment.id),
                    cart=dict(products=[dict(name=p.product.name, 
                                             quantity=p.quantity,
                                             price=int(p.product.price),
                                        ) 
                                        for p in cart.products],
                              total_amount=h.format_number(cart.tickets_amount),
                    ))

    def on_error(self):
        """ 座席確保できなかった場合
        """

class ReleaseCartView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='cart.release', request_method="POST", renderer="json")
    def __call__(self):
        cart = api.get_cart(self.request)
        cart.release()
        api.remove_cart(self.request)

        return dict()


class PaymentView(object):
    """ 支払い方法、引き取り方法選択 """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='cart.payment', request_method="GET", renderer=selectable_renderer("carts/%(membership)s/payment.html"))
    @view_config(route_name='cart.payment', request_type='.interfaces.IMobileRequest', request_method="GET", renderer=selectable_renderer("carts_mobile/%(membership)s/payment.html"))
    def __call__(self):
        """ 支払い方法、引き取り方法選択
        """
        if not api.has_cart(self.request):
            raise NoCartError()
        cart = api.get_cart(self.request)
        self.context.event_id = cart.performance.event.id

        start_on = cart.performance.start_on
        payment_delivery_methods = self.context.get_payment_delivery_method_pair(start_on=start_on)
        user = self.context.get_or_create_user()
        user_profile = None
        if user is not None:
            user_profile = user.user_profile

        if user_profile is not None:
            formdata = MultiDict(
                last_name=user_profile.last_name,
                last_name_kana=user_profile.last_name_kana,
                first_name=user_profile.first_name,
                first_name_kana=user_profile.first_name_kana,
                tel=user_profile.tel_1,
                fax=getattr(user_profile, "fax", None), 
                zip=user_profile.zip,
                prefecture=user_profile.prefecture,
                city=user_profile.city,
                address_1=user_profile.address_1,
                address_2=user_profile.address_2,
                mail_address=user_profile.email
                )
        else:
            formdata = None

        form = schemas.ClientForm(formdata=formdata)
        return dict(form=form,
            payment_delivery_methods=payment_delivery_methods,
            #user=user, user_profile=user.user_profile,
            )

    def validate(self, payment_delivery_pair):
        form = schemas.ClientForm(formdata=self.request.params)
        if form.validate() and payment_delivery_pair:
            return None 
        else:
            return form

    @view_config(route_name='cart.payment', request_method="POST", renderer=selectable_renderer("carts/%(membership)s/payment.html"))
    @view_config(route_name='cart.payment', request_type='.interfaces.IMobileRequest', request_method="POST", renderer=selectable_renderer("carts_mobile/%(membership)s/payment.html"))
    def post(self):
        """ 支払い方法、引き取り方法選択
        """

        params = self.request.params
        if not api.has_cart(self.request):
            raise NoCartError()
        cart = api.get_cart(self.request)

        user = self.context.get_or_create_user()

        payment_delivery_method_pair_id = self.request.params.get('payment_delivery_method_pair_id', 0)
        payment_delivery_pair = c_models.PaymentDeliveryMethodPair.query.filter_by(id=payment_delivery_method_pair_id).first()
        form = self.validate(payment_delivery_pair)

        if not payment_delivery_pair or form:
            if not payment_delivery_pair:
                self.request.session.flash(u"お支払い方法／受け取り方法をどれかひとつお選びください")
                logger.debug("invalid : %s" % 'payment_delivery_method_pair_id')
            else:
                logger.debug("invalid : %s" % form.errors)

            self.context.event_id = cart.performance.event.id

            start_on = cart.performance.start_on
            payment_delivery_methods = self.context.get_payment_delivery_method_pair(start_on=start_on)

            return dict(form=form,
                payment_delivery_methods=payment_delivery_methods,
                #user=user, user_profile=user.user_profile,
                )

        cart.payment_delivery_pair = payment_delivery_pair
        cart.system_fee = payment_delivery_pair.system_fee

        shipping_address = self.create_shipping_address(user)

        DBSession.add(shipping_address)
        cart.shipping_address = shipping_address
        DBSession.add(cart)

        client_name = self.get_client_name()

        order = dict(
            client_name=client_name,
            payment_delivery_method_pair_id=payment_delivery_method_pair_id,
            mail_address=shipping_address.email,
        )
        self.request.session['order'] = order

        payment_delivery_plugin = api.get_payment_delivery_plugin(self.request, 
            payment_delivery_pair.payment_method.payment_plugin_id,
            payment_delivery_pair.delivery_method.delivery_plugin_id,)
        if payment_delivery_plugin is not None:
            res = payment_delivery_plugin.prepare(self.request, cart)
            if res is not None and callable(res):
                return res
        else:
            payment_plugin = api.get_payment_plugin(self.request, payment_delivery_pair.payment_method.payment_plugin_id)
            res = payment_plugin.prepare(self.request, cart)
            if res is not None and callable(res):
                return res
        return HTTPFound(self.request.route_url("payment.confirm"))

    def get_client_name(self):
        return self.request.params['last_name'] + self.request.params['first_name']

    def create_shipping_address(self, user):
        params = self.request.params
        shipping_address = c_models.ShippingAddress(
            first_name=params['first_name'],
            last_name=params['last_name'],
            first_name_kana=params['first_name_kana'],
            last_name_kana=params['last_name_kana'],
            zip=params['zip'],
            prefecture=params['prefecture'],
            city=params['city'],
            address_1=params['address_1'],
            address_2=params['address_2'],
            #country=params['country'],
            country=u"日本国",
            tel_1=params['tel'],
            #tel_2=params['tel_2'],
            fax=params.get('fax'),
            user=user,
            email=params['mail_address']
        )
        return shipping_address


class ConfirmView(object):
    """ 決済確認画面 """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='payment.confirm', request_method="GET", renderer=selectable_renderer("carts/%(membership)s/confirm.html"))
    @view_config(route_name='payment.confirm', request_type='.interfaces.IMobileRequest', request_method="GET", renderer=selectable_renderer("carts_mobile/%(membership)s/confirm.html"))
    def get(self):
        form = schemas.CSRFSecureForm(csrf_context=self.request.session)
        if not api.has_cart(self.request):
            raise NoCartError()
        cart = api.get_cart(self.request)

        magazines = u_models.MailMagazine.query.outerjoin(u_models.MailSubscription) \
            .filter(u_models.MailMagazine.organization==cart.performance.event.organization) \
            .all()

        user = self.context.get_or_create_user()
        return dict(cart=cart, mailmagazines=magazines, 
            #user=user, 
            form=form,
            )


class CompleteView(object):
    """ 決済完了画面"""
    def __init__(self, request):
        self.request = request
        self.context = request.context
        # TODO: Orderを表示？

    @back
    @view_config(route_name='payment.finish', renderer=selectable_renderer("carts/%(membership)s/completion.html"), request_method="POST")
    @view_config(route_name='payment.finish', request_type='.interfaces.IMobileRequest', renderer=selectable_renderer("carts_mobile/%(membership)s/completion.html"), request_method="POST")
    def __call__(self):
        form = schemas.CSRFSecureForm(formdata=self.request.params, csrf_context=self.request.session)
        form.validate()
        #assert not form.csrf_token.errors
        if not api.has_cart(self.request):
            raise NoCartError()

        cart = api.get_cart(self.request)
        if not cart.is_valid():
            raise NoCartError()

        order_session = self.request.session['order']

        payment_delivery_method_pair_id = order_session['payment_delivery_method_pair_id']
        payment_delivery_pair = c_models.PaymentDeliveryMethodPair.query.filter(
            c_models.PaymentDeliveryMethodPair.id==payment_delivery_method_pair_id
        ).one()

        payment_delivery_plugin = api.get_payment_delivery_plugin(self.request, 
            payment_delivery_pair.payment_method.payment_plugin_id,
            payment_delivery_pair.delivery_method.delivery_plugin_id,)
        if payment_delivery_plugin is not None:
            order = payment_delivery_plugin.finish(self.request, cart)

            user = self.context.get_or_create_user()
            order.user = user
            order.organization_id = order.performance.event.organization_id
            cart.order = order
        else:
            payment_plugin = api.get_payment_plugin(self.request, payment_delivery_pair.payment_method.payment_plugin_id)
            order = payment_plugin.finish(self.request, cart)

            user = self.context.get_or_create_user()
            order.user = user
            order.organization_id = order.performance.event.organization_id
            cart.order = order

            DBSession.add(order)
            delivery_plugin = api.get_delivery_plugin(self.request, payment_delivery_pair.delivery_method.delivery_plugin_id)
            delivery_plugin.finish(self.request, cart)

        notify_order_completed(self.request, order)

        # メール購読でエラーが出てロールバックされても困る
        order_id = order.id
        mail_address = cart.shipping_address.email
        plain_user = self.context.get_or_create_user()
        user_id = None
        if plain_user is not None:
            user_id = plain_user.id
            user_cls = plain_user.__class__
        transaction.commit()
        user = None
        if user_id is not None:
            user = DBSession.query(user_cls).get(user_id)
        order = DBSession.query(order.__class__).get(order_id)
 
        # メール購読
        self.save_subscription(user, mail_address)
        api.remove_cart(self.request)

        api.logout(self.request)
        return dict(order=order)


    def save_subscription(self, user, mail_address):
        magazines = u_models.MailMagazine.query.all()

        # 購読
        magazine_ids = self.request.params.getall('mailmagazine')
        logger.debug("magazines: %s" % magazine_ids)
        for subscription in u_models.MailMagazine.query.filter(u_models.MailMagazine.id.in_(magazine_ids)).all():
            if subscription.subscribe(user, mail_address):
                logger.debug("User %s starts subscribing %s for <%s>" % (user, subscription.name, mail_address))
            else:
                logger.debug("User %s is already subscribing %s for <%s>" % (user, subscription.name, mail_address))


class InvalidMemberGroupView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(context='.authorization.InvalidMemberGroupException')
    def __call__(self):
        event_id = self.context.event_id
        event = c_models.Event.query.filter(c_models.Event.id==event_id).one()
        location = api.get_valid_sales_url(self.request, event)
        logger.debug('url: %s ' % location)
        return HTTPFound(location=location)


class MobileIndexView(object):
    """モバイルのパフォーマンス選択
    """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='cart.index.sales', renderer=selectable_renderer('carts_mobile/%(membership)s/index.html'), xhr=False, permission="buy", request_type=".interfaces.IMobileRequest")
    def __call__(self):
        event_id = self.request.matchdict['event_id']
        venue_name = self.request.params.get('v')

        # セールスセグメント必須
        sales_segment = self.context.get_sales_segument()

        if sales_segment is None:
            raise NoEventError("No matching sales_segment")

        # パフォーマンスIDが確定しているなら商品選択へリダイレクト
        performance_id = self.request.params.get('pid') or self.request.params.get('performance')
        if performance_id:
            return HTTPFound(self.request.route_url(
                "cart.seat_types",
                event_id=event_id,
                performance_id=performance_id,
                sales_segment_id=sales_segment.id))

        event = c_models.Event.query.filter(c_models.Event.id==event_id).first()
        if event is None:
            raise NoEventError("No such event (%d)" % event_id)

        #if venue_name:
        #    venue = c_models.Venue.query.filter(c_models.Venue.name==venue_name).first()
        #    if venue is None:
        #        logger.debug("No such venue venue_name=%s" % venue_name)
        #else:
        #    venue = None
        ## 会場が指定されていなければ会場を選択肢を作る
        #if venue:
        #    venues = []
        #    # 会場が確定しているならパフォーマンスの選択肢を作る
        #    performances_query = c_models.Performance.query \
        #        .filter(c_models.Performance.event_id==event_id)
        #    performances = [dict(id=p.id, start_on=p.start_on.strftime('%Y-%m-%d %H:%M')) \
        #        for p in performances_query if p.venue.name==venue_name]
        #else:
        #    # 会場は会場名で一意にする
        #    venues = set(performance.venue.name for performance in event.performances)
        #    performances = []

        # 公演名リスト
        perms = api.performance_names(self.request, event, sales_segment)
        performances = [p[0] for p in perms]
        logger.debug('performances %s' % performances)

        # 公演名が指定されている場合は、（日時、会場）のリスト
        performance_name = self.request.params.get('performance_name')
        venues = []
        if performance_name:
            venues = [(x['pid'], u"{start:%Y-%m-%d %H:%M} {vname}".format(**x)) for x in api.performance_venue_by_name(self.request, event, sales_segment, performance_name)]

        return dict(
            event=event,
            sales_segment=sales_segment,
            #venue=venue,
            venues=venues,
            performances=performances,
            performance_name=performance_name,
        )


class MobileSelectProductView(object):
    """モバイルの商品選択
    """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='cart.seat_types', renderer=selectable_renderer('carts_mobile/%(membership)s/seat_types.html'), xhr=False, request_type=".interfaces.IMobileRequest")
    def __call__(self):
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        sales_segment_id = self.request.matchdict['sales_segment_id']
        seat_type_id = self.request.params.get('stid')

        if seat_type_id:
            return HTTPFound(self.request.route_url(
                "cart.products",
                event_id=event_id,
                performance_id=performance_id,
                sales_segment_id=sales_segment_id,
                seat_type_id=seat_type_id))

        # セールスセグメント必須
        sales_segment = self.context.get_sales_segument()
        if sales_segment is None:
            raise NoEventError("No matching sales_segment")

        event = c_models.Event.query.filter(c_models.Event.id==event_id).first()
        if event is None:
            raise NoEventError("No such event (%d)" % event_id)

        performance = c_models.Performance.query.filter(
            c_models.Performance.id==performance_id).filter(
            c_models.Performance.event_id==event.id).first()
        if performance is None:
            raise NoEventError("No such performance (%d)" % performance_id)

        seat_type_triplets = get_seat_type_triplets(event.id, performance.id, sales_segment.id)            

        data = dict(
            seat_types=[
                dict(id=s.id, name=s.name,
                     style=s.style,
                     products_url=self.request.route_url('cart.products',
                                                         event_id=event_id, performance_id=performance_id, sales_segment_id=sales_segment.id, seat_type_id=s.id),
                     availability=available > 0,
                     availability_text=h.get_availability_text(available),
                     quantity_only=s.quantity_only,
                     )
            for s, total, available in seat_type_triplets
            ],
            event=event,
            performance=performance,
            venue=performance.venue,
        )
        return data

    @view_config(route_name='cart.products', renderer=selectable_renderer('carts_mobile/%(membership)s/products.html'), xhr=False, request_type=".interfaces.IMobileRequest")
    def products(self):
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        seat_type_id = self.request.matchdict['seat_type_id']
        sales_segment_id = self.request.matchdict['sales_segment_id']

        # イベント
        event = c_models.Event.query.filter(c_models.Event.id==event_id).first()
        if event is None:
            raise NoEventError("No such event (%d)" % event_id)

        # パフォーマンス(イベントにひもづいてること)
        performance = c_models.Performance.query.filter(
            c_models.Performance.id==performance_id).filter(
            c_models.Performance.event_id==event.id).first()
        if performance is None:
            raise NoEventError("No such performance (%d)" % performance_id)

        sales_segment = c_models.SalesSegment.query.filter(
            c_models.SalesSegment.id==sales_segment_id,
            c_models.SalesSegment.event_id==event.id).first()
        if sales_segment is None:
            raise NoEventError("No such sales segment (%s)" % sales_segment_id)
        

        # 席種(イベントとパフォーマンスにひもづいてること)
        segment_stocks = DBSession.query(c_models.ProductItem.stock_id).filter(
            c_models.ProductItem.product_id==c_models.Product.id).filter(
            c_models.Product.sales_segment_id==sales_segment.id)

        seat_type = DBSession.query(c_models.StockType).filter(
            c_models.Performance.event_id==event_id).filter(
            c_models.Performance.id==performance_id).filter(
            c_models.Performance.event_id==c_models.StockHolder.event_id).filter(
            c_models.StockHolder.id==c_models.Stock.stock_holder_id).filter(
            c_models.Stock.stock_type_id==c_models.StockType.id).filter(
            c_models.Stock.id.in_(segment_stocks)).filter(
            c_models.StockType.id==seat_type_id).first()

        if seat_type is None:
            raise NoEventError("No such seat_type (%s)" % seat_type_id)

        # 商品一覧
        # サブクエリの部分
        product_items = DBSession.query(c_models.ProductItem.product_id).filter(
            c_models.ProductItem.stock_id==c_models.Stock.id).filter(
            c_models.Stock.stock_type_id==seat_type_id).filter(
            c_models.ProductItem.performance_id==performance_id)

        products = c_models.Product.query.filter(
            c_models.Product.id.in_(product_items)).order_by(
            sa.desc("display_order, price")).filter_by(
            sales_segment=sales_segment)

        # CSRFトークン発行
        form = schemas.CSRFSecureForm(csrf_context=self.request.session)

        data = dict(
            event=event,
            performance=performance,
            venue=performance.venue,
            seat_type=seat_type,
            upper_limit=sales_segment.upper_limit,
            products=[
                dict(
                    id=product.id,
                    name=product.name,
                    detail=h.product_name_with_unit(product, performance_id),
                    price=h.format_number(product.price, ","),
                )
                for product in products
            ],
            form=form,
        )
        return data

class OutTermSalesView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(context='.exceptions.OutTermSalesException', renderer=selectable_renderer('ticketing.cart:templates/carts/%(membership)s/out_term_sales.html'))
    def pc(self):
        api.logout(self.request)
        return dict(event=self.context.event, 
                    sales_segment=self.context.sales_segment)

    @view_config(context='.exceptions.OutTermSalesException', renderer=selectable_renderer('ticketing.cart:templates/carts_mobile/%(membership)s/out_term_sales.html'), 
        request_type=".interfaces.IMobileRequest")
    def mobile(self):
        api.logout(self.request)
        return dict(event=self.context.event, 
                    sales_segment=self.context.sales_segment)

@view_config(route_name='cart.logout')
def logout(request):
    headers = security.forget(request)
    res = HTTPFound(location='/')
    res.headerlist.extend(headers)
    return res
