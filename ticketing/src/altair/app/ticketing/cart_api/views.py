# -*- coding:utf-8 -*-
import logging
import transaction
from collections import namedtuple

from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql import not_, or_, func, distinct

from datetime import date, datetime, time

from altair.sqlahelper import get_db_session

from altair.app.ticketing.core.models import (
    ChannelEnum,
    StockType,
    Seat,
    Stock,
    StockType,
    SeatStatus,
    SeatStatusEnum,
    Product,
    ProductItem,
    SalesSegment,
    StockStatus,
    Performance,
    SeatAdjacency,
    SeatAdjacencySet,
    Seat_SeatAdjacency
)
from altair.app.ticketing.cart.models import (
    Cart,
    CartedProduct,
    CartedProductItem
)
from altair.app.ticketing.cart.exceptions import OutTermSalesException, NoPerformanceError
from altair.app.ticketing.cart.exceptions import (
    PerProductProductQuantityOutOfBoundsError,
    QuantityOutOfBoundsError,
    AuthenticationError,
    ProductQuantityOutOfBoundsError,
    PerStockTypeQuantityOutOfBoundsError,
    PerStockTypeProductQuantityOutOfBoundsError
)
from altair.app.ticketing.cart import api
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.cart import view_support
from altair.app.ticketing.cart.reserving import NotEnoughAdjacencyException, InvalidSeatSelectionException
from altair.app.ticketing.cart.stocker import NotEnoughStockException
from altair.app.ticketing.cart.helpers import get_availability_text

from .view_support import get_filtered_stock_types, search_seat, parse_fields_params, get_spa_svg_urls, search_seatGroup

logger = logging.getLogger(__name__)


def check_auth(fn):
    def _check(context, request):
        if context.cart_setting.auth_type:
            user_info = context.authenticated_user()
            if "user_id" not in user_info:
                raise AuthenticationError
        return fn(context, request)
    return _check


