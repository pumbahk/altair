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
from decimal import Decimal
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy import sql
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import object_session
from zope.deprecation import deprecate, deprecated
from zope.interface import implementer

from pyramid.i18n import TranslationString as _
from altair.saannotation import AnnotatedColumn

from altair.app.ticketing.utils import sensible_alnum_encode
from altair.models import Identifier, JSONEncodedDict, LogicallyDeleted, WithTimestamp, MutationDict
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.core import api as c_api
from altair.app.ticketing.core.interfaces import IOrderedProductLike, IOrderedProductItemLike
from altair.app.ticketing.payments.interfaces import IPaymentCart
from . import logger
from .exceptions import NoCartError, CartCreationException, InvalidCartStatusError
from .interfaces import ICartSetting

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

cart_seat_table = sa.Table("CartedProductItem_Seat", Base.metadata,
    sa.Column("seat_id", Identifier, sa.ForeignKey("Seat.id")),
    sa.Column("carted_product_item_id", Identifier, sa.ForeignKey("CartedProductItem.id")),
)

cart_user_point_account_table = sa.Table(
    "Cart_UserPointAccount", Base.metadata,
    sa.Column("cart_id", Identifier, sa.ForeignKey("Cart.id")),
    sa.Column("user_point_account_id", Identifier, sa.ForeignKey("UserPointAccount.id"))
    )

