# -*- coding:utf-8 -*-
import hashlib

from pyramid.view import view_config
import sqlahelper
import sqlalchemy as sa

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

class ReservedNumber(Base):
    __tablename__ = "reserved_number"
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    order_no = sa.Column(sa.Unicode(255), unique=True)
    number = sa.Column(sa.Unicode(32))

def create_reserved_number(request, cart):
    """ 引き換え番号生成
    """

    number = hashlib.md5(str(cart.id)).hexdigest()
    reserved_number = ReservedNumber(order_no=cart.id, number=number)
    DBSession.add(reserved_number)
    return number


@view_config(context="ticketing.orders.models.Order", name="delivery-3")
def reserved_number_viewlet(request):
    order = request.context
    reserved_number = ReservedNumber.query.filter_by(order_no=order.id).one()
    #return dict(reserved_number=reserved_number) 
    return u"引き換え番号: %s" % reserved_number.number