@view_defaults(decorator=check_auth, renderer='json')
class CartAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='cart.api.health_check')
    def health_check(self):
        return HTTPNotFound()

    @view_config(route_name='cart.api.index')
    def index(self):
        return dict(status='OK')

    @view_config(route_name='cart.api.performances')
    def performances(self):
        available_sales_segments = self.context.available_sales_segments
        available_ss_per_perfromance = {}
        for ss in available_sales_segments:
            if ss.performance not in available_ss_per_perfromance.keys():
                available_ss_per_perfromance[ss.performance] = [ss]
            else:
                available_ss_per_perfromance[ss.performance].append(ss)
        return dict(
            performances=[dict(
                performance_id=p.id,
                performance_name=p.name,
                open_on=p.open_on,
                start_on=p.start_on,
                end_on=p.end_on,
                venue_id=p.venue.id,
                venue_name=p.venue.name,
                sales_segments=[dict(
                    sales_segment_id=ss.id,
                    sales_segment_name=ss.sales_segment_group.name
                ) for ss in available_ss_per_perfromance[p]]
            ) for p in available_ss_per_perfromance.keys()]
        )

    @view_config(route_name='cart.api.performance')
    def performance(self):
        performance = self.context.performance
        if performance is None:
            raise HTTPNotFound('performance_id={} not found'.format(self.request.matchdict.get('performance_id')))

        available_sales_segments = self.context.available_sales_segments

        #SPA用のsvg(s3)を取得して返却
        drawings = get_spa_svg_urls(self.request, performance.id)

        reason = ""
        if 'root' not in drawings:
            reason = "root svg is none "

        if 'mini' not in drawings:
            reason += " mini svg is none "

        if 'seat' not in drawings:
            reason += " seat data is none "

        if reason:
            return {
                "results": {
                    "status": "NG",
                    "reason": reason
                }
            }

        root_map_url = drawings['root']
        mini_map_url = drawings['mini']
        seat_data_url = drawings['seat']
        logger.debug("root_url=%s", root_map_url)
        logger.debug("mini_url=%s", mini_map_url)
        logger.debug("seat_url=%s", seat_data_url)

        reason = ""
        if not root_map_url or not mini_map_url or not seat_data_url:
            reason = "svg map_url & seats_data is none"

        if reason:
            return {
                "results": {
                    "status": "NG",
                    "reason": reason
                }
            }

        return dict(
            performance=dict(
                performance_id=performance.id,
                performance_name=performance.name,
                open_on=performance.open_on,
                start_on=performance.start_on,
                end_on=performance.end_on,
                order_limit=performance.setting.order_limit,
                venue_id=performance.venue.id,
                venue_name=performance.venue.name,
                venue_map_url=root_map_url,
                mini_venue_map_url=mini_map_url,
                seat_data_url=seat_data_url,
            ),
            event=dict(
                event_id=performance.event.id,
                order_limit=performance.event.setting.order_limit,
            ),
            sales_segments=[dict(
                sales_segment_id=ss.id,
                sales_segment_name=ss.sales_segment_group.name,
                start_at=ss.start_at,
                end_at=ss.end_at,
                seat_choice=ss.seat_choice,
                order_limit=ss.order_limit,
                upper_limit=ss.max_quantity,
                product_limit=ss.max_product_quantity
            ) for ss in available_sales_segments]
        )

    @view_config(route_name='cart.api.stock_types')
    def stock_types(self):
        sales_segment = self.context.sales_segment
        seat_type_dicts = view_support.get_seat_type_dicts(self.request, sales_segment)
        return dict(
            stock_types=[dict(
                stock_type_id=st['id'],
                stock_type_name=st['name'],
                is_quantity_only=st['quantity_only'],
                description=st['description'],
                min_quantity=st['min_quantity'],
                max_quantity=st['max_quantity'],
                min_product_quantity=st['min_product_quantity'],
                max_product_quantity=st['max_product_quantity']
            ) for st in seat_type_dicts]
        )

    @view_config(route_name='cart.api.stock_type')
    def stock_type(self):
        sales_segment = self.context.sales_segment
        stock_type_id = self.request.matchdict.get('stock_type_id')
        session = get_db_session(self.request, 'slave')
        try:
            if int(stock_type_id) not in [s.stock_type_id for s in sales_segment.stocks]:
                raise HTTPBadRequest('no stock_type_id({}) has relation with sales_segment({})'.format(stock_type_id, sales_segment.id))
            stock_type = session.query(StockType).filter(StockType.id == stock_type_id).one()
        except NoResultFound as e:
            logger.warning("{} for stock_type_id={}".format(e.message, stock_type_id))
            raise HTTPNotFound()
        products = [p for p in sales_segment.products if p.seat_stock_type_id == int(stock_type_id) and p.public]

        # svg側では描画エリアをregionと定義しているのでそれに合わせる
        int_stock_type_id = int(stock_type_id)
        region_ids = set()
        for s in sales_segment.stocks:
            if s.stock_type_id == int_stock_type_id:
                for region_id in s.drawing_l0_ids:
                    region_ids.add(region_id)

        return dict(
            stock_types=[dict(
                stock_type_id=stock_type.id,
                stock_type_name=stock_type.name,
                is_quantity_only=stock_type.quantity_only,
                description=stock_type.description,
                min_quantity=stock_type.min_quantity,
                max_quantity=stock_type.max_quantity,
                min_product_quantity=stock_type.min_product_quantity,
                max_product_quantity=stock_type.max_product_quantity,
                products=[dict(
                    product_id=product.id,
                    product_name=product.name,
                    price=product.price,
                    min_product_quantity=product.min_product_quantity,
                    max_product_quantity=product.max_product_quantity,
                    is_must_be_chosen=product.must_be_chosen,
                    product_items=[dict(
                        product_item_id=item.id,
                        product_item_name=item.name,
                        price=item.price,
                        sales_unit_quantity=item.quantity
                    ) for item in product.items],
                ) for product in products],
                regions=list(region_ids)
            )]
        )

    @view_config(route_name='cart.api.stock_type.all')
    def stock_type_all(self):
        sales_segment = self.context.sales_segment
        session = get_db_session(self.request, 'slave')
        stock_types = session.query(StockType).filter(StockType.event_id == sales_segment.event_id).all()

        ret_stock_types = {}
        for stock_type in stock_types:
            products = [p for p in sales_segment.products if p.seat_stock_type_id == int(stock_type.id) and p.public]
            # svg側では描画エリアをregionと定義しているのでそれに合わせる
            int_stock_type_id = int(stock_type.id)
            region_ids = set()
            for s in sales_segment.stocks:
                if s.stock_type_id == int_stock_type_id:
                    for region_id in s.drawing_l0_ids:
                        region_ids.add(region_id)
            stock_type_detail = {'products':products,'regions':region_ids}
            ret_stock_types[stock_type] = stock_type_detail
            #公開されている商品がある席種のみ返す
            if len(products) > 0:
                ret_stock_types[stock_type] = stock_type_detail

        return dict(
            stock_types=[dict(
                stock_type_id=stock_type.id,
                stock_type_name=stock_type.name,
                is_quantity_only=stock_type.quantity_only,
                description=stock_type.description,
                min_quantity=stock_type.min_quantity,
                max_quantity=stock_type.max_quantity,
                min_product_quantity=stock_type.min_product_quantity,
                max_product_quantity=stock_type.max_product_quantity,
                products=[dict(
                    product_id=product.id,
                    product_name=product.name,
                    price=product.price,
                    min_product_quantity=product.min_product_quantity,
                    max_product_quantity=product.max_product_quantity,
                    is_must_be_chosen=product.must_be_chosen,
                    product_items=[dict(
                        product_item_id=item.id,
                        product_item_name=item.name,
                        price=item.price,
                        sales_unit_quantity=item.quantity
                    ) for item in product.items],
                ) for product in detail['products']],
                regions=list(detail['regions'])
            ) for stock_type,detail in ret_stock_types.iteritems()]
        )

    @view_config(route_name='cart.api.seats')
    def seats(self):
        session = get_db_session(self.request, 'slave')

        # 必要な項目を指定(fieldsが空の時は全項目を返す)
        fields = parse_fields_params(self.request)

        # available_sales_segmentsは優先順位順にならんでるはず
        sales_segment = [ss for ss in self.context.available_sales_segments][0]

        def status(rest_quantity, all_quantity):
            setting = sales_segment.event.setting
            return get_availability_text(rest_quantity, all_quantity,
                                         setting.middle_stock_threshold, setting.middle_stock_threshold_percent)

        result = get_filtered_stock_types(self.request, sales_segment, session)

        res = dict()
        if 'stock_types' in fields or not fields:
            res['stock_types'] = [dict(
                stock_type_id=st['stock_type_id'],
                available_counts=st['rest_quantity'],
                #total_counts=st['quantity'],
                stock_status=status(
                    st['rest_quantity'],
                    st['quantity']
                )
            ) for st in result['stock_types']]
        if 'regions' in fields or not fields:
            res['regions'] = [dict(
                region_id=r['region_id'],
                available_counts=r['rest_quantity'],
                #total_counts=r['quantity'],
                stock_status=status(
                    r['rest_quantity'],
                    r['quantity']
                )
            ) for r in result['regions']]
        if 'seats' in fields or not fields:
            stock_type_by_stock_id = dict(((s.id, st) for st in result['stock_types'] for s in st['stocks']))
            stock_ids = stock_type_by_stock_id.keys()
            seats = search_seat(self.request, stock_ids, session) if stock_ids else [ ]

            res['seats'] = [dict(
                seat_l0_id=seat_l0_id,
                stock_type_id=stock_type_by_stock_id[stock_id]['stock_type_id'],
                is_available=(seat_status == SeatStatusEnum.Vacant.v),
            ) for seat_l0_id, stock_id, seat_status in seats]

        performance_id = int(self.request.matchdict.get('performance_id'))
        performance = session.query(Performance).filter_by(id=performance_id).first()
        seat_groups = search_seatGroup(self.request, performance.venue.site_id, performance.venue.id, session)

        res['seat_groups'] = [dict(
            seat_group_id=sg.l0_id,
            seat_group_name=sg.name,
            seat_l0_ids=[seat.l0_id for seat in sg.seats],
        ) for sg in seat_groups]

        return res

    @view_config(route_name='cart.api.seat_reserve')
    def seat_reserve(self):
        sales_segment = self.context.sales_segment
        if not sales_segment.in_term(self.context.now):
            logger.debug("out of term")
            return {
                "results": {
                    "status": "NG",
                    "reason": "out of term"
                }
            }

        performance_id = int(self.request.matchdict.get('performance_id'))
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id'))
        logger.debug("performance_id=%d, sales_segment_id=%d", performance_id, sales_segment_id)

        # 同一セッションでのカート生成を複数回させないため
        api.remove_cart(self.request)

        # リクエストボディのJSONからパラメータ取得
        try:
            json_data = self.request.json_body;
            logger.debug("json_data %s", json_data)
        except ValueError as e:
            logger.warning("no json_data")
            return {
                "results": {
                    "status": "NG",
                    "reason": "no json_data"
                }
            }

        reserve_type = json_data.get("reserve_type")
        selected_seats = json_data.get("selected_seats")
        auto_select_conditions = json_data.get("auto_select_conditions")

        # パラメータチェック
        request_quantity = 0
        reason = ""
        stock_type_id = ""

        if reserve_type != "auto" and reserve_type != "seat_choise":
            reason = "invalid parameter reserve_type"

        if reserve_type == "auto":
            stock_type_id = auto_select_conditions.get("stock_type_id")
            quantity = auto_select_conditions.get("quantity")

            if stock_type_id is None:
                reason = "invalid parameter stock_type_id"

            if quantity is None:
                reason = "invalid parameter quantity"
            else:
                request_quantity = int(quantity)
        elif reserve_type == "seat_choise":
            if selected_seats is None:
                reason = "invalid parameter selected_seats"
            else:
                request_quantity = len(selected_seats)
        else:
            reason = "invalid parameter reserve_type"

        if reason:
            return {
                "results": {
                    "status": "NG",
                    "reason": reason
                }
            }

        stocker = api.get_stocker(self.request)
        reserving = api.get_reserving(self.request)
        cart_factory = api.get_cart_factory(self.request)

        #カート生成前に購入枚数制限 or 席種混在チェック
        if reserve_type == "auto":
            #席種に紐づく商品を全てチェック
            products = DBSession.query(Product) \
                    .filter(Product.performance_id == performance_id) \
                    .filter(Product.sales_segment_id == sales_segment_id) \
                    .filter(Product.seat_stock_type_id == stock_type_id) \
                    .order_by(Product.id) \
                    .all()

            check_assert_quantity = []
            for ps in products:
                #購入枚数条件チェック
                sales_unit_quantity = sum([item.quantity for item in ps.items])
                ordered_items = [(ps, request_quantity / sales_unit_quantity)]
                logger.debug("ordered_items %s", ordered_items)

                try:
                    view_support.assert_quantity_within_bounds(sales_segment, ordered_items)
                    check_assert_quantity.append("OK")
                except (PerProductProductQuantityOutOfBoundsError,
                        QuantityOutOfBoundsError,
                        ProductQuantityOutOfBoundsError,
                        PerStockTypeQuantityOutOfBoundsError,
                        PerStockTypeProductQuantityOutOfBoundsError) as e:
                    check_assert_quantity.append("NG")

            #OKとなる商品が1つもない場合、制限エラーとしてNG
            if "OK" not in check_assert_quantity:
                return {
                    "results": {
                        "status": "NG",
                        "reason": "assert_quantity_within_bounds error"
                    }
                }

        elif reserve_type == "seat_choise":
            # 席種の混在をチェック
            stock_type = ''
            performance = DBSession.query(Performance).filter_by(id=performance_id).first()
            try:
                stock_type = DBSession.query(StockType.id) \
                            .join(Stock, Seat) \
                            .filter(Seat.l0_id.in_(selected_seats)) \
                            .filter(Seat.venue_id == performance.venue.id) \
                            .group_by(StockType.id) \
                            .one()
            except MultipleResultsFound as e:
                logger.warning("stock types are mixed %s", stock_type)
                transaction.abort()
                return {
                    "results": {
                        "status": "NG",
                        "reason": "stock types are mixed"
                    }
                }

            stock_type_id = stock_type.id

        #Cart生成
        try:
            products = DBSession.query(Product) \
                        .filter(Product.performance_id == performance_id) \
                        .filter(Product.sales_segment_id == sales_segment_id) \
                        .filter(Product.seat_stock_type_id == stock_type_id) \
                        .order_by(Product.id) \
                        .all()

        except NoResultFound as e:
            logger.warning("no product stock_type_id=%d", stock_type_id)
            return {
                "results": {
                    "status": "NG",
                    "reason": "no product"
                }
            }

        merge_product = ""
        min_quantity = ""
        mix_sales_unit = False
        for product in products:
            #公開商品以外はスキップ
            if not product.public:
                continue
            #商品明細の販売単位をSUM
            sales_unit_quantity = sum([item.quantity for item in product.items])

            #販売単位が1の場合は当商品情報で座席確保
            if sales_unit_quantity == 1:
                merge_product = product
                min_quantity = sales_unit_quantity
                break
            else:
                if not min_quantity:
                    merge_product = product
                    min_quantity = sales_unit_quantity
                    continue
                #販売単位が同じならそのまま。
                if min_quantity == sales_unit_quantity:
                    continue
                else:
                    mix_sales_unit = True
                    #現在の販売単位より小さい販売単位がきた場合は、入れ替え
                    if sales_unit_quantity < min_quantity:
                        min_quantity = sales_unit_quantity
                        merge_product = product
                        continue

        #販売単位が2以上の場合、販売単位チェック
        #1の場合は、リクエストされた枚数をそのまま使用する。
        if min_quantity != 1:
            #販売単位の最小が1ではなく、2以上が混在している場合エラー
            if mix_sales_unit:
                return {
                    "results": {
                        "status": "NG",
                        "reason": "mix salse unit quantity not 1"
                    }
                }
            else:
                #販売単位の最小が1ではなく、2以上が混在していない場合
                #要求席数/販売単位
                request_quantity /= min_quantity

        product_requires = [(merge_product, request_quantity)]
        logger.debug("product_requires %s", product_requires)
        try:
            stockstatuses = stocker.take_stock(performance_id, product_requires)
        except NotEnoughStockException:
            transaction.abort()
            return {
                "results": {
                    "status": "NG",
                    "reason": "not enough stock exception"
                    }
            }

        separate_seats = False
        quantity_only = True
        seats = []
        if reserve_type == "auto":
            for stockstatus, quantity in stockstatuses:
                if stockstatus.stock.stock_type.quantity_only:
                    logger.debug('stock %d quantity only', stockstatus.stock.id)
                    continue

                #separate_seats取得
                org = api.get_organization(self.request)
                setting = org.setting
                separate_seats = setting.entrust_separate_seats
                logger.debug('separate_seats %d  ', separate_seats)

                try:
                    seats += reserving.reserve_seats(stockstatus.stock_id, quantity, separate_seats=separate_seats)
                except NotEnoughAdjacencyException:
                    transaction.abort()
                    return {
                        "results": {
                            "status": "NG",
                            "reason": "no enough adjacency exception"
                        }
                    }

                quantity_only = False
        elif reserve_type == "seat_choise":
            try:
                seats += reserving.reserve_selected_seats(stockstatuses, performance_id, selected_seats)
            except InvalidSeatSelectionException:
                transaction.abort()
                return {
                    "results": {
                        "status": "NG",
                        "reason": "invalid seat selection exception"
                    }
                }
            quantity_only = False

        seat_ids = [seat.id for seat in seats]
        seat_l0_ids = [seat.l0_id for seat in seats]
        seat_names = [seat.name for seat in seats]
        logger.debug("seat_l0_ids %s", seat_l0_ids)

        cart = cart_factory.create_cart(sales_segment, seats, product_requires, channel=ChannelEnum.SPA.v)
        if cart is None:
            transaction.abort()
            return {
                "results": {
                    "status": "NG",
                    "reason": "create cart error"
                }
            }

        cart.sales_segment = sales_segment
        DBSession.add(cart)
        DBSession.flush()
        api.set_cart(self.request, cart)
        logger.debug("cart_id %s", cart.id)

        if quantity_only:
            return dict(
                results = dict(
                    status = "OK",
                    reserve_type = reserve_type,
                    stock_type_id = stock_type_id,
                    quantity = request_quantity,
                    is_quantity_only = quantity_only,
                    is_separated = False,
                )
            )
        else:
            # 席種の混在をチェック
            stock_type_ids = ''
            try:
                stock_type_ids = DBSession.query(StockType.id) \
                            .join(Stock, Seat) \
                            .filter(Seat.id.in_(seat_ids)) \
                            .group_by(StockType.id) \
                            .one()
            except MultipleResultsFound as e:
                logger.warning("stock types are mixed %s", stock_type_ids)
                transaction.abort()
                return {
                    "results": {
                        "status": "NG",
                        "reason": "stock types are mixed"
                    }
                }

            ret_seats = []
            for index, l0_id in enumerate(seat_l0_ids):
                ret_seat = {"seat_id":l0_id,"seat_name":seat_names[index]}
                ret_seats.append(ret_seat)

            is_separated = False

            #おまかせで席受け(2枚以上)の場合、連席or飛び席判定
            #確保した座席が連席データに入っていれば連席とみなす。
            if reserve_type == "auto" and quantity >= 2:
                performance = DBSession.query(Performance).filter_by(id=performance_id).first()

                seat_separate = DBSession.query(func.count(Seat_SeatAdjacency.seat_adjacency_id)) \
                    .join(SeatAdjacency, Seat_SeatAdjacency.seat_adjacency_id == SeatAdjacency.id) \
                    .join(SeatAdjacencySet, SeatAdjacency.adjacency_set_id == SeatAdjacencySet.id) \
                    .join(Seat, Seat_SeatAdjacency.l0_id == Seat.l0_id) \
                    .filter(Seat.venue_id == performance.venue.id) \
                    .filter(SeatAdjacencySet.seat_count == quantity) \
                    .filter(SeatAdjacencySet.site_id == performance.venue.site_id) \
                    .filter(Seat_SeatAdjacency.l0_id.in_(seat_l0_ids)) \
                    .group_by(Seat_SeatAdjacency.seat_adjacency_id) \
                    .having(func.count(Seat_SeatAdjacency.seat_adjacency_id) == quantity) \
                    .first()

                #取得できない場合は、飛び席とする。
                if not seat_separate:
                    is_separated = True

            return dict(
                results = dict(
                    status = "OK",
                    reserve_type = reserve_type,
                    stock_type_id = stock_type_ids[0],
                    quantity = len(seat_l0_ids),
                    is_quantity_only = quantity_only,
                    is_separated = is_separated,
                    seats = ret_seats
                )
            )


    @view_config(route_name='cart.api.seat_release')
    def seat_release(self):
        cart = api.get_cart(self.request, False)

        if cart is None or cart.finished_at is not None:
            return {
                "results": {
                    "status": "NG",
                    "reason": "cart does not exist"
                }
            }

        logger.debug("cart_id %s", cart.id)

        try:
            carted_products = DBSession.query(CartedProduct) \
                                .filter(CartedProduct.cart_id == cart.id) \
                                .all()
        except NoResultFound as e:
            logger.warning("no CartedProduct cart_id=%d", cart.id)
            return {
                "results": {
                    "status": "NG",
                    "reason": "no CartedProduct"
                }
            }

        quantity = sum(carted_product.quantity for carted_product in carted_products)
        product_ids = [carted_product.product_id for carted_product in carted_products]
        carted_product_ids = [carted_product.id for carted_product in carted_products]

        try:
            stock_type = DBSession.query(StockType) \
                                .join(Product) \
                                .filter(Product.id.in_(product_ids)) \
                                .first()
        except NoResultFound as e:
            logger.warning("no StockType product_id=%s", product_ids)
            return {
                "results": {
                    "status": "NG",
                    "reason": "no StockType"
                }
            }

        try:
            carted_product_items = DBSession.query(CartedProductItem) \
                                .filter(CartedProductItem.carted_product_id.in_(carted_product_ids)) \
                                .all()
        except NoResultFound as e:
            logger.warning("no CartedProductItem carted_product_id=%s", carted_product_ids)
            return {
                "results": {
                    "status": "NG",
                    "reason": "no CartedProductItem"
                }
            }

        seats = []
        for carted_product_item in carted_product_items:
            seats += carted_product_item.seats

        api.remove_cart(self.request)
        return {
            "results": {
                "status": "OK",
                "stock_type_id": int(stock_type.id),
                "quantity": quantity,
                "is_quantity_only": stock_type.quantity_only,
                "seats": [seat.l0_id for seat in seats]
            }
        }

    @view_config(route_name='cart.api.select_products')
    def select_products(self):
        #セッション情報から取得
        cart = api.get_cart(self.request, False)
        logger.debug("cart_id %s", cart.id)

        if cart is None or cart.finished_at is not None:
            return {
                "results": {
                    "status": "NG",
                    "reason": "cart does not exist"
                }
            }

        # リクエストボディのJSONからパラメータ取得
        try:
            json_data = self.request.json_body;
            logger.debug("json_data %s", json_data)
        except ValueError as e:
            logger.warning("no json_data")
            return {
                "results": {
                    "status": "NG",
                    "reason": "no json_data"
                }
            }

        is_quantity_only = json_data.get("is_quantity_only")
        selected_products = json_data.get("selected_products")

        reason = ""

        # パラメータチェック
        if is_quantity_only is None:
            reason = "invalid parameter is_quantity_only"

        if selected_products is None:
            reason = "invalid parameter selected_products"

        for sp in selected_products:
            if 'product_item_id' not in sp:
                reason = "no key selected_products in product_item_id"
            elif sp['product_item_id'] is None:
                reason = "invalid parameter selected_products in product_item_id"

            if 'quantity' not in sp:
                reason = "no key selected_products in quantity"
            elif sp['quantity'] is None:
                reason = "invalid parameter selected_products in quantity"

            if not is_quantity_only and 'seat_id' not in sp:
                reason = "no key selected_products in seat_id"
            elif not is_quantity_only and sp['seat_id'] is None:
                reason = "invalid parameter selected_products in seat_id"

        if reason:
            return {
                "results": {
                    "status": "NG",
                    "reason": reason
                }
            }

        # SalesSegment取得
        sales_segment = DBSession.query(SalesSegment).filter_by(id=cart.sales_segment_id).first()
        if sales_segment is None:
            return {
                "results": {
                    "status": "NG",
                    "reason": "No matching sales_segment"
                }
            }

        #リクエスト内容（商品明細）を商品単位にまとめる。
        request_items = {}
        for sp in selected_products:
            #同一商品明細単位でまとめる。
            if sp['product_item_id'] not in request_items.keys():
                item = {'quantity':sp['quantity']}
                if not is_quantity_only:
                    item['seat'] = [sp['seat_id']]
                request_items[sp['product_item_id']] = item
            else:
                item_quantity = request_items[sp['product_item_id']]['quantity']
                item_quantity += sp['quantity']
                request_items[sp['product_item_id']]['quantity'] = item_quantity
                if not is_quantity_only:
                    request_items[sp['product_item_id']]['seat'].append(sp['seat_id'])

        #まとめた商品明細を同一商品単位でまとめる。
        request_products = {}
        for key,value in request_items.iteritems():
            product_item = DBSession.query(ProductItem).filter_by(id=key).first()
            product = DBSession.query(Product).filter_by(id=product_item.product_id).first()
            #商品明細の商品IDが同じであれば、追加し商品単位にまとめる。
            if product not in request_products.keys():
                items = []
                items.append(dict({key:value}))
                request_products[product] = items
            else:
                items = request_products[product]
                items.append(dict({key:value}))
                request_products[product] = items

        #購入枚数チェック
        for product,request_items in request_products.iteritems():
            #商品明細の販売単位、枚数から商品の枚数を特定する。
            sum_sales_unit_quantity = sum([item.quantity for item in product.items])
            sum_item_quantity = 0
            for req in request_items:
                for reqItem in req.values():
                    sum_item_quantity += reqItem['quantity']
            ordered_items = [(product, sum_item_quantity / sum_sales_unit_quantity)]
            logger.debug("ordered_items %s", ordered_items)

            try:
                view_support.assert_quantity_within_bounds(sales_segment, ordered_items)
            except (PerProductProductQuantityOutOfBoundsError,
                    QuantityOutOfBoundsError,
                    ProductQuantityOutOfBoundsError,
                    PerStockTypeQuantityOutOfBoundsError,
                    PerStockTypeProductQuantityOutOfBoundsError) as e:
                logger.debug("PerProductProductQuantityOutOfBoundsError error %s",e.message)
                return {
                "results": {
                       "status": "NG",
                        "reason": "assert_quantity_within_bounds error"
                    }
                }

        #保存処理
        #Cart取得
        exec_cart = DBSession.query(Cart).filter_by(id=cart.id).first()

        #古いcart_product、cart_product_itemを論理削除
        cart_product = DBSession.query(CartedProduct).filter_by(cart_id=exec_cart.id).all()
        for cp in cart_product:
            cp.deleted_at = datetime.now()

            cart_product_items = DBSession.query(CartedProductItem).filter_by(carted_product_id=cp.id).all()
            for cpi in cart_product_items:
                cpi.deleted_at = datetime.now()

        for product,request_items in request_products.iteritems():
            #商品明細の販売単位、枚数から商品の枚数を特定する。
            sum_sales_unit_quantity = sum([item.quantity for item in product.items])
            sum_item_quantity = 0
            for req in request_items:
                for reqItem in req.values():
                    sum_item_quantity += reqItem['quantity']

            product_quantity = sum_item_quantity / sum_sales_unit_quantity

            #カート商品登録
            cart_product = CartedProduct(cart=exec_cart, product=product, quantity=product_quantity, organization_id=exec_cart.organization_id)
            DBSession.add(cart_product)

            cart_factory = api.get_cart_factory(self.request)

            #カート商品明細登録
            for req in request_items:
                for key, reqItem in req.iteritems():
                    seats = []
                    product_item = DBSession.query(ProductItem).filter_by(id=key).first()
                    cart_product_item = CartedProductItem(
                        carted_product = cart_product,
                        organization_id = cart_product.organization_id,
                        quantity = reqItem['quantity'],
                        product_item = product_item)

                    # 席受け時の座席割り当て
                    if not is_quantity_only:
                        #performance取得
                        performance = DBSession.query(Performance).filter_by(id=exec_cart.performance_id).first()
                        #座席情報取得
                        for seat_l0_id in reqItem['seat']:
                            seat = DBSession.query(Seat).filter_by(l0_id=seat_l0_id,venue_id=performance.venue.id).first()
                            seats.append(seat)
                        logger.debug("seats %s", seats)
                        item_seats = cart_factory.pop_seats(product_item, reqItem['quantity'], seats)
                        cart_product_item.seats = item_seats

                    DBSession.add(cart_product_item)

        DBSession.flush()

        return {
            "results": {
                "status": "OK",
                "reason": ""
            }
        }