@implementer(IPaymentCart)
class Cart(Base, c_models.CartMixin):
    __tablename__ = 'Cart'

    query = DBSession.query_property()

    id = sa.Column(Identifier, primary_key=True)
    cart_session_id = sa.Column(sa.VARBINARY(72), unique=False)
    performance_id = sa.Column(Identifier, sa.ForeignKey('Performance.id'))

    performance = orm.relationship('Performance')

    created_at = AnnotatedColumn(sa.DateTime, default=datetime.now, _a_label=_(u'カート生成日時'))
    updated_at = sa.Column(sa.DateTime, nullable=True, onupdate=datetime.now)
    deleted_at = sa.Column(sa.DateTime, nullable=True)
    finished_at = AnnotatedColumn(sa.DateTime, _a_label=_(u'カート処理日時'))

    shipping_address_id = sa.Column(Identifier, sa.ForeignKey("ShippingAddress.id"))
    shipping_address = orm.relationship('ShippingAddress', backref='cart')
    payment_delivery_method_pair_id = sa.Column(Identifier, sa.ForeignKey("PaymentDeliveryMethodPair.id"))
    payment_delivery_pair = orm.relationship("PaymentDeliveryMethodPair")

    _order_no = AnnotatedColumn("order_no", sa.String(255), _a_label=_(u'注文番号'))
    order_id = sa.Column(Identifier, sa.ForeignKey("Order.id"))
    order = declared_attr(lambda self: orm.relationship('Order', backref=orm.backref('cart', uselist=False)))
    operator_id = sa.Column(Identifier, sa.ForeignKey("Operator.id"))
    operator = orm.relationship('Operator', backref='orders')
    channel = sa.Column(sa.Integer, nullable=True)

    sales_segment_group_id = sa.Column(Identifier, sa.ForeignKey('SalesSegmentGroup.id'))
    sales_segment_group = orm.relationship('SalesSegmentGroup')

    sales_segment_id = sa.Column(Identifier, sa.ForeignKey('SalesSegment.id'))
    sales_segment = orm.relationship('SalesSegment')

    disposed = False

    browserid = sa.Column(sa.String(40))

    organization_id = sa.Column(Identifier,
                                sa.ForeignKey('Organization.id'))
    organization = orm.relationship('Organization')

    cart_setting_id = sa.Column(Identifier, sa.ForeignKey('CartSetting.id'), nullable=False)
    cart_setting = orm.relationship('CartSetting')

    user_agent = sa.Column(sa.VARBINARY(200), nullable=True)

    membership_id = sa.Column(Identifier, sa.ForeignKey('Membership.id'), nullable=True)
    membership = orm.relationship('Membership')

    membergroup_id = sa.Column(Identifier, sa.ForeignKey('MemberGroup.id'), nullable=True)
    membergroup = orm.relationship('MemberGroup')

    user_point_accounts = orm.relationship('UserPointAccount', secondary=cart_user_point_account_table)

    @property
    def products(self):
        return self.items

    @products.setter
    def products(self, value):
        self.items = value

    products = deprecated(products, "use items property instead")

    @property
    def name(self):
        return str(self.performance.id)

    @classmethod
    @deprecate("this function does not take it account that a cart is not associated to a single performance")
    def create(cls, request, **kwargs):
        performance_id = kwargs.pop('performance_id', None)
        if performance_id is None:
            performance = kwargs.pop('performance', None)
            if performance is None:
                raise Exception('performance or performance_id must be specified')
            performance_id = performance.id
        else:
            performance = c_models.Performance.query.filter_by(id=performance_id).one()
        organization = performance.event.organization
        logger.debug("organization.id = %d" % organization.id)
        order_no = c_api.get_next_order_no(request, organization)

        if 'organization' not in kwargs and 'organization_id' not in kwargs:
            kwargs['organization_id'] = performance.event.organization_id

        new_cart = cls(
            _order_no=order_no,
            performance=performance,
            performance_id=performance_id,
            **kwargs)
        DBSession.add(new_cart)
        return new_cart

    @classmethod
    def create_from(cls, request, that):
        # すでに detach しているかもしれないので、merge を試みる
        that = DBSession.merge(that)
        if that.order_id is not None:
            raise CartCreationException(
                request,
                "Cannot translate the contents of a cart that has already been associated to the order",
                performance_id=that.performance_id,
                sales_segment_id=that.sales_segment_id
                )
        if that.finished_at is not None:
            raise CartCreationException(
                request,
                "Cannot translate the contents of a cart that has already been marked as finished",
                performance_id=that.performance_id,
                sales_segment_id=that.sales_segment_id
                )
        new_cart = cls.create(
            cart_session_id=that.cart_session_id,
            shipping_address_id=that.shipping_address_id,
            payment_delivery_method_pair_id=that.payment_delivery_method_pair_id,
            performance_id=that.performance_id,
            sales_segment_id=that.sales_segment_id,
            sales_segment_group_id=that.sales_segment_group_id
            )
        # translate all the products in the specified cart to the new cart
        for carted_product in that.items:
            new_cart.items.append(carted_product)
        that.disposed = True
        that.products = []
        return new_cart

    @hybrid_property
    def order_no(self):
        if self._order_no is None:
            raise InvalidCartStatusError(cart_id=self.id)
        return self._order_no

    @order_no.expression
    def order_no_expr(cls):
        return cls._order_no

    @property
    def total_amount(self):
        try:
            return c_api.calculate_total_amount(self)
        except Exception as e:
            raise InvalidCartStatusError(self.id)


    @property
    def delivery_fee(self):
        """ 引取手数料 """
        return self.sales_segment.get_delivery_fee(
            self.payment_delivery_pair,
            [(p.product, p.quantity) for p in self.items])

    @property
    def transaction_fee(self):
        """ 決済手数料 """
        return self.sales_segment.get_transaction_fee(
            self.payment_delivery_pair,
            [(p.product, p.quantity) for p in self.items])

    @property
    def system_fee(self):
        """システム利用料"""
        return self.sales_segment.get_system_fee(
            self.payment_delivery_pair,
            [(p.product, p.quantity) for p in self.items])

    @property
    def special_fee(self):
        """特別手数料"""
        return self.sales_segment.get_special_fee(
            self.payment_delivery_pair,
            [(p.product, p.quantity) for p in self.items])

    @property
    def special_fee_name(self):
        """特別手数料名称"""
        return self.payment_delivery_pair.special_fee_name

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
    def is_expired(self, expire_span_minutes, now):
        """ 決済完了までの時間制限
        """
        assert isinstance(now, datetime)
        return self.created_at < (now - timedelta(minutes=expire_span_minutes))

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
        for item in self.items:
            item.finish()
        self.finished_at = datetime.now() # SAFE TO USE datetime.now() HERE

    def release(self):
        """ カート開放
        """
        logger.info('trying to release Cart (id=%d, order_no=%s)' % (self.id, self._order_no))
        carted_products = object_session(self).query(CartedProduct) \
            .with_lockmode('update') \
            .filter(CartedProduct.cart_id == self.id) \
            .all()
        for item in carted_products:
            if not item.release():
                return False
        return True

    def is_valid(self):
        return all(item.is_valid() for item in self.items)

    @classmethod
    def from_order_no(cls, order_no):
        return Cart.query.filter_by(_order_no=order_no).one()

    @property
    def user(self):
        """いずれは、Cartにもuser_idをカラムとして持たせたい"""
        return self.shipping_address and self.shipping_address.user

    @user.setter
    def user(self, value):
        """いずれは、Cartにもuser_idをカラムとして持たせたい"""
        # XXX: 自動的に ShippingAddress はアサインしない
        assert self.shipping_address is not None
        self.shipping_address.user = value

    @property
    def user_id(self):
        """いずれは、Cartにもuser_idをカラムとして持たせたい"""
        return self.shipping_address and self.shipping_address.user_id 


