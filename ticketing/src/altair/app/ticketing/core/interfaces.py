from zope.interface import Interface, Attribute

class ISalesSegmentQueryable(Interface):
    def query_sales_segment(user, now, type):
        pass

class IOrderedProductLike(Interface):
    product               = Attribute('')
    elements              = Attribute('')

class IOrderedProductItemLike(Interface):
    product_item          = Attribute('')

class IPurchase(Interface):
    order_no              = Attribute('')
    browserid             = Attribute('')
    sales_segment         = Attribute('')
    payment_delivery_pair = Attribute('')

class IOrderLike(IPurchase):
    items                 = Attribute('')
