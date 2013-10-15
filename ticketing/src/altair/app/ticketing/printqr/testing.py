# -*- coding:utf-8 -*-
from datetime import datetime
import sqlalchemy as sa
_engine = None

def setUpSwappedDB():
    from altair.app.ticketing.core.models import Base
    import sqlahelper
    try:
        engine__ = sqlahelper.get_engine()
    except RuntimeError:
        engine__ = sa.create_engine("sqlite://", echo=False)
        sqlahelper.add_engine(engine__)
        assert Base.metadata.bind == sqlahelper.get_engine()
        Base.metadata.create_all()
    global _engine
    from altair.app.ticketing.models import Base
    engine = sa.create_engine("sqlite://", echo=False)
    _engine = swap_engine(engine)
    assert engine__ != engine
    assert Base.metadata.bind == engine
    Base.metadata.create_all()

def tearDownSwappedDB():
    global _engine
    swap_engine(_engine)


def set_default_engine(engine, name="default"):
    "i hate sqlahelper"
    import sqlahelper
    sqlahelper._engines[name] = engine

def swap_engine(engine):
    import sqlahelper
    from altair.app.ticketing.core.models import DBSession
    base = sqlahelper.get_base()
    old_engine = sqlahelper.get_engine()

    session = sqlahelper.get_session()
    assert session == DBSession
    session.remove()

    assert old_engine == session.bind == base.metadata.bind
    set_default_engine(engine)
    base.metadata.bind = engine
    session.configure(bind=engine)
    session.bind = engine ## xxx:
    assert engine == base.metadata.bind
    assert engine == session.bind
    return old_engine

def get_ordered_product_item__full_relation(quantity, quantity_only):
    from altair.app.ticketing.core.models import OrderedProductItemToken
    from altair.app.ticketing.core.models import OrderedProductItem
    from altair.app.ticketing.core.models import OrderedProduct
    from altair.app.ticketing.core.models import Stock
    from altair.app.ticketing.core.models import StockStatus
    from altair.app.ticketing.core.models import StockType
    from altair.app.ticketing.core.models import StockHolder
    from altair.app.ticketing.core.models import Performance
    from altair.app.ticketing.core.models import PerformanceSetting
    from altair.app.ticketing.core.models import Product
    from altair.app.ticketing.core.models import ProductItem
    from altair.app.ticketing.core.models import Order
    from altair.app.ticketing.core.models import ShippingAddress
    from altair.app.ticketing.core.models import SalesSegment
    from altair.app.ticketing.core.models import SalesSegmentGroup
    from altair.app.ticketing.core.models import Event
    from altair.app.ticketing.core.models import Organization
    from altair.app.ticketing.core.models import TicketBundle
    from altair.app.ticketing.core.models import Venue
    from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
    from altair.app.ticketing.core.models import PaymentMethod
    from altair.app.ticketing.core.models import DeliveryMethod

    sales_segment = SalesSegment(start_at=datetime(2000, 1, 1), 
                         end_at=datetime(2000, 1, 1, 23), 
                         upper_limit=8, 
                         seat_choice=True
                         )
    sales_segment.sales_segment_group = SalesSegmentGroup(
        name=":SalesSegmentGroup:name", 
        kind=":kind")

    shipping_address = ShippingAddress(
        email_1=":email_1",
        email_2=":email_2",
        nick_name=":nick_name",
        first_name=":first_name",
        last_name=":last_name",
        first_name_kana=":first_name_kana",
        last_name_kana=":last_name_kana",
        zip=":zip",
        country=":country",
        prefecture=":prefecture",
        city=":city",
        address_1=":address_1",
        address_2=":address_2",
        tel_1=":tel_1",
        tel_2=":tel_2",
        fax=":fax",
        )
    order = Order(shipping_address=shipping_address, 
                  total_amount=600, 
                  system_fee=100, 
                  transaction_fee=200, 
                  delivery_fee=300, 
                  multicheckout_approval_no=":multicheckout_approval_no", 
                  order_no=":order_no", 
                  paid_at=datetime(2000, 1, 1, 1, 10), 
                  delivered_at=None, 
                  canceled_at=None, 
                  created_at=datetime(2000, 1, 1, 1), 
                  issued_at=datetime(2000, 1, 1, 1, 13),                                        
                  )
    payment_delivery_method_pair = order.payment_delivery_pair = PaymentDeliveryMethodPair(system_fee=100, transaction_fee=200, delivery_fee=300, )
    payment_method = payment_delivery_method_pair.payment_method = PaymentMethod(name=":PaymentMethod:name", 
                          fee=300, 
                          fee_type=1, 
                          payment_plugin_id=2)
    delivery_method = payment_delivery_method_pair.delivery_method = DeliveryMethod(name=":DeliveryMethod:name", 
                          fee=300, 
                          fee_type=1, 
                          delivery_plugin_id=2)
    ordered_product = OrderedProduct(price=12000, 
                                     quantity=quantity)
    ordered_product.order = order
    ordered_product_item = OrderedProductItem(id=1, price=14000, quantity=quantity)
    ordered_product_item.ordered_product = ordered_product
    product_item = ordered_product_item.product_item = ProductItem(name=":ProductItem:name", 
                        price=12000, 
                        quantity=quantity, 
                        )
    product = product_item.product = Product(name=":Product:name", 
                                             price=10000)
    ordered_product.product = product
    product_item.product.sales_segment = sales_segment
    performance = product_item.performance = Performance(name=":Performance:name",
                       code=":code", 
                       open_on=datetime(2000, 1, 1), 
                       start_on=datetime(2000, 1, 1, 10), 
                       end_on=datetime(2000, 1, 1, 23), 
                       abbreviated_title=":PerformanceSetting:abbreviated_title", 
                       subtitle=":PerformanceSetting:subtitle", 
                       note=":PerformanceSetting:note")
    performance.settings.append(PerformanceSetting())

    venue = performance.venue = Venue(name=":Venue:name", 
                                      sub_name=":sub_name")

    event = performance.event = Event(title=":Event:title",
                  abbreviated_title=":abbreviated_title", 
                  code=":Event:code")
    event.organization = Organization(name=":Organization:name", 
                                      code=":Organization:code")
    ticket_bundle = event.ticket_bundle = TicketBundle()
    ticket_bundle.attributes = {"key": "value"}
    product_item.ticket_bundle = ticket_bundle
    stock = product_item.stock = Stock(quantity=10)
    stock.stock_type = StockType(name=":StockType:name", type=":type", display_order=50, quantity_only=quantity_only)
    stock.stock_holder = StockHolder(name=":StockHolder:name")
    stock.stock_status = StockStatus(quantity=10)
    return ordered_product_item
