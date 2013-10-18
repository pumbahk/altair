from zope.interface import Interface, Attribute

class ISalesSegmentQueryable(Interface):
    def query_sales_segment(user, now, type):
        pass

class IOrderedProductLike(Interface):
    price                 = Attribute('')
    quantity              = Attribute('')
    product               = Attribute('')
    elements              = Attribute('')

class IOrderedProductItemLike(Interface):
    price                 = Attribute(u"")
    quantity              = Attribute(u"")
    product_item          = Attribute('')
    seats                 = Attribute(u"")

class IPurchase(Interface):
    order_no              = Attribute('')
    browserid             = Attribute('')
    sales_segment         = Attribute('')
    payment_delivery_pair = Attribute('')

class IOrderLike(IPurchase):
    items                 = Attribute('')
    total_amount          = Attribute(u"")
    system_fee            = Attribute(u"")
    delivery_fee          = Attribute(u"")
    transaction_fee       = Attribute(u"")
    special_fee           = Attribute(u"")
    special_fee_name      = Attribute(u"")
    shipping_address      = Attribute(u"")
    channel               = Attribute(u"")
    operator              = Attribute(u"")

class IShippingAddress(Interface):
    user_id         = Attribute(u"")
    tel_1           = Attribute(u"")
    tel_2           = Attribute(u"")
    first_name      = Attribute(u"")
    last_name       = Attribute(u"")
    first_name_kana = Attribute(u"")
    last_name_kana  = Attribute(u"")
    zip             = Attribute(u"")
    email_1         = Attribute(u"")
    email_2         = Attribute(u"")
    email           = Attribute(u"")

