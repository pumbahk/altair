# -*- coding:utf-8 -*-

"""
購入フローに関連する座席状態遷移

Vacant 開始状態
 座席確保

InCart 座席確保済
 決済
 キャンセル

Canceled:
 購入フローでのアクションなし

Ordered: 決済完了
 購入フローでのアクションなし

Reserved
 今回の実装なし
"""


from datetime import datetime, timedelta
import itertools
import operator
import sqlahelper
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy import sql
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm.exc import NoResultFound
from zope.deprecation import deprecate

from ticketing.utils import sensible_alnum_encode, sensible_alnum_decode
from ticketing.models import Identifier
from ..core import models as c_models
from ..core import api as c_api
from ..models import Identifier
from . import logger
from .exceptions import NoCartError, UnassignedOrderNumberError

class PaymentMethodManager(object):
    def __init__(self):
        self.route_map = {}

    def add_route_name(self, payment_method_id, route_name):
        self.route_map[payment_method_id] = route_name

    def get_route_name(self, payment_method_id):
        return self.route_map.get(payment_method_id)


MULTICHECKOUT_AUTH_OK = '110'
MULTICHECKOUT_SALES_OK = '120'

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

cart_seat_table = sa.Table("cat_seat", Base.metadata,
    sa.Column("seat_id", Identifier, sa.ForeignKey("Seat.id")),
    sa.Column("cartproductitem_id", Identifier, sa.ForeignKey("ticketing_cartedproductitems.id")),
)

class CartedProductItem(Base):
    """ カート内プロダクトアイテム + 座席 + 座席状況
    """
    __tablename__ = 'ticketing_cartedproductitems'
    query = DBSession.query_property()

    id = sa.Column(Identifier, primary_key=True)

    quantity = sa.Column(sa.Integer)

    product_item_id = sa.Column(Identifier, sa.ForeignKey("ProductItem.id"))

    #seat_status_id = sa.Column(sa.Integer, sa.ForeignKey(""))

    product_item = orm.relationship("ProductItem", backref='carted_product_items')
    seats = orm.relationship("Seat", secondary=cart_seat_table)
    #seat_status = orm.relationship("SeatStatus")

    carted_product_id = sa.Column(Identifier, sa.ForeignKey("ticketing_cartedproducts.id", onupdate='cascade', ondelete='cascade'))
    carted_product = orm.relationship("CartedProduct", backref="items", cascade='all')

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, nullable=True, onupdate=datetime.now)
    deleted_at = sa.Column(sa.DateTime, nullable=True)
    finished_at = sa.Column(sa.DateTime)

    @property
    def seatdicts(self):
        return ({'name': s.name, 'l0_id': s.l0_id}
                for s in self.seats)

    @deprecate("deprecated method")
    def pop_seats(self, seats):
        """ 必要な座席を取り出して保持する

        必要な座席： :attr:`product_item` の stockが一致する Seat
        :param seats: list of :class:`ticketing.models.Seat`
        """

        my_seats = [seat for seat in seats if seat.stock_id == self.product_item.stock_id][:self.quantity]
        map(seats.remove, my_seats)
        self.seats.extend(my_seats)
        return seats

    @property
    def seat_statuses(self):
        """ 確保済の座席ステータス
        """
        return DBSession.query(c_models.SeatStatus).filter(c_models.SeatStatus.seat_id.in_([s.id for s in self.seats])).all()

    @property
    def seat_statuses_for_update(self):
        """ 確保済の座席ステータス
        """
        return DBSession.query(c_models.SeatStatus).filter(c_models.SeatStatus.seat_id.in_([s.id for s in self.seats])).with_lockmode('update').all()

    def finish(self):
        """ 決済処理
        """
        for seat_status in self.seat_statuses_for_update:
            if seat_status.status != int(c_models.SeatStatusEnum.InCart):
                raise NoCartError()
            seat_status.status = int(c_models.SeatStatusEnum.Ordered)
        self.finished_at = datetime.now()

    def release(self):
        logger.info('trying to release CartedProductItem (id=%d)' % self.id)
        if not self.finished_at:
            # 座席開放
            for seat_status in self.seat_statuses_for_update:
                logger.info('trying to release seat (id=%d)' % seat_status.seat_id)
                if seat_status.status != int(c_models.SeatStatusEnum.InCart):
                    logger.info('seat (id=%d) has status=%d, while expecting InCart (%d)' % (seat_status.seat_id, seat_status.status, int(c_models.SeatStatusEnum.InCart)))
                    logger.info('not releaseing CartedProductItem (id=%d) for safety' % self.id)
                    return False
                logger.info('setting status of seat (id=%d) to Vacant (%d)' % (seat_status.seat_id, int(c_models.SeatStatusEnum.Vacant)))
                seat_status.status = int(c_models.SeatStatusEnum.Vacant)

            # 在庫数戻し
            if self.product_item.stock.stock_type.quantity_only:
                release_quantity = self.quantity
            else:
                release_quantity = len(self.seats)
            stock_status = c_models.StockStatus.filter_by(stock_id=self.product_item.stock_id).with_lockmode('update').one()
            logger.info('restoring the quantity of stock (id=%s, quantity=%d) by +%d' % (stock_status.stock_id, stock_status.quantity, release_quantity))
            stock_status.quantity += release_quantity
            stock_status.save()
            logger.info('done for CartedProductItem (id=%d)' % self.id)

            self.finished_at = datetime.now()
        return True

    def is_valid(self):
        for seat_status in self.seat_statuses:
            if seat_status.status != int(c_models.SeatStatusEnum.InCart):
                return False
        return True
        

