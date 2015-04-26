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
    user                  = Attribute(u"")

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

class ISettingRenderer(Interface):
    def __iter__():
        pass

class ICoreModelTraverser(Interface):
    def begin_event(event):
        pass

    def end_event(event):
        pass

    def visit_event_setting(event_setting):
        pass

    def begin_sales_segment_group(sales_segment_group):
        pass

    def end_sales_segment_group(sales_segment_group):
        pass

    def visit_sales_segment_group_setting(sales_segment_group_setting):
        pass

    def visit_stock_type(stock_type):
        pass

    def visit_stock_holder(stock_holder):
        pass

    def visit_payment_delivery_method_pair(payment_delivery_method_pair):
        pass

    def begin_ticket_bundle(ticket_bundle):
        pass

    def visit_ticket_bundle_attribute(ticket_bundle_attribute):
        pass

    def end_ticket_bundle(ticket_bundle):
        pass

    def visit_ticket(ticket):
        pass

    def begin_lot(lot):
        pass

    def end_lot(lot):
        pass

    def begin_performance(performance):
        pass

    def end_performance(performance):
        pass

    def visit_performance_setting(performance_setting):
        pass

    def visit_stock(stock):
        pass

    def begin_sales_segment(sales_segment):
        pass

    def end_sales_segment(sales_segment):
        pass

    def visit_sales_segment_setting(sales_segment_setting):
        pass

    def begin_product(product):
        pass

    def end_product(product):
        pass

    def visit_product_item(product_item):
        pass

    def begin_venue(venue):
        pass

    def end_venue(venue):
        pass

    def begin_venue_area(venue_area):
        pass

    def end_venue_area(venue_area):
        pass

    def begin_seat(seat):
        pass

    def end_seat(seat):
        pass

    def visit_seat_attribute(seat_attribute):
        pass

    def begin_seat_index_type(seat_index_type):
        pass

    def end_seat_index_type(seat_index_type):
        pass

    def visit_seat_index(seat_index):
        pass
