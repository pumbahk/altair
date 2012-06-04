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
import sqlahelper
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy import sql
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm.exc import NoResultFound

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

cart_seat_table = sa.Table("cat_seat", Base.metadata,
    sa.Column("seat_id", sa.Integer, sa.ForeignKey("Seat.id")),
    sa.Column("cartproductitem_id", sa.Integer, sa.ForeignKey("ticketing_cartedproductitems.id")),
)

class CartedProductItem(Base):
    """ カート内プロダクトアイテム + 座席 + 座席状況
    """
    __tablename__ = 'ticketing_cartedproductitems'
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)

    quantity = sa.Column(sa.Integer)

    product_item_id = sa.Column(sa.Integer, sa.ForeignKey("ProductItem.id"))

    #seat_status_id = sa.Column(sa.Integer, sa.ForeignKey(""))

    product_item = orm.relationship("ProductItem")
    seats = orm.relationship("Seat", secondary=cart_seat_table)
    #seat_status = orm.relationship("SeatStatus")

    carted_product_id = sa.Column(sa.Integer, sa.ForeignKey("ticketing_cartedproducts.id"))
    carted_product = orm.relationship("CartedProduct", backref="items")

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, nullable=True, onupdate=datetime.now)
    deleted_at = sa.Column(sa.DateTime, nullable=True)

    def pop_seats(self, seats):
        """ 必要な座席を取り出して保持する

        必要な座席： :attr:`product_item` の stockが一致する Seat
        :param seats: list of :class:`ticketing.venues.models.Seat`
        """

        # TODO: ループじゃなくてquantityでスライスするような実装も可能
#        for i in range(self.quantity):
#            myseat = [seat for seat in seats if seat.stock_id == self.product_item.stock_id][0]
#            seats.remove(myseat)
#            self.seats.append(myseat)
        my_seats = [seat for seat in seats if seat.stock_id == self.product_item.stock_id][:self.quantity]
        map(seats.remove, my_seats)
        self.seats.extend(my_seats)
        return seats

class CartedProduct(Base):
    __tablename__ = 'ticketing_cartedproducts'

    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    quantity = sa.Column(sa.Integer)
    cart_id = sa.Column(sa.Integer, sa.ForeignKey('ticketing_carts.id'))
    cart = orm.relation("Cart", backref="products")

    product_id = sa.Column(sa.Integer, sa.ForeignKey("Product.id"))
    product = orm.relationship("Product")

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, nullable=True, onupdate=datetime.now)
    deleted_at = sa.Column(sa.DateTime, nullable=True)

    @property
    def amount(self):
        """ 購入額小計
        """
        return self.product.price * self.quantity

    def pop_seats(self, seats):
        for product_item in self.product.items:
            cart_product_item = CartedProductItem(carted_product=self, quantity=self.quantity, product_item=product_item)
            seats = cart_product_item.pop_seats(seats)
        return seats

    @classmethod
    def get_reserved_amount(cls, product_item):
        return DBSession.query(sql.func.sum(cls.amount)).filter(cls.product_item==product_item).filter(cls.state=="reserved").first()[0] or 0


class Cart(Base):
    __tablename__ = 'ticketing_carts'

    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    cart_session_id = sa.Column(sa.Unicode, unique=True)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, nullable=True, onupdate=datetime.now)
    deleted_at = sa.Column(sa.DateTime, nullable=True)

    @property
    def total_amount(self):
        return sum(cp.amount for cp in self.products)

    @classmethod
    def get_or_create(cls, cart_session_id):
        try:
            return cls.query.filter_by(cart_session_id=cart_session_id).one()
        except NoResultFound:
            cart = cls(cart_session_id=cart_session_id)
            DBSession.add(cart)
            return cart

    @classmethod
    def is_existing_cart_session_id(cls, cart_session_id):
        return cls.query.filter_by(cart_session_id=cart_session_id).count()

    @hybrid_method
    def is_expired(self, expire_span_minutes):
        """ 決済完了までの時間制限
        """
        return self.created_at > datetime.now() - timedelta(minutes=expire_span_minutes)

    def add_seat(self, seats, ordered_products):
        """ 確保した座席を追加
        :param seats: list of Seat
        :param ordered_products: list of tuple(product, quantity)
        """
        # ordered_productsでループ
        for ordered_product, quantity in ordered_products:
            # ordered_productでCartProductを作成
            cart_product = CartedProduct(cart=self, product=ordered_product, quantity=quantity)
            seats = cart_product.pop_seats(seats)
        # CartProductでseatsから必要な座席を取り出し