@view_config(context=OutTermSalesException, renderer='json')
def out_term_exec(context, request):
    request.response.status = 404
    message = context.message or 'no resource was found'
    return dict(
            error=dict(
                code="404",
                message="{}: {}".format(context.__class__.__name__, message),
                details=[]
            )
        )


@view_config(context=NoPerformanceError, renderer='json')
def out_term_exec(context, request):
    request.response.status = 404
    message = context.message or 'no resource was found'
    return dict(
            error=dict(
                code="404",
                message="{}: {}".format(context.__class__.__name__, message),
                details=[]
            )
        )


@view_config(context=HTTPNotFound, renderer='json')
def no_resource(context, request):
    request.response.status = 404
    message = context.message or 'no resource was found'
    return dict(
        error=dict(
            code="404",
            message="{}: {}".format(context.__class__.__name__, message),
            details=[]
        )
    )


@view_config(context=HTTPBadRequest, renderer='json')
def no_resource(context, request):
    request.response.status = 400
    message = context.message or 'bad request'
    return dict(
        error=dict(
            code="400",
            message="{}: {}".format(context.__class__.__name__, message),
            details=[]
        )
    )


@view_config(context=AuthenticationError, renderer='json')
def authentication_error(context, request):
    request.response.status = 200
    message = "Authentication Failed"
    return dict(
        error=dict(
            code='401',
            message="{}: {}".format(context.__class__.__name__, message),
            details=[]
        )
    )


@view_config(context=Exception, renderer='json')
def exception_handler(context, request):
    return context