@implementer(IOrderedProductLike)
class CartedProduct(Base):
    __tablename__ = 'CartedProduct'

    query = DBSession.query_property()

    id = sa.Column(Identifier, primary_key=True)
    quantity = sa.Column(sa.Integer)
    cart_id = sa.Column(Identifier, sa.ForeignKey(Cart.id, onupdate='cascade', ondelete='cascade'))
    cart = orm.relationship("Cart", backref="items", cascade='all')

    product_id = sa.Column(Identifier, sa.ForeignKey("Product.id"))
    product = orm.relationship("Product")

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, nullable=True, onupdate=datetime.now)
    deleted_at = sa.Column(sa.DateTime, nullable=True)
    finished_at = sa.Column(sa.DateTime)

    organization_id = sa.Column(Identifier,
                                sa.ForeignKey('Organization.id'))
    organization = orm.relationship('Organization', backref='carted_products')

    @property
    def items(self):
        return self.elements

    @items.setter
    def items(self, value):
        self.elements = value

    items = deprecated(items, 'use elements property instead')

    @property
    def amount(self):
        """ 購入額小計
        """
        return self.product.price * self.quantity

    @property
    def price(self):
        return self.product.price

    @property
    def seats(self):
        return sorted(itertools.chain.from_iterable(i.seatdicts for i in self.elements),
            key=operator.itemgetter('l0_id'))

    @property
    def seat_quantity(self):
        quantity = 0
        for item in self.items:
            if item.product_item.stock_type.is_seat:
                quantity += item.quantity
        return quantity

    @deprecate("deprecated method")
    def pop_seats(self, seats, performance_id):
        for product_item in self.product.items:
            if product_item.performance_id != performance_id:
                continue
            cart_product_item = CartedProductItem(carted_product=self, quantity=self.quantity, product_item=product_item)
            seats = cart_product_item.pop_seats(seats)
        return seats

    # @deprecate("deprecated method")
    # used by Cart.add_products
    def adjust_items(self, performance_id):
        for product_item in self.product.items:
            if product_item.performance_id != performance_id:
                continue
            cart_product_item = CartedProductItem(carted_product=self, quantity=product_item.quantity * self.quantity, product_item=product_item)

    @classmethod
    def get_reserved_amount(cls, product_item):
        return DBSession.query(sql.func.sum(cls.amount)).filter(cls.product_item==product_item).filter(cls.state=="reserved").first()[0] or 0

    def _mark_finished(self):
        self.finished_at = datetime.now() # SAFE TO USE datetime.now() HERE

    def finish(self):
        """ 決済処理
        """
        for element in self.elements:
            element.finish()
        self._mark_finished()

    def release(self):
        """ 開放
        """
        logger.info('trying to release CartedProduct (id=%d)' % self.id)
        if not self.finished_at:
            carted_product_items = object_session(self).query(CartedProductItem) \
                .with_lockmode('update') \
                .filter(CartedProductItem.carted_product_id == self.id) \
                .all()
            for element in carted_product_items:
                if not element.release():
                    logger.info('returing False to abort. NO FURTHER SQL EXECUTION IS SUPPOSED!')
                    return False
            self._mark_finished()
            logger.info('CartedProduct (id=%d) successfully released' % self.id)
        else:
            logger.info('CartedProduct (id=%d) is already marked finished' % self.id)
        return True

    def is_valid(self):
        return all(element.is_valid() for element in self.elements)


