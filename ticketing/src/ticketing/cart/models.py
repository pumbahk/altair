# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm.exc import NoResultFound
import sqlahelper
from sqlalchemy import sql

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

"""
カートアイテム状態

- 要求
- 仮押
- 決済中
- 決済完了
"""

import ticketing.venues.models
import ticketing.products.models
import ticketing.events.models

class CartItem(Base):
    __tablename__ = 'ticketing_cartitems'

    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    amount = sa.Column(sa.Integer)
    state = sa.Column(sa.Enum("requested", "reserved", "completed"))
    product_item_id = sa.Column(sa.Integer, sa.ForeignKey("ProductItem.id"))
    product_item = orm.relationship("ProductItem")
    cart_id = sa.Column(sa.Integer, sa.ForeignKey('ticketing_carts.id'))
    cart = orm.relation("Cart", backref="items")

    @classmethod
    def get_reserved_amount(cls, product_item):
        return DBSession.query(sql.func.sum(cls.amount)).filter(cls.product_item==product_item).filter(cls.state=="reserved").first()[0] or 0


class Cart(Base):
    __tablename__ = 'ticketing_carts'

    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    cart_session_id = sa.Column(sa.Unicode, unique=True)

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
