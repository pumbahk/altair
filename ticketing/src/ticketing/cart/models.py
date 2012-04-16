from zope.interface import Interface
from zope.interface import Attribute
from zope.interface import implements

from datetime import datetime

from ticketing.products.models import *
from ticketing.orders.models import *

class ICart(Interface):
    order = Attribute("order")
    orderItems = Attribute("orderItems")
    assignedProductItems = Attribute("assignedProductItems")
    def restore(orderId):
        pass
    def add(product):
        pass
    def remove(orderItemId):
        pass
    def abort():
        pass
    def commit():
        pass
    def list():
        pass

class SimpleCart:

    implements(ICart)

    def __init__(self, order=None):
        self.order = Order()
        self.order.created_at = datetime.now()
        self.order.updated_at = datetime.now()
        self.orderItems = list()
        self.assignedProductItems = dict()

    def restore(self, orderId):
        #@TODO
        self.order = orderId

    def add(self, product):
        if product.put_in_cart() == True:
            order = OrderItem()
            order.product_id = product.id
            order.created_at = datetime.now()
            order.updated_at = datetime.now()
            self.orderItems.append(order)
            self.assignedProductItems[product.id] = list()
            for item in product.items:
                assigned = AssignedProductItem()
                assigned.product_item_id = item.id
                assigned.seat_stock_id = item.seatStock.id
                assigned.created_at = datetime.now()
                assigned.updated_at = datetime.now()
                self.assignedProductItems[product.id].append(assigned)
            return True
        else:
            return False

    def remove(self, orderItemId):
        #@TODO
        pass

    def abort(self):
        self.order = None
        self.orderItems = None
        self.assignedProductItems = None

    def commit(self):
        session.add(self.order)
        session.flush()
        for order in self.orderItems:
            order.order_id = self.order.id
            session.add(order)
        for k, v in self.assignedProductItems.iteritems():
            for assigned in v:
                assigned.order_id = self.order.id
                session.add(assigned)
        session.flush()

    def list(self):
        return self.orderItems
