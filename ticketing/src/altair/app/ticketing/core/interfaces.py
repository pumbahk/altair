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
    organization_id       = Attribute('')
    order_no              = Attribute('')
    cart_setting_id       = Attribute('')
    browserid             = Attribute('')
    sales_segment         = Attribute('')
    performance           = Attribute('') # primary performance
    payment_delivery_pair = Attribute('')
    issuing_start_at      = Attribute('')
    issuing_end_at        = Attribute('')
    payment_start_at      = Attribute('')
    payment_due_at        = Attribute('')
    created_at            = Attribute('')

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

class IChainedSetting(Interface):
    super           = Attribute(u"")

class ISettingContainer(Interface): 
    setting         = Attribute(u"")

class ISetting(Interface):
    container       = Attribute(u"")

class IAllAppliedSetting(Interface):
    order_limit           = Attribute(u"")
    max_quantity_per_user = Attribute(u"")

class IOrderQueryable(Interface):
    def query_orders_by_user(user, filter_canceled, query=None):
        pass

    def query_orders_by_mailaddresses(mail_addresses, filter_canceled, query=None):
        pass
