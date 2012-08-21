# encoding: utf-8

from ..users.models import SexEnum

SEX_TO_STRING_MAP = {
    SexEnum.NoAnswer.v: u'未回答',
    SexEnum.Male.v: u'男性',
    SexEnum.Female.v: u'女性'
    }

def sex_as_string(sex):
    return SEX_TO_STRING_MAP[sex] 

def format_date(date):
    return unicode(date.strftime('%Y年 %0m月 %0d日'), 'utf-8')

def format_time(time):
    return unicode(time.strftime('%H時 %M分'), 'utf-8')

def datetime_as_dict(dt):
    return {
        u'year': dt.year, u'month': dt.month, u'day': dt.day,
        u'hour': dt.hour, u'minute': dt.minute, u'second': dt.second
        } if dt is not None else None

def build_dict_from_stock(stock, retval=None):
    retval = retval or {}
    stock_holder = stock.stock_holder
    stock_type = stock.stock_type
    stock_status = stock.stock_status
    retval.update({
        u'stock': {
            u'quantity': stock.quantity
            },
        u'stockStatus': {
            u'quantity': stock_status.quantity
            },
        u'stockHolder': {
            u'name': stock_holder.name
            },
        u'stockType': {
            u'name': stock_type.name,
            u'type': stock_type.type,
            u'display_order': stock_type.display_order,
            u'quantity_only': stock_type.quantity_only
            },
        u'席種名': stock_type.name,
        })
    return retval

def build_dict_from_venue(venue, retval=None):
    retval = retval or {}
    performance = venue.performance
    event = performance.event
    organization = event.organization
    retval.update({
        u'organization': {
            u'name': organization.name,
            u'code': organization.code
            },
        u'event': {
            u'code': event.code,
            u'title': event.title,
            u'abbreviated_title': event.abbreviated_title,
            },
        u'performance': {
            u'name': performance.name,
            u'code': performance.code,
            u'open_on': datetime_as_dict(performance.open_on),
            u'start_on': datetime_as_dict(performance.start_on),
            u'end_on': datetime_as_dict(performance.end_on)
            },
        u'venue': {
            u'name': venue.name,
            u'sub_name': venue.sub_name
            },
        u'イベント名': event.title,
        u'パフォーマンス名': performance.name,
        u'対戦名': performance.name,
        u'会場名': venue.name,
        u'公演コード': performance.code,
        u'開催日': format_date(performance.start_on),
        u'開場時刻': format_time(performance.open_on),
        u'開始時刻': format_time(performance.start_on),
        u'終了時刻': format_time(performance.end_on),
        })
    return retval
    
def build_dict_from_seat(seat, ticket_number_issuer=None):
    retval = {}
    retval = build_dict_from_stock(seat.stock, retval)
    retval = build_dict_from_venue(seat.venue, retval)
    retval.update({
            u'seat': {
                u'l0_id': seat.l0_id,
                u'seat_no': seat.seat_no,
                u'name': seat.name,
                },
            u'seatAttributes': seat.attributes,
            u'席番': seat.name,
            u'発券番号': ticket_number_issuer() if ticket_number_issuer else None
            })
    return retval

def build_dict_from_product_item(product_item):
    ticket_bundle = product_item.ticket_bundle
    product = product_item.product
    sales_segment = product.sales_segment

    retval = {
        u'salesSegment': {
            u'name': sales_segment.name,
            u'kind': sales_segment.kind,
            u'start_at': datetime_as_dict(sales_segment.start_at),
            u'end_at': datetime_as_dict(sales_segment.end_at),
            u'upper_limit': sales_segment.upper_limit,
            u'seat_choice': sales_segment.seat_choice
            }, 
        u'product': {
            u'name': product.name,
            u'price': product.price
            },
        u'productItem': {
            u'name': product_item.name,
            u'price': product_item.price,
            u'quantity': product_item.quantity
            },
        u'aux': dict(ticket_bundle.attributes), 
        u'券種名': product_item.name or product.name,
        u'商品価格': product.price,
        u'チケット価格': product_item.price,
        }

    retval = build_dict_from_stock(product_item.stock, retval)
    retval = build_dict_from_venue(product_item.performance.venue, retval)
    ## 不足分
    retval.update({
            u"席番": u"{{席番}}", 
            u'注文番号': u"{{注文番号}}",
            u'予約番号': u"{{予約番号}}", 
            u'発券番号': u"{{発券番号}}", 
            u"公演コード": u"xxx"
    })
    return retval

