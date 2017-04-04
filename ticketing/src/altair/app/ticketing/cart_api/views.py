# -*- coding:utf-8 -*-
import logging

from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import distinct, func

from altair.sqlahelper import get_db_session
from altair.pyramid_dynamic_renderer import lbr_view_config

from altair.app.ticketing.core.models import (
    StockType,
    Seat,
    Stock,
    SeatStatus,
    SeatStatusEnum,
    Product,
    ProductItem,
    SalesSegment,
    StockStatus
)
from altair.app.ticketing.cart.models import (
    Cart,
    CartedProduct,
    CartedProductItem
)
from altair.app.ticketing.cart.exceptions import OutTermSalesException, NoPerformanceError
from altair.app.ticketing.cart import api
from altair.app.ticketing.models import DBSession

logger = logging.getLogger(__name__)


@view_defaults(renderer='json')
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
        return dict(
            performance=dict(
                performance_id=performance.id,
                performance_name=performance.name,
                open_on=performance.open_on,
                start_on=performance.start_on,
                end_on=performance.end_on,
                order_limit=performance.setting.order_limit,
                venue_id=performance.venue.id,
                venue_name=performance.venue.name
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
                order_limit=ss.order_limit
            ) for ss in available_sales_segments]
        )

    @view_config(route_name='cart.api.stock_types')
    def stock_types(self):
        stock_types = self.context.performance.stock_types
        return dict(
            stock_types=[dict(
                stock_type_id=st.id,
                stock_type_name=st.name,
                is_quantity_only=st.quantity_only,
                description=st.description,
                min_quantity=st.min_quantity,
                max_quantity=st.max_quantity,
                min_product_quantity=st.min_product_quantity,
                max_product_quantity=st.max_product_quantity
            ) for st in stock_types]
        )

    @view_config(route_name='cart.api.stock_type')
    def stock_type(self):
        performance = self.context.performance
        stock_type_id = self.request.matchdict.get('stock_type_id')
        session = get_db_session(self.request, 'slave')
        try:
            stock_type = session.query(StockType).filter(StockType.id == stock_type_id).one()
        except NoResultFound as e:
            logger.warning("{} for stock_type_id={}".format(e.message, stock_type_id))
            raise HTTPNotFound()
        products = [p for p in stock_type.product if p.performance_id == performance.id]  # XXX: productだけどlistが返ってくる
        blocks = stock_type.blocks(performance_id=performance.id)
        return dict(
            stock_type=dict(
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
                    is_must_be_chosen=product.must_be_chosen
                ) for product in products],
                blocks=blocks
            )
        )

    @view_config(route_name='cart.api.seats')
    def seats(self):
        from collections import namedtuple
        SeatDict = namedtuple("SeatDict", "seat_id stock_type_id seat_status stock_quantity")
        StockTypeQuantityPair = namedtuple("StockTypeQuantityPair", "stock_type_id stock_quantity")

        # available_sales_segmentsは優先順位順にならんでるはず
        sales_segment = [ss for ss in self.context.available_sales_segments][0]
        session = get_db_session(self.request, 'slave')
        seat_dicts = session.query(distinct(Seat.id), Stock.stock_type_id, SeatStatus.status, StockStatus.quantity)\
                            .join(Seat.status_)\
                            .join(Seat.stock)\
                            .join(Stock.product_items)\
                            .join(Stock.stock_status)\
                            .join(ProductItem.product)\
                            .join(Product.sales_segment)\
                            .filter(SalesSegment.id == sales_segment.id)\
                            .all()

        seat_dicts = [SeatDict(d[0], d[1], d[2], d[3]) for d in seat_dicts]
        stock_type_quantity_pairs = [StockTypeQuantityPair(type_id, quantity)
                                     for type_id, quantity in set([(d.stock_type_id, d.stock_quantity) for d in seat_dicts])]
        stock_type_ids = [pairs.stock_type_id for pairs in stock_type_quantity_pairs]
        stock_types = session.query(StockType).filter(StockType.id.in_(stock_type_ids)).all()

        blocks = []
        performance_id = sales_segment.performance.id
        for stock_type in stock_types:
            blocks.extend(stock_type.blocks(performance_id=performance_id))

        return dict(
            seats=[dict(
                seat_id=d.seat_id,
                stock_type_id=d.stock_type_id,
                is_available=(d.seat_status == SeatStatusEnum.Vacant.v),
            ) for d in seat_dicts],
            stock_types=[dict(
                stock_type_id=pairs.stock_type_id,
                available_counts=pairs.stock_quantity
            ) for pairs in stock_type_quantity_pairs],
            blocks=[dict(
                block_id=block
            ) for block in set(blocks)]
        )

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
        stock_type_id = auto_select_conditions.get("stock_type_id")
        quantity = auto_select_conditions.get("quantity")
        
        # パラメータチェック
        request_quantity = 0
        reason = ""

        if reserve_type != "auto" and reserve_type != "seat_choise":
            reason = "invalid parameter reserve_type"

        if reserve_type == "auto":
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
        
        # TODO:座席確保の前に枚数制限チェックをする必要あり（ただし席種単位のしかできない）

        stocker = api.get_stocker(self.request)
        reserving = api.get_reserving(self.request)
        cart_factory = api.get_cart_factory(self.request)

        try:
            product = DBSession.query(Product) \
                        .filter(Product.performance_id == performance_id) \
                        .filter(Product.sales_segment_id == sales_segment_id) \
                        .filter(Product.seat_stock_type_id == stock_type_id) \
                        .order_by(Product.id) \
                        .first()
        except NoResultFound as e:
            logger.warning("no product stock_type_id=%d", stock_type_id)
            return {
                "results": {
                    "status": "NG",
                    "reason": "no product"
                }
            }

        product_requires = [(product, request_quantity)]
        logger.debug("product_requires %s", product_requires)
        stockstatuses = stocker.take_stock(performance_id, product_requires)

        # TODO:autoの場合はseparate_seatsをどこからか取得して設定する必要あり
        separate_seats = False
        quantity_only = True
        seats = []
        if reserve_type == "auto":
            for stockstatus, quantity in stockstatuses:
                if stockstatus.stock.stock_type.quantity_only:
                    logger.debug('stock %d quantity only', stockstatus.stock.id)
                    continue
                seats += reserving.reserve_seats(stockstatus.stock_id, quantity, separate_seats=separate_seats)
                quantity_only = False
        elif reserve_type == "seat_choise":
            seats += reserving.reserve_selected_seats(stockstatuses, performance_id, selected_seats)
            quantity_only = False
        
        seat_ids = [seat.id for seat in seats]
        seat_l0_ids = [seat.l0_id for seat in seats]
        logger.debug("seat_l0_ids %s", seat_l0_ids)

        cart = cart_factory.create_cart(sales_segment, seats, product_requires)
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

            return dict(
                results = dict(
                    status = "OK",
                    reserve_type = reserve_type,
                    stock_type_id = stock_type_ids[0],
                    quantity = len(seat_l0_ids),
                    is_quantity_only = quantity_only,
                    is_separated = False,
                    seats = seat_l0_ids
                )
            )


    @view_config(route_name='cart.api.seat_release')
    def seat_release(self):
        cart = api.get_cart(self.request, False)
        logger.debug("cart_id %s", cart.id)

        if cart is None or cart.finished_at is not None:
            return {
                "results": {
                    "status": "NG",
                    "reason": "cart does not exist"
                }
            }

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