class CartedProduct(Base):
    __tablename__ = 'ticketing_cartedproducts'

    query = DBSession.query_property()

    id = sa.Column(Identifier, primary_key=True)
    quantity = sa.Column(sa.Integer)
    cart_id = sa.Column(Identifier, sa.ForeignKey('ticketing_carts.id', onupdate='cascade', ondelete='cascade'))
    cart = orm.relationship("Cart", backref="products", cascade='all')

    product_id = sa.Column(Identifier, sa.ForeignKey("Product.id"))
    product = orm.relationship("Product")

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, nullable=True, onupdate=datetime.now)
    deleted_at = sa.Column(sa.DateTime, nullable=True)
    finished_at = sa.Column(sa.DateTime)

    @property
    def amount(self):
        """ 購入額小計
        """
        return self.product.price * self.quantity

    @property
    def seats(self):
        return sorted(itertools.chain.from_iterable(i.seatdicts for i in self.items), 
            key=operator.itemgetter('l0_id'))

    @deprecate("deprecated method")
    def pop_seats(self, seats, performance_id):
        for product_item in self.product.items:
            if product_item.performance_id != performance_id:
                continue
            cart_product_item = CartedProductItem(carted_product=self, quantity=self.quantity, product_item=product_item)
            seats = cart_product_item.pop_seats(seats)
        return seats

    @deprecate("deprecated method")
    def adjust_items(self, performance_id):
        for product_item in self.product.items:
            if product_item.performance_id != performance_id:
                continue
            cart_product_item = CartedProductItem(carted_product=self, quantity=self.quantity, product_item=product_item)

    @classmethod
    def get_reserved_amount(cls, product_item):
        return DBSession.query(sql.func.sum(cls.amount)).filter(cls.product_item==product_item).filter(cls.state=="reserved").first()[0] or 0


    def finish(self):
        """ 決済処理
        """
        for item in self.items:
            item.finish()
        self.finished_at = datetime.now()

    def release(self):
        """ 開放
        """
        logger.info('trying to release CartedProduct (id=%d)' % self.id)
        if not self.finished_at:
            for item in self.items:
                if not item.release():
                    logger.info('returing False to abort. NO FURTHER SQL EXECUTION IS SUPPOSED!')
                    return False
            self.finished_at = datetime.now()
            logger.info('CartedProduct (id=%d) successfully released' % self.id)
        return True

    def is_valid(self):
        return all([i.is_valid() for i in self.items])
        