def build_dicts_from_ordered_product_item(ordered_product_item, user_profile=None, ticket_number_issuer=None):
    product_item = ordered_product_item.product_item
    ticket_bundle = product_item.ticket_bundle
    ordered_product = ordered_product_item.ordered_product 
    product = ordered_product.product
    order = ordered_product.order
    shipping_address = order.shipping_address
    payment_delivery_method_pair = order.payment_delivery_pair # XXX
    payment_method = payment_delivery_method_pair.payment_method
    delivery_method = payment_delivery_method_pair.delivery_method
    sales_segment = product.sales_segment

    extra = {
        u'order': {
            u'total_amount': order.total_amount,
            u'system_fee': order.system_fee,
            u'transaction_fee': order.transaction_fee,
            u'delivery_fee': order.delivery_fee,
            u'multicheckout_approval_no': order.multicheckout_approval_no,
            u'order_no': order.order_no,
            u'paid_at': datetime_as_dict(order.paid_at),
            u'delivered_at': datetime_as_dict(order.delivered_at),
            u'cancelled_at': datetime_as_dict(order.canceled_at),
            },
        u'orderedProductItem': {
            u'price': ordered_product_item.price
            },
        u'orderedProductItemAttributes': ordered_product_item.attributes,
        u'orderedProduct': {
            u'price': ordered_product.price,
            u'quantity': ordered_product.quantity
            },
        u'salesSegment': {
            u'name': sales_segment.name,
            u'kind': sales_segment.kind,
            u'start_at': datetime_as_dict(sales_segment.start_at),
            u'end_at': datetime_as_dict(sales_segment.end_at),
            u'upper_limit': sales_segment.upper_limit,
            u'seat_choice': sales_segment.seat_choice
            },
        u'paymentMethod': {
            u'name': payment_method.name,
            u'fee': payment_method.fee,
            u'fee_type': payment_method.fee_type
            },
        u'deliveryMethod': {
            u'name': delivery_method.name,
            u'fee': delivery_method.fee,
            u'fee_type': delivery_method.fee_type
            },
        u'product': {
            u'name': product.name,
            u'price': product.price
            },
        u'productItem': {
            u'name': product_item.name,
            u'price': product_item.price,
            u'quantity': product_item.quantity
            },
        u"shippingAddress": {
            u"email": shipping_address.email,
            u"nick_name": shipping_address.nick_name,
            u"first_name": shipping_address.first_name,
            u"last_name": shipping_address.last_name,
            u"first_name_kana": shipping_address.first_name_kana,
            u"last_name_kana": shipping_address.last_name_kana,
            u"zip": shipping_address.zip,
            u"country": shipping_address.country,
            u"prefecture": shipping_address.prefecture,
            u"city": shipping_address.city,
            u"address_1": shipping_address.address_1,
            u"address_2": shipping_address.address_2,
            u"tel_1": shipping_address.tel_1,
            u"tel_2": shipping_address.tel_2,
            u"fax": shipping_address.fax
            },
        u'aux': ticket_bundle.attributes,
        u'券種名': product_item.name or product.name,
        u'商品価格': ordered_product.price,
        u'チケット価格': ordered_product_item.price,
        u'注文番号': order.order_no,
        u'予約番号': order.order_no
        }

    if user_profile is not None:
        extra["userProfile"] = {
            u"email": user_profile.email,
            u"nick_name": user_profile.nick_name,
            u"first_name": user_profile.first_name,
            u"last_name": user_profile.last_name,
            u"first_name_kana": user_profile.first_name_kana,
            u"last_name_kana": user_profile.last_name_kana,
            u"birth_day": datetime_as_dict(user_profile.birth_day),
            u"sex": sex_as_string(user_profile.sex),
            u"zip": user_profile.zip,
            u"country": user_profile.country,
            u"prefecture": user_profile.prefecture,
            u"city": user_profile.city,
            u"address_1": user_profile.address_1,
            u"address_2": user_profile.address_2,
            u"tel_1": user_profile.tel_1,
            u"tel_2": user_profile.tel_2,
            u"fax": user_profile.fax,
            u"status": user_profile.status
            }

    retval = dict()
    for seat in ordered_product_item.seats:
        d = build_dict_from_seat(seat, ticket_number_issuer)
        d.update(extra)
        retval.append(d)
    return retval