@implementer(IOrderedProductItemLike)
class CartedProductItem(Base):
    """ カート内プロダクトアイテム + 座席 + 座席状況
    """
    __tablename__ = 'CartedProductItem'
    query = DBSession.query_property()

    id = sa.Column(Identifier, primary_key=True)

    quantity = sa.Column(sa.Integer)

    product_item_id = sa.Column(Identifier, sa.ForeignKey("ProductItem.id"))

    #seat_status_id = sa.Column(sa.Integer, sa.ForeignKey(""))

    product_item = orm.relationship("ProductItem", backref='carted_product_items')
    seats = orm.relationship("Seat", secondary=cart_seat_table)
    #seat_status = orm.relationship("SeatStatus")

    carted_product_id = sa.Column(Identifier, sa.ForeignKey(CartedProduct.id, onupdate='cascade', ondelete='cascade'))
    carted_product = orm.relationship("CartedProduct", backref="elements", cascade='all')

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, nullable=True, onupdate=datetime.now)
    deleted_at = sa.Column(sa.DateTime, nullable=True)
    finished_at = sa.Column(sa.DateTime)
    organization_id = sa.Column(Identifier,
                                sa.ForeignKey('Organization.id'))
    organization = orm.relationship('Organization', backref='carted_product_items')

    @property
    def seatdicts(self):
        return ({'name': s.name, 'l0_id': s.l0_id}
                for s in self.seats)

    @property
    def price(self):
        return self.product_item.price

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
        if len(self.seats) > 0:
            return DBSession.query(c_models.SeatStatus).filter(c_models.SeatStatus.seat_id.in_([s.id for s in self.seats])).all()
        else:
            return []

    @property
    def seat_statuses_for_update(self):
        """ 確保済の座席ステータス
        """
        if len(self.seats) > 0:
            # although seat_id is the primary key, optimizer may wrongly choose other index
            # if IN predicate has many values, because of implicit "deleted_at IS NULL" (#11358)
            return DBSession.query(c_models.SeatStatus).filter(c_models.SeatStatus.seat_id.in_([s.id for s in self.seats]))\
                .with_hint(c_models.SeatStatus, 'USE INDEX (primary)').with_lockmode('update').all()
        else:
            return []

    def _mark_finished(self):
        self.finished_at = datetime.now() # SAFE TO USE datetime.now() HERE

    def finish(self):
        """ 決済処理
        """
        for seat_status in self.seat_statuses_for_update:
            if seat_status.status != int(c_models.SeatStatusEnum.InCart):
                raise NoCartError()
            seat_status.status = int(c_models.SeatStatusEnum.Ordered)
        self._mark_finished()

    def release(self):
        logger.info('trying to release CartedProductItem (id=%d)' % self.id)
        if not self.finished_at:
            stock_status = c_models.StockStatus.filter_by(stock_id=self.product_item.stock_id).with_lockmode('update').one()
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
            logger.info('restoring the quantity of stock (id=%s, quantity=%d) by +%d' % (stock_status.stock_id, stock_status.quantity, release_quantity))
            stock_status.quantity += release_quantity
            stock_status.save()
            self._mark_finished()
            logger.info('done for CartedProductItem (id=%d)' % self.id)
        else:
            logger.info('CartedProductItem (id=%d) is already marked finished' % self.id)
        return True

    def is_valid(self):
        for seat_status in self.seat_statuses:
            if seat_status.status != int(c_models.SeatStatusEnum.InCart):
                return False
        return True