class Cart(Base):
    __tablename__ = 'ticketing_carts'

    query = DBSession.query_property()

    id = sa.Column(Identifier, primary_key=True)
    cart_session_id = sa.Column(sa.Unicode(255), unique=True)
    performance_id = sa.Column(Identifier, sa.ForeignKey('Performance.id'))

    performance = orm.relationship('Performance')

    system_fee = sa.Column(sa.Numeric(precision=16, scale=2))

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, nullable=True, onupdate=datetime.now)
    deleted_at = sa.Column(sa.DateTime, nullable=True)
    finished_at = sa.Column(sa.DateTime)

    shipping_address_id = sa.Column(Identifier, sa.ForeignKey("ShippingAddress.id"))
    shipping_address = orm.relationship('ShippingAddress', backref='cart')

    payment_delivery_method_pair_id = sa.Column(Identifier, sa.ForeignKey("PaymentDeliveryMethodPair.id"))
    payment_delivery_pair = orm.relationship("PaymentDeliveryMethodPair")

    _order_no = sa.Column("order_no", sa.String(255))
    order_id = sa.Column(Identifier, sa.ForeignKey("Order.id"))
    order = orm.relationship('Order', backref='carts')

    sales_segment_id = sa.Column(Identifier, sa.ForeignKey('SalesSegment.id'))
    sales_segment = orm.relationship('SalesSegment', backref='carts')

    disposed = False

    @classmethod 
    def create(cls, **kwargs):
        performance = kwargs.pop('performance', None)
        if performance is None:
            performance_id = kwargs.pop('performance_id', None)
            if performance_id is None:
                raise Exception('performance or performance_id must be specified')
            performance = c_models.Performance.query.filter_by(id=performance_id).one()
        organization = performance.event.organization
        logger.debug("organization.id = %d" % organization.id)
        base_id = c_api.get_next_order_no()
        order_no = organization.code + sensible_alnum_encode(base_id).zfill(10)
        new_cart = cls(
            _order_no=order_no,
            performance=performance,
            **kwargs)
        DBSession.add(new_cart)
        return new_cart

    @classmethod
    def create_from(cls, that):
        # すでに detach しているかもしれないので、merge を試みる
        that = DBSession.merge(that) 
        if that.order_id is not None:
            raise CartCreationException("Cannot translate the contents of a cart that has already been associated to the order")
        if that.finished_at is not None:
            raise CartCreationException("Cannot translate the contents of a cart that has already been marked as finished")
        new_cart = cls.create(
            cart_session_id=that.cart_session_id,
            system_fee=that.system_fee,
            shipping_address=that.shipping_address,
            payment_delivery_pair=that.payment_delivery_pair,
            performance=that.performance,
            sales_segment=that.sales_segment
            )
        # translate all the products in the specified cart to the new cart
        for carted_product in that.products:
            new_cart.products.append(carted_product) 
        that.disposed = True
        that.products = []
        return new_cart

    @property
    def order_no(self):
        if self._order_no is None:
            raise UnassignedOrderNumberError(self.id)
        return self._order_no

    @property
    def total_amount(self):
        return self.tickets_amount + self.system_fee + self.transaction_fee + self.delivery_fee

    @property
    def tickets_amount(self):
        return sum(cp.amount for cp in self.products)

    @property
    def total_quantiy(self):
        return sum(cp.quantity for cp in self.products)

    @property
    def transaction_fee(self):
        """ 決済手数料 """
        payment_fee = self.payment_delivery_pair.transaction_fee
        payment_method = self.payment_delivery_pair.payment_method
        if payment_method.fee_type == c_models.FeeTypeEnum.Once.v[0]:
            return payment_fee
        elif payment_method.fee_type == c_models.FeeTypeEnum.PerUnit.v[0]:
            return payment_fee * self.total_quantiy
        else:
            return 0

    @property 
    def delivery_fee(self):
        """ 配送手数料 """
        delivery_fee = self.payment_delivery_pair.delivery_fee
        delivery_method = self.payment_delivery_pair.delivery_method
        if delivery_method.fee_type == c_models.FeeTypeEnum.Once.v[0]:
            return delivery_fee
        elif delivery_method.fee_type == c_models.FeeTypeEnum.PerUnit.v[0]:
            return delivery_fee * self.total_quantiy
        else:
            return 0

    @classmethod
    def get_or_create(cls, performance, cart_session_id):
        try:
            return cls.query.filter_by(cart_session_id=cart_session_id).one()
        except NoResultFound:
            return cls.create(performance=performance, cart_session_id=cart_session_id)

    @classmethod
    def is_existing_cart_session_id(cls, cart_session_id):
        return cls.query.filter_by(cart_session_id=cart_session_id).count()

    @hybrid_method
    def is_expired(self, expire_span_minutes):
        """ 決済完了までの時間制限
        """
        return self.created_at < datetime.now() - timedelta(minutes=expire_span_minutes)

    @deprecate("deprecated method")
    def add_seat(self, seats, ordered_products):
        """ 確保した座席を追加
        :param seats: list of Seat
        :param ordered_products: list of tuple(product, quantity)
        """
        # ordered_productsでループ
        for ordered_product, quantity in ordered_products:
            # ordered_productでCartProductを作成
            cart_product = CartedProduct(cart=self, product=ordered_product, quantity=quantity)
            seats = cart_product.pop_seats(seats, self.performance_id)
        # CartProductでseatsから必要な座席を取り出し

    #@deprecate("deprecated method") 
    # 抽選から使う
    def add_products(self, ordered_products):
        for ordered_product, quantity in ordered_products:
            # ordered_productでCartProductを作成
            cart_product = CartedProduct(cart=self, product=ordered_product, quantity=quantity)
            cart_product.adjust_items(self.performance_id)

    def finish(self):
        """ 決済完了
        """
        for product in self.products:
            product.finish()
        self.finished_at = datetime.now()

    def release(self):
        """ カート開放
        """
        logger.info('trying to release Cart (id=%d, order_no=%s)' % (self.id, self.order_no))
        for product in self.products:
            if not product.release():
                return False
        return True

    def is_valid(self):
        return all([p.is_valid() for p in self.products])

    @classmethod
    def from_order_no(cls, order_no):
        return Cart.query.filter_by(_order_no=order_no).one()
