from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DummyCart(object):
    def __init__(self, id, system_fee, delivery_fee, special_fee, items=[]):
        self.id = id
        self.system_fee = system_fee
        self.delivery_fee = delivery_fee
        self.special_fee = special_fee
        self.items = items

    @property
    def total_amount(self):
        return self.system_fee + self.delivery_fee + self.special_fee + sum(item.product.price * item.quantity for item in self.items)

class DummyCartedProduct(object):
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity

class DummyProduct(object):
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price