@implementer(ICartSetting)
class CartSetting(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'CartSetting'

    id = sa.Column(Identifier, primary_key=True)
    organization_id = sa.Column(Identifier,
                                sa.ForeignKey('Organization.id'))
    organization = orm.relationship('Organization')
    name = AnnotatedColumn(sa.Unicode(128), nullable=False, default=u'', _a_label=_(u"設定名称"))
    type = AnnotatedColumn(sa.Unicode(64), nullable=False, default=u'', _a_label=_(u"設定のタイプ"))
    data = sa.Column(MutationDict.as_mutable(JSONEncodedDict(16384)), nullable=False, default={}, server_default='{}')
    performance_selector = AnnotatedColumn(sa.Unicode(128), doc=u"カートでの公演絞り込み方法", _a_label=_(u"公演絞り込み方式"))
    performance_selector_label1_override = AnnotatedColumn(sa.Unicode(128), nullable=True, _a_label=_(u'絞り込みラベル1'), _a_visible_column=True)
    performance_selector_label2_override = AnnotatedColumn(sa.Unicode(128), nullable=True, _a_label=_(u'絞り込みラベル2'), _a_visible_column=True)
    auth_type = AnnotatedColumn(sa.Unicode(255), _a_label=u"認証方式")
    secondary_auth_type = AnnotatedColumn(sa.Unicode(255), _a_label=u"副認証方式")

    @property
    def auth_types(self):
        retval = []
        if self.auth_type is not None:
            retval.append(self.auth_type)
        if self.secondary_auth_type is not None:
            retval.append(self.secondary_auth_type)
        return retval

    @property
    def default_prefecture(self):
        return self.data.get('default_prefecture')

    @default_prefecture.setter
    def default_prefecture(self, value):
        if self.data is None:
            self.data = {}
        self.data['default_prefecture'] = value

    @property
    def flavors(self):
        return self.data.get('flavors')

    @flavors.setter
    def flavors(self, value):
        if self.data is None:
            self.data = {}
        self.data['flavors'] = value

    @property
    def title(self):
        return self.data.get('title')

    @title.setter
    def title(self, value):
        if self.data is None:
            self.data = {}
        self.data['title'] = value

    @property
    def fc_kind_title(self):
        return self.data.get('fc_kind_title')

    @fc_kind_title.setter
    def fc_kind_title(self, value):
        if self.data is None:
            self.data = {}
        self.data['fc_kind_title'] = value

    @property
    def fc_name(self):
        return self.data.get('fc_name')

    @fc_name.setter
    def fc_name(self, value):
        if self.data is None:
            self.data = {}
        self.data['fc_name'] = value

    @property
    def lots_date_title(self):
        return self.data.get('lots_date_title')

    @lots_date_title.setter
    def lots_date_title(self, value):
        if self.data is None:
            self.data = {}
        self.data['lots_date_title'] = value

    @property
    def contact_url(self):
        return self.data.get('contact_url')

    @contact_url.setter
    def contact_url(self, value):
        if self.data is None:
            self.data = {}
        self.data['contact_url'] = value

    @property
    def contact_url_mobile(self):
        return self.data.get('contact_url_mobile')

    @contact_url_mobile.setter
    def contact_url_mobile(self, value):
        if self.data is None:
            self.data = {}
        self.data['contact_url_mobile'] = value

    @property
    def contact_tel(self):
        return self.data.get('contact_tel')

    @contact_tel.setter
    def contact_tel(self, value):
        if self.data is None:
            self.data = {}
        self.data['contact_tel'] = value

    @property
    def contact_office_hours(self):
        return self.data.get('contact_office_hours')

    @contact_office_hours.setter
    def contact_office_hours(self, value):
        if self.data is None:
            self.data = {}
        self.data['contact_office_hours'] = value

    @property
    def contact_name(self):
        return self.data.get('contact_name')

    @contact_name.setter
    def contact_name(self, value):
        if self.data is None:
            self.data = {}
        self.data['contact_name'] = value

    @property
    def mobile_marker_color(self):
        return self.data.get('mobile_marker_color')

    @mobile_marker_color.setter
    def mobile_marker_color(self, value):
        if self.data is None:
            self.data = {}
        self.data['mobile_marker_color'] = value

    @property
    def mobile_required_marker_color(self):
        return self.data.get('mobile_required_marker_color')

    @mobile_required_marker_color.setter
    def mobile_required_marker_color(self, value):
        if self.data is None:
            self.data = {}
        self.data['mobile_required_marker_color'] = value

    @property
    def mobile_header_background_color(self):
        return self.data.get('mobile_header_background_color')

    @mobile_header_background_color.setter
    def mobile_header_background_color(self, value):
        if self.data is None:
            self.data = {}
        self.data['mobile_header_background_color'] = value

    @property
    def fc_announce_page_url(self):
        return self.data.get('fc_announce_page_url')

    @fc_announce_page_url.setter
    def fc_announce_page_url(self, value):
        if self.data is None:
            self.data = {}
        self.data['fc_announce_page_url'] = value

    @property
    def fc_announce_page_url_mobile(self):
        return self.data.get('fc_announce_page_url_mobile')

    @fc_announce_page_url_mobile.setter
    def fc_announce_page_url_mobile(self, value):
        if self.data is None:
            self.data = {}
        self.data['fc_announce_page_url_mobile'] = value

    @property
    def fc_announce_page_title(self):
        return self.data.get('fc_announce_page_title')

    @fc_announce_page_title.setter
    def fc_announce_page_title(self, value):
        if self.data is None:
            self.data = {}
        self.data['fc_announce_page_title'] = value

    @property
    def privacy_policy_page_url(self):
        return self.data.get('privacy_policy_page_url')

    @privacy_policy_page_url.setter
    def privacy_policy_page_url(self, value):
        if self.data is None:
            self.data = {}
        self.data['privacy_policy_page_url'] = value

    @property
    def privacy_policy_page_url_mobile(self):
        return self.data.get('privacy_policy_page_url_mobile')

    @privacy_policy_page_url_mobile.setter
    def privacy_policy_page_url_mobile(self, value):
        if self.data is None:
            self.data = {}
        self.data['privacy_policy_page_url_mobile'] = value

    @property
    def legal_notice_page_url(self):
        return self.data.get('legal_notice_page_url')

    @legal_notice_page_url.setter
    def legal_notice_page_url(self, value):
        if self.data is None:
            self.data = {}
        self.data['legal_notice_page_url'] = value

    @property
    def legal_notice_page_url_mobile(self):
        return self.data.get('legal_notice_page_url_mobile')

    @legal_notice_page_url_mobile.setter
    def legal_notice_page_url_mobile(self, value):
        if self.data is None:
            self.data = {}
        self.data['legal_notice_page_url_mobile'] = value

    @property
    def orderreview_page_url(self):
        return self.data.get('orderreview_page_url')

    @orderreview_page_url.setter
    def orderreview_page_url(self, value):
        if self.data is None:
            self.data = {}
        self.data['orderreview_page_url'] = value

    @property
    def lots_orderreview_page_url(self):
        return self.data.get('lots_orderreview_page_url')

    @lots_orderreview_page_url.setter
    def lots_orderreview_page_url(self, value):
        if self.data is None:
            self.data = {}
        self.data['lots_orderreview_page_url'] = value

    @property
    def extra_footer_links(self):
        return self.data.get('extra_footer_links')

    @extra_footer_links.setter
    def extra_footer_links(self, value):
        if self.data is None:
            self.data = {}
        self.data['extra_footer_links'] = value

    @property
    def extra_footer_links_mobile(self):
        return self.data.get('extra_footer_links_mobile')

    @extra_footer_links_mobile.setter
    def extra_footer_links_mobile(self, value):
        if self.data is None:
            self.data = {}
        self.data['extra_footer_links_mobile'] = value

    @property
    def mail_filter_domain_notice_template(self):
        return self.data.get('mail_filter_domain_notice_template')

    @mail_filter_domain_notice_template.setter
    def mail_filter_domain_notice_template(self, value):
        if self.data is None:
            self.data = {}
        self.data['mail_filter_domain_notice_template'] = value

    @property
    def extra_form_fields(self):
        return self.data.get('extra_form_fields')

    @extra_form_fields.setter
    def extra_form_fields(self, value):
        if self.data is None:
            self.data = {}
        self.data['extra_form_fields'] = value

    @property
    def header_image_url(self):
        return self.data.get('header_image_url')

    @header_image_url.setter
    def header_image_url(self, value):
        if self.data is None:
            self.data = {}
        self.data['header_image_url'] = value

    @property
    def header_image_url_mobile(self):
        return self.data.get('header_image_url_mobile')

    @header_image_url_mobile.setter
    def header_image_url_mobile(self, value):
        if self.data is None:
            self.data = {}
        self.data['header_image_url_mobile'] = value

    @property
    def booster_or_fc_cart(self):
        from .schemas import extra_form_type_map
        return self.type in extra_form_type_map

    @property
    def booster_cart(self):
        return self.booster_or_fc_cart and not self.fc_cart

    @property
    def fc_cart(self):
        return self.type == 'fc'

    @property
    def hidden_venue_html(self):
        return self.data.get('hidden_venue_html')

    @hidden_venue_html.setter
    def hidden_venue_html(self, value):
        if self.data is None:
            self.data = {}
        self.data['hidden_venue_html'] = value

    @property
    def embedded_html_complete_page(self):
        return self.data.get('embedded_html_complete_page')

    @embedded_html_complete_page.setter
    def embedded_html_complete_page(self, value):
        if self.data is None:
            self.data = {}
        self.data['embedded_html_complete_page'] = value

    @property
    def embedded_html_complete_page_mobile(self):
        return self.data.get('embedded_html_complete_page_mobile')

    @embedded_html_complete_page_mobile.setter
    def embedded_html_complete_page_mobile(self, value):
        if self.data is None:
            self.data = {}
        self.data['embedded_html_complete_page_mobile'] = value

    @property
    def embedded_html_complete_page_smartphone(self):
        return self.data.get('embedded_html_complete_page_smartphone')

    @embedded_html_complete_page_smartphone.setter
    def embedded_html_complete_page_smartphone(self, value):
        if self.data is None:
            self.data = {}
        self.data['embedded_html_complete_page_smartphone'] = value

    @property
    def nogizaka46_auth_key(self):
        return self.data.get('nogizaka46_auth_key')

    @nogizaka46_auth_key.setter
    def nogizaka46_auth_key(self, value):
        if self.data is None:
            self.data = {}
        self.data['nogizaka46_auth_key'] = value

    @property
    def oauth_client_id(self):
        return self.data.get('oauth_client_id')

    @oauth_client_id.setter
    def oauth_client_id(self, value):
        if self.data is None:
            self.data = {}
        self.data['oauth_client_id'] = value

    @property
    def oauth_client_secret(self):
        return self.data.get('oauth_client_secret')

    @oauth_client_secret.setter
    def oauth_client_secret(self, value):
        if self.data is None:
            self.data = {}
        self.data['oauth_client_secret'] = value

    @property
    def oauth_endpoint_authz(self):
        return self.data.get('oauth_endpoint_authz')

    @oauth_endpoint_authz.setter
    def oauth_endpoint_authz(self, value):
        if self.data is None:
            self.data = {}
        self.data['oauth_endpoint_authz'] = value

    @property
    def oauth_endpoint_api(self):
        return self.data.get('oauth_endpoint_api')

    @oauth_endpoint_api.setter
    def oauth_endpoint_api(self, value):
        if self.data is None:
            self.data = {}
        self.data['oauth_endpoint_api'] = value

    @property
    def oauth_endpoint_token(self):
        return self.data.get('oauth_endpoint_token')

    @oauth_endpoint_token.setter
    def oauth_endpoint_token(self, value):
        if self.data is None:
            self.data = {}
        self.data['oauth_endpoint_token'] = value

    @property
    def oauth_endpoint_token_revocation(self):
        return self.data.get('oauth_endpoint_token_revocation')

    @oauth_endpoint_token_revocation.setter
    def oauth_endpoint_token_revocation(self, value):
        if self.data is None:
            self.data = {}
        self.data['oauth_endpoint_token_revocation'] = value

    @property
    def oauth_scope(self):
        return self.data.get('oauth_scope')

    @oauth_scope.setter
    def oauth_scope(self, value):
        if self.data is None:
            self.data = {}
        self.data['oauth_scope'] = value

    @property
    def openid_prompt(self):
        return self.data.get('openid_prompt')

    @openid_prompt.setter
    def openid_prompt(self, value):
        if self.data is None:
            self.data = {}
        self.data['openid_prompt'] = value


