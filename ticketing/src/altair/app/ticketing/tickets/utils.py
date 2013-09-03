# encoding: utf-8

from lxml import etree
from collections import namedtuple

from ..users.models import SexEnum

from .constants import SVG_NAMESPACE, TS_SVG_EXT_NAMESPACE
from datetime import datetime
import re
import numpy
from ..formatter import Japanese_Japan_Formatter

I = numpy.matrix('1 0 0; 0 1 0; 0 0 1', dtype=numpy.float64)

def datetime_as_dict(dt):
    return {
        u'year': dt.year, u'month': dt.month, u'day': dt.day,
        u'hour': dt.hour, u'minute': dt.minute, u'second': dt.second,
        u'weekday': dt.weekday()
        } if dt is not None else None

def safe_format(formatter, target, default=u""):
    if target is None:
        return default
    return formatter(target)

class TicketCoverDictBuilder(object):
    def __init__(self, formatter):
        self.formatter = formatter
        self.ticket_dict_builder = TicketDictBuilder(formatter)
    
    def build_dict_from_order_total_information(self, order, retval=None):
        retval = retval or {}
        flowline = etree.tostring(etree.Element("{{{}}}flowLine".format(SVG_NAMESPACE)))
        retval.update({
                u'合計金額': u"{total_amount} 円".format(total_amount=int(order.total_amount)), 
                u"合計枚数": sum(op.quantity for op in order.ordered_products),
                u"座席詳細": "",  #<tbreak/>
                u"商品詳細": flowline.join(u"  {op.product.name} x{op.quantity}".format(op=op) for op in order.ordered_products),
                })
        return retval

    def build_dict_from_shipping_address_information(self, shipping_address, retval=None):
        retval = retval or {}
        if shipping_address:
            retval.update({
                    u'住所': u"{shipping.zip} {shipping.prefecture}{shipping.city}{shipping.address_1}{shipping.address_2}".format(shipping=shipping_address), 
                    u"氏名": u"{shipping.last_name} {shipping.first_name}".format(shipping=shipping_address), 
                    u"電話番号": shipping_address.tel_1, 
                    u"メールアドレス": shipping_address.email_1 or shipping_address.email_2
                    })
        else:
            retval.update({
                    u'住所': u"-", 
                    u"氏名": u"-", 
                    u"電話番号": u"-", 
                    u"メールアドレス": u"-"
                    })
        return retval

    def build_dict_from_order(self, order):
        extra = self.ticket_dict_builder.build_basic_dict_from_order(order)
        extra = self.ticket_dict_builder.build_dict_from_performance(order.performance, retval=extra)
        extra = self.build_dict_from_order_total_information(order, retval=extra)
        extra = self.build_dict_from_shipping_address_information(order.shipping_address, retval=extra)
        return extra

class TicketDictBuilder(object):
    def __init__(self, formatter, empty_text=u""):
        self.formatter = formatter
        self.empty_text = empty_text

    def build_user_profile_dict(self, data, user_profile):
        if user_profile is None:
            data['userProfile'] = {}
            return data
        data["userProfile"] = {
            u"email_1": user_profile.email_1,
            u"email_2": user_profile.email_2,
            u"email": user_profile.email,
            u"nick_name": user_profile.nick_name,
            u"first_name": user_profile.first_name,
            u"last_name": user_profile.last_name,
            u"first_name_kana": user_profile.first_name_kana,
            u"last_name_kana": user_profile.last_name_kana,
            u"birth_day": datetime_as_dict(user_profile.birth_day),
            u"sex": self.formatter.sex_as_string(user_profile.sex),
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
        return data

    def build_shipping_address_dict(self, data, shipping_address):
        if shipping_address is None:
            data['shippingAddress'] = {}
            return data
        data[u'shippingAddress'] = {
            u"email_1": shipping_address.email_1,
            u"email_2": shipping_address.email_2,
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
            }
        return data

    def build_dict_from_stock(self, stock, retval=None):
        retval = {} if retval is None else retval
        if stock is None:
            retval["stock"] = {}
            return retval
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

    def build_dict_from_organization(self, organization, retval=None):
        retval = {} if retval is None else retval
        if organization is None:
            retval.update(organization={})
            return retval
        retval.update({
            u'organization': {
                u'name': organization.name,
                u'code': organization.code
                },
            })
        return retval

    def build_dict_from_event(self, event, retval=None):
        retval = {} if retval is None else retval
        if event is None:
            retval["event"] = {}
            retval["organization"] = {}
            return retval
        organization = event.organization
        retval = self.build_dict_from_organization(organization, retval=retval)
        retval.update({
            u'event': {
                u'code': event.code,
                u'title': event.title,
                u'abbreviated_title': event.abbreviated_title,
                },
            u'イベント名': event.title,
            u'イベント名略称': event.abbreviated_title,
            })
        return retval

    def build_dict_from_performance(self, performance, retval=None):
        retval = retval or {}
        if performance is None:
            retval.update(performance={})
            return retval
        event = performance.event
        retval = self.build_dict_from_event(event, retval=retval)
        setting = performance.settings[0] if performance.settings else None
        retval.update({
            u'performance': {
                u'name': performance.name,
                u'code': performance.code,
                u'open_on': datetime_as_dict(performance.open_on),
                u'start_on': datetime_as_dict(performance.start_on),
                u'end_on': datetime_as_dict(performance.end_on)
                },
            u'パフォーマンス名': performance.name,
            u'対戦名': performance.name,
            u'公演コード': performance.code,
            u'開催日': safe_format(self.formatter.format_date, performance.start_on), 
            u'開催日s': safe_format(self.formatter.format_date_short, performance.start_on),
            u'開場時刻': safe_format(self.formatter.format_time, performance.open_on), 
            u'開場時刻s': safe_format(self.formatter.format_time_short, performance.open_on),
            u'開始時刻': safe_format(self.formatter.format_time, performance.start_on), 
            u'開始時刻s': safe_format(self.formatter.format_time_short, performance.start_on),
            u'終了時刻': safe_format(self.formatter.format_time, performance.end_on), 
            u'終了時刻s': safe_format(self.formatter.format_time_short, performance.end_on),
            })
        return self.build_dict_from_performance_setting(setting, retval=retval)
        
    def build_dict_from_performance_setting(self, setting, retval=None):
        retval = {} if retval is None else retval
        if setting is None:
            return retval

        retval.update({ 
                u"公演名略称": setting.abbreviated_title if setting else u"", 
                u"公演名副題": setting.subtitle if setting else u"", 
                u"公演名備考": setting.note if setting else u"", 
                })
        return retval

    def build_dict_from_venue(self, venue, retval=None):
        retval = {} if retval is None else retval
        if venue is None:
            retval["venue"] = {}
            return retval
        performance = venue.performance
        retval = self.build_dict_from_performance(performance, retval=retval)
        retval.update({
            u'venue': {
                u'name': venue.name,
                u'sub_name': venue.sub_name
                },
            u'会場名': venue.name,
            })
        return retval
        
    def build_dict_from_seat(self, seat, retval=None, ticket_number_issuer=None):
        retval = {} if retval is None else retval
        if seat is None:
            retval["seat"] = {}
            retval[u"席番"] = self.empty_text
            return retval
        retval = self.build_dict_from_stock(seat.stock, retval=retval)
        retval = self.build_dict_from_venue(seat.venue, retval=retval)
        retval.update({
            u'seat': {
                u'l0_id': seat.l0_id,
                u'seat_no': seat.seat_no,
                u'name': seat.name,
                },
            u'seatAttributes': dict(seat.attributes),
            u'席番': seat.name,
            })
        return retval

    def build_dict_from_product(self, product, retval=None):
        retval = retval or {}
        if product is None:
            retval["product"] = {}
            return retval
        sales_segment = product.sales_segment

        retval.update({
            u'product': {
                u'name': product.name,
                u'price': product.price
                },
            u'券種名': product.name,
            u'商品名': product.name,
            u'商品価格': self.formatter.format_currency(product.price),
            u'チケット価格': self.formatter.format_currency(product.price),
            })
        retval = self.build_dict_from_sales_segment(sales_segment, retval=retval)
        return retval

    def build_dict_from_sales_segment(self, sales_segment, retval=None):
        retval = retval or {}
        if sales_segment is None:
            retval["salesSegment"] = {}
            return retval
        retval.update({u'salesSegment': {
                    u'name': sales_segment.name,
                    u'kind': sales_segment.kind,
                    u'start_at': datetime_as_dict(sales_segment.start_at),
                    u'end_at': datetime_as_dict(sales_segment.end_at),
                    u'upper_limit': sales_segment.upper_limit,
                    u'seat_choice': sales_segment.seat_choice
                    }})
        return retval


    def build_dict_from_product_item(self, product_item, retval=None):
        retval = retval or {}
        if product_item is None:
            retval["productItem"] = {}
            return retval
        product = product_item.product
        retval = self.build_dict_from_product(product_item.product, retval=retval)
        retval = self.build_dict_from_ticket_bundle(product_item.ticket_bundle, retval=retval)
        retval = self.build_dict_from_stock(product_item.stock, retval=retval)
        retval = self.build_dict_from_venue(product_item.performance.venue, retval=retval)

        retval.update({
            u'productItem': {
                u'name': product_item.name,
                u'price': product_item.price,
                u'quantity': product_item.quantity
                },
            u'券種名': product_item.name or product.name,
            u'商品名': product_item.name or product.name,
            u'商品価格': self.formatter.format_currency(product.price),
            u'チケット価格': self.formatter.format_currency(product_item.price),
            })
        # ## 不足分
        # retval.update({
        #     u"席番": u"{{席番}}", 
        #     u'注文番号': u"{{注文番号}}",
        #     u'注文日時': u"{{注文日時}}",
        #     u'注文日時s': u"{{注文日時s}}",
        #     u'受付番号': u"{{注文番号}}",
        #     u'受付日時': u"{{受付日時}}",
        #     u'受付日時s': u"{{受付日時s}}",
        #     u'予約番号': u"{{予約番号}}", 
        #     u'発券番号': u"{{発券番号}}", 
        #     u"公演コード": u"xxx"
        # })
        return retval

    def build_dict_from_ticket_bundle(self, ticket_bundle, retval=None):
        if ticket_bundle is None:
            retval[u"aux"] = {}
            return retval
        retval.update({
                u'aux': dict(ticket_bundle.attributes), 
                })
        return retval


    def build_basic_dict_from_order(self, order, retval=None):
        if order is None:
            retval[u"order"] = {}
            return retval
        return {
            u'order': {
                u'total_amount': order.total_amount,
                u'system_fee': order.system_fee,
                u'transaction_fee': order.transaction_fee,
                u'delivery_fee': order.delivery_fee,
                u'multicheckout_approval_no': order.multicheckout_approval_no,
                u'order_no': order.order_no,
                u'paid_at': datetime_as_dict(order.paid_at),
                u'delivered_at': datetime_as_dict(order.delivered_at),
                u'canceled_at': datetime_as_dict(order.canceled_at),
                u'cancelled_at': datetime_as_dict(order.canceled_at), #typo
                },
            u'注文番号': order.order_no,
            u'注文日時': safe_format(self.formatter.format_datetime,  order.created_at),
            u'注文日時s': safe_format(self.formatter.format_datetime_short, order.created_at),
            u'受付番号': order.order_no,
            u'受付日時': safe_format(self.formatter.format_datetime,  order.created_at),
            u'受付日時s': safe_format(self.formatter.format_datetime_short, order.created_at),
            u'発券日時': safe_format(self.formatter.format_datetime,  order.issued_at),
            u'発券日時s': safe_format(self.formatter.format_datetime_short, order.issued_at),
            u'予約番号': order.order_no,
        }

    def build_dict_from_order(self, order, user_profile=None, retval=None):
        retval = self.build_basic_dict_from_order(order, retval=retval)
        if order is None:
            return retval
        shipping_address = order.shipping_address
        payment_delivery_method_pair = order.payment_delivery_pair # XXX
        self.build_user_profile_dict(retval, user_profile)
        self.build_shipping_address_dict(retval, shipping_address) #xxx:
        retval = self.build_dict_from_payment_delivery_method_pair(payment_delivery_method_pair, retval=retval)
        return retval

    def build_dict_from_payment_delivery_method_pair(self, payment_delivery_method_pair, retval=None):
        retval = retval or {}
        if payment_delivery_method_pair is None:
            return retval
        payment_method = payment_delivery_method_pair.payment_method
        delivery_method = payment_delivery_method_pair.delivery_method
        retval = self.build_dict_from_payment_method(payment_method, retval=retval)
        retval = self.build_dict_from_delivery_method(delivery_method, retval=retval)
        return retval

    def build_dict_from_payment_method(self, payment_method, retval=None):
        retval = retval or {}
        if payment_method is None:
            retval[u"paymentMethod"] = {}
            return retval
        retval.update({
                u'paymentMethod': {
                    u'name': payment_method.name,
                    u'fee': payment_method.fee,
                    u'fee_type': payment_method.fee_type, 
                    u'plugin_id': payment_method.payment_plugin_id
                    },
                })
        return retval

    def build_dict_from_delivery_method(self, delivery_method, retval=None):
        retval = retval or {}
        if delivery_method is None:
            retval[u"deliveryMethod"] = {}
            return retval
        retval.update({
                u'deliveryMethod': {
                    u'name': delivery_method.name,
                    u'fee': delivery_method.fee,
                    u'fee_type': delivery_method.fee_type, 
                    u'plugin_id': delivery_method.delivery_plugin_id
                    },
                })
        return retval

    def build_basic_dict_from_ordered_product_item(self, ordered_product_item, user_profile=None, retval=None):
        extra = retval or {}
        if ordered_product_item is None:
            extra["orderedProductItem"] = {}
            return extra

        product_item = ordered_product_item.product_item
        ordered_product = ordered_product_item.ordered_product 
        order = ordered_product.order
        
        extra = self.build_dict_from_order(order, user_profile=user_profile, retval=extra)
        extra = self.build_dict_from_product_item(product_item, retval=extra)

        extra.update({
            u'orderedProductItem': {
                u'price': ordered_product_item.price
                },
            u'orderedProductItemAttributes': dict(ordered_product_item.attributes),
            u'orderedProduct': {
                u'price': ordered_product.price,
                u'quantity': ordered_product.quantity
                },
            u'商品価格': self.formatter.format_currency(ordered_product.price),
            u'チケット価格': self.formatter.format_currency(ordered_product_item.price),
            })
        return extra
        
    def build_dicts_from_ordered_product_item(self, ordered_product_item, user_profile=None, ticket_number_issuer=None):
        extra = self.build_basic_dict_from_ordered_product_item(ordered_product_item, user_profile)
        retval = []
        if ordered_product_item.product_item.stock.stock_type.quantity_only:
            for i in range(0, ordered_product_item.quantity):
                d = {}
                d = self.build_dict_from_stock(ordered_product_item.product_item.stock, d)
                d = self.build_dict_from_venue(ordered_product_item.product_item.performance.venue, d)
                d[u'発券番号'] = ticket_number_issuer(ordered_product_item.product_item.id) if ticket_number_issuer else None
                d.update(extra)
                retval.append((None, d))
        else:
            for seat in ordered_product_item.seats:
                d = self.build_dict_from_seat(seat, ticket_number_issuer)
                d[u'発券番号'] = ticket_number_issuer(ordered_product_item.product_item.id) if ticket_number_issuer else None
                d.update(extra)
                retval.append((seat, d))
        return retval

    ## 使われていない可能性が高い
    def build_dicts_from_ordered_product_item_tokens(self, ordered_product_item, user_profile=None, ticket_number_issuer=None):
        extra = self.build_basic_dict_from_ordered_product_item(ordered_product_item, user_profile)
        retval = []
        for token in ordered_product_item.tokens:
            pair = self._build_dict_from_ordered_product_item_token(extra, ordered_product_item, token, ticket_number_issuer)
            if pair is not None:
                retval.append(pair)
        return retval

    def _build_dict_from_ordered_product_item_token(self, extra, ordered_product_item, ordered_product_item_token, ticket_number_issuer=None):
        if not ordered_product_item_token.valid:
            return None
        if ordered_product_item_token.seat is not None:
            d = self.build_dict_from_seat(ordered_product_item_token.seat, ticket_number_issuer)
            d[u'serial'] = ordered_product_item_token.serial
            d[u'発券番号'] = ticket_number_issuer(ordered_product_item.product_item.id) if ticket_number_issuer else None
            d.update(extra)
            return (ordered_product_item_token.seat, d) 
        else:
            d = {}
            d = self.build_dict_from_stock(ordered_product_item.product_item.stock, d)
            d = self.build_dict_from_venue(ordered_product_item.product_item.performance.venue, d)
            d[u'発券番号'] = ticket_number_issuer(ordered_product_item.product_item.id) if ticket_number_issuer else None
            d[u'serial'] = ordered_product_item_token.serial
            d.update(extra)
            return (None, d)

    def build_dict_from_ordered_product_item_token(self, ordered_product_item_token, user_profile=None, ticket_number_issuer=None):
        ordered_product_item = ordered_product_item_token.item
        extra = self.build_basic_dict_from_ordered_product_item(ordered_product_item, user_profile)
        return self._build_dict_from_ordered_product_item_token(extra, ordered_product_item, ordered_product_item_token, ticket_number_issuer)

    def build_dict_from_cart(self, cart, retval=None, now=None):
        retval = retval or {}
        if cart is None:
            retval[u"order"] = {}
            return retval
        shipping_address = cart.shipping_address
        self.build_shipping_address_dict(retval, shipping_address)
        retval.update({
            u'order': {
                u'total_amount': cart.total_amount,
                u'system_fee': cart.system_fee,
                u'transaction_fee': cart.transaction_fee,
                u'delivery_fee': cart.delivery_fee,
                u'order_no': cart.order_no
                },
            u'注文番号': cart.order_no,
            u'注文日時': safe_format(self.formatter.format_datetime, now),
            u'注文日時s': safe_format(self.formatter.format_datetime_short, now),
            u'受付番号': cart.order_no,
            u'受付日時': safe_format(self.formatter.format_datetime, now),
            u'受付日時s': safe_format(self.formatter.format_datetime_short, now),
            u'予約番号': cart.order_no,
            u'発券日時': u'\ufeff{{発券日時}}\ufeff',
            u'発券日時s': u'\ufeff{{発券日時s}}\ufeff',
            })
        return retval
        

    def build_basic_dict_from_carted_product_item(self, carted_product_item, payment_delivery_method_pair=None, user_profile=None, ordered_product_item_attributes=None, now=None):
        product_item = carted_product_item.product_item
        carted_product = carted_product_item.carted_product
        product = carted_product.product
        now = now or datetime.now()

        retval = {}
        self.build_user_profile_dict(retval, user_profile)
        retval = self.build_dict_from_product_item(carted_product_item.product_item, retval=retval)
        retval = self.build_dict_from_payment_delivery_method_pair(payment_delivery_method_pair, retval=retval)
        retval = self.build_dict_from_cart(carted_product.cart, retval=retval, now=now)
        retval.update({
                u'orderedProductItem': {
                    u'price': product_item.price
                    },
                u'orderedProductItemAttributes': ordered_product_item_attributes or {},
                u'orderedProduct': {
                    u'price': product.price,
                    u'quantity': carted_product.quantity
                    },
                })
        return retval

    def build_dicts_from_carted_product_item(self, carted_product_item, payment_delivery_method_pair=None, ordered_product_item_attributes=None, user_profile=None, ticket_number_issuer=None, now=None):
        extra = self.build_basic_dict_from_carted_product_item(carted_product_item, 
                                                               payment_delivery_method_pair=payment_delivery_method_pair, 
                                                               ordered_product_item_attributes=ordered_product_item_attributes, 
                                                               user_profile=user_profile, 
                                                               now=now
                                                               )
        retval = []
        if carted_product_item.product_item.stock.stock_type.quantity_only:
            for i in range(0, carted_product_item.quantity):
                d = {}
                self.build_dict_from_stock(carted_product_item.product_item.stock, d)
                d[u'発券番号'] = ticket_number_issuer(carted_product_item.product_item.id) if ticket_number_issuer else ""
                d.update(extra)
                retval.append((None, d))
        else:
            for seat in carted_product_item.seats:
                d = self.build_dict_from_seat(seat, ticket_number_issuer)
                d[u'発券番号'] = ""
                d.update(extra)
                retval.append((seat, d))
        return retval

#b/c
DictBuilder = TicketDictBuilder

_default_builder = DictBuilder(Japanese_Japan_Formatter())
build_dict_from_stock = _default_builder.build_dict_from_stock
build_dict_from_venue = _default_builder.build_dict_from_venue
build_dict_from_seat = _default_builder.build_dict_from_seat
build_dict_from_organization = _default_builder.build_dict_from_organization
build_dict_from_event = _default_builder.build_dict_from_event
build_dict_from_performance = _default_builder.build_dict_from_performance
build_dict_from_product = _default_builder.build_dict_from_product
build_dict_from_product_item = _default_builder.build_dict_from_product_item
build_dicts_from_ordered_product_item = _default_builder.build_dicts_from_ordered_product_item
build_dicts_from_carted_product_item = _default_builder.build_dicts_from_carted_product_item
build_dict_from_ordered_product_item_token = _default_builder.build_dict_from_ordered_product_item_token

_default_cover_builder = TicketCoverDictBuilder(Japanese_Japan_Formatter())
build_cover_dict_from_order = _default_cover_builder.build_dict_from_order

Size = namedtuple('Size', 'width height')
Position = namedtuple('Position', 'x y')
Rectangle = namedtuple('Rectangle', 'x y width height')
Margin = namedtuple('Margin', 'top bottom left right')

class SvgPageSetBuilder(object):
    def __init__(self, page_format, ticket_format):
        orientation = page_format[u'orientation'].lower()
        
        printable_area = Rectangle(
            x=as_user_unit(page_format[u'printable_area'][u'x']),
            y=as_user_unit(page_format[u'printable_area'][u'y']),
            width=as_user_unit(page_format[u'printable_area'][u'width']),
            height=as_user_unit(page_format[u'printable_area'][u'height'])
            )

        if orientation == u'landscape':
            printable_area = Rectangle(
                printable_area.y, printable_area.x,
                printable_area.height, printable_area.width
                )

        ticket_size = Size(
            width=as_user_unit(ticket_format[u'size'][u'width']),
            height=as_user_unit(ticket_format[u'size'][u'height'])
            )

        ticket_margin = Margin(
            top=as_user_unit(page_format[u'ticket_margin'][u'top']),
            bottom=as_user_unit(page_format[u'ticket_margin'][u'bottom']),
            left=as_user_unit(page_format[u'ticket_margin'][u'left']),
            right=as_user_unit(page_format[u'ticket_margin'][u'right'])
            )

        if printable_area.width < ticket_size.width + ticket_margin.left or \
            printable_area.height < ticket_size.height + ticket_margin.top:
            raise ValueError('printable area too small')

        self.page_format = page_format
        self.ticket_format = ticket_format
        self.orientation = orientation
        self.ticket_size = ticket_size
        self.printable_area = printable_area
        self.ticket_margin = ticket_margin
        self.root = self.build_root_element()
        self.pageset = etree.Element(u'{%s}pageSet' % SVG_NAMESPACE)
        self.root.append(self.pageset)
        self.page = None
        self.offset = Position(printable_area.x, printable_area.y)

    @property
    def tickets_per_page(self):
        return (self.printable_area.width + self.ticket_margin.right) // \
            (self.ticket_size.width +
             self.ticket_margin.left +
             self.ticket_margin.right) * \
            (self.printable_area.height + self.ticket_margin.bottom) // \
                (self.ticket_size.height +
                 self.ticket_margin.top +
                 self.ticket_margin.bottom)

    def build_root_element(self):
        width = unicode(as_user_unit(self.page_format[u'size'][u'width']))
        height = unicode(as_user_unit(self.page_format[u'size'][u'height']))

        # Swap width / height if the orientation is 'landscape'
        if self.orientation == u'landscape':
            width, height = height, width
        return etree.Element(
            u'{%s}svg' % SVG_NAMESPACE,
            nsmap={ u'svg': SVG_NAMESPACE, u'ts' : TS_SVG_EXT_NAMESPACE },
            version=u'1.2',
            width=width,
            height=height
            )

    def add(self, svg, queue_id, title=None):
        if self.offset.x + self.ticket_margin.left + self.ticket_size.width > self.printable_area.x + self.printable_area.width:
            self.offset = Position(self.printable_area.x, self.offset.y + self.ticket_size.height + self.ticket_margin.top + self.ticket_margin.bottom)
        if self.offset.y + self.ticket_margin.top + self.ticket_size.height > self.printable_area.y + self.printable_area.height:
            self.offset = Position(self.printable_area.x, self.printable_area.y)
            self.page = None
        if self.page is None:
            self.page = etree.Element(u'{%s}page' % SVG_NAMESPACE)
            if title is not None:
                title_elem = etree.Element(u'{%s}title' % SVG_NAMESPACE)
                title_elem.text = title
                self.page.append(title_elem)
            self.pageset.append(self.page)
        svgroot = svg.getroot() if isinstance(svg, etree._ElementTree) else svg
        svgroot.set(u'x', unicode(self.offset.x + self.ticket_margin.left))
        svgroot.set(u'y', unicode(self.offset.y + self.ticket_margin.top))
        svgroot.set(u'{%s}queue-id' % TS_SVG_EXT_NAMESPACE, unicode(queue_id))
        self.page.append(svgroot)
        self.offset = Position(self.offset.x + self.ticket_size.width + self.ticket_margin.left + self.ticket_margin.right, self.offset.y)

class FallbackSvgPageSetBuilder(object):
    def __init__(self, page_format, ticket_format):
        orientation = page_format[u'orientation'].lower()
        
        printable_area = Rectangle(
            x=as_user_unit(page_format[u'printable_area'][u'x']),
            y=as_user_unit(page_format[u'printable_area'][u'y']),
            width=as_user_unit(page_format[u'printable_area'][u'width']),
            height=as_user_unit(page_format[u'printable_area'][u'height'])
            )

        if orientation == u'landscape':
            printable_area = Rectangle(
                printable_area.y, printable_area.x,
                printable_area.height, printable_area.width
                )

        ticket_size = Size(
            width=as_user_unit(ticket_format[u'size'][u'width']),
            height=as_user_unit(ticket_format[u'size'][u'height'])
            )

        ticket_margin = Margin(
            top=as_user_unit(page_format[u'ticket_margin'][u'top']),
            bottom=as_user_unit(page_format[u'ticket_margin'][u'bottom']),
            left=as_user_unit(page_format[u'ticket_margin'][u'left']),
            right=as_user_unit(page_format[u'ticket_margin'][u'right'])
            )

        self.page_format = page_format
        self.ticket_format = ticket_format
        self.orientation = orientation
        self.ticket_size = ticket_size
        self.printable_area = printable_area
        self.ticket_margin = ticket_margin
        self.root = self.build_root_element()
        self.pageset = etree.Element(u'{%s}pageSet' % SVG_NAMESPACE)
        self.root.append(self.pageset)
        self.offset = Position(printable_area.x, printable_area.y)

    @property
    def tickets_per_page(self):
        return 1

    def build_root_element(self):
        width = unicode(as_user_unit(self.page_format[u'size'][u'width']))
        height = unicode(as_user_unit(self.page_format[u'size'][u'height']))

        # Swap width / height if the orientation is 'landscape'
        if self.orientation == u'landscape':
            width, height = height, width
        return etree.Element(
            u'{%s}svg' % SVG_NAMESPACE,
            nsmap={ u'svg': SVG_NAMESPACE, u'ts' : TS_SVG_EXT_NAMESPACE },
            version=u'1.2',
            width=width,
            height=height
            )

    def add(self, svg, queue_id, title=None):
        page = etree.Element(u'{%s}page' % SVG_NAMESPACE)
        if title is not None:
            title_elem = etree.Element(u'{%s}title' % SVG_NAMESPACE)
            title_elem.text = title
            page.append(title_elem)
        self.pageset.append(page)
        svgroot = svg.getroot() if isinstance(svg, etree._ElementTree) else svg
        svgroot.set(u'x', unicode(self.offset.x + self.ticket_margin.left))
        svgroot.set(u'y', unicode(self.offset.y + self.ticket_margin.top))
        svgroot.set(u'{%s}queue-id' % TS_SVG_EXT_NAMESPACE, unicode(queue_id))
        page.append(svgroot)
        self.offset = Position(self.offset.x + self.ticket_size.width + self.ticket_margin.left + self.ticket_margin.right, self.offset.y)


def as_user_unit(size, rel_unit=None):
    if size is None:
        return None
    spec = re.match('(-?[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(pt|pc|mm|cm|in|px|em|%)?', size.strip().lower())
    if spec is None:
        raise Exception('Invalid length / size specifier: ' + size)
    degree = float(spec.group(1))
    unit = spec.group(2) or 'px'
    if unit == 'pt':
        return degree * 1.25
    elif unit == 'pc':
        return degree * 15
    elif unit == 'mm':
        return degree * 90 / 25.4
    elif unit == 'cm':
        return degree * 90 / 2.54
    elif unit == 'in':
        return degree * 90.
    elif unit == 'px':
        return degree
    elif unit == 'em':
        if rel_unit is None:
            raise Exception('Relative size specified where no unit size is given in the applied context')
        return rel_unit * degree
    elif unit == '%':
        if rel_unit is None:
            raise Exception('Relative size specified where no unit size is given in the applied context')
        return rel_unit * degree / 100.

def translate(x, y):
    return numpy.matrix(
        [
            [1., 0., float(x)],
            [0., 1., float(y)],
            [0., 0., 1.]
            ],
        dtype=numpy.float64)

def parse_transform(transform_str):
    for g in re.finditer(ur'\s*([A-Za-z_-][0-9A-Za-z_-]*)\s*\(\s*((?:[^\s,]+(?:\s*,\s*|\s+))*[^\s,]+)\s*\)\s*', transform_str):
        f = g.group(1)
        args = re.split(ur'\s*,\s*|\s+',g.group(2).strip())
        if f == u'matrix':
            if len(args) != 6:
                raise Exception('invalid number of arguments for matrix()')
            return numpy.matrix(
                [
                    [float(args[0]), float(args[2]), float(args[4])],
                    [float(args[1]), float(args[3]), float(args[5])],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)
        elif f == u'translate':
            if len(args) != 2:
                raise Exception('invalid number of arguments for translate()')
            return translate(args[0], args[1])
        elif f == u'scale':
            if len(args) != 2:
                raise Exception('invalid number of arguments for scale()')
            return numpy.matrix(
                [
                    [float(args[0]), 0., 0.],
                    [0., float(args[1]), 0.],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)
        elif f == u'rotate':
            if len(args) != 1:
                raise Exception('invalid number of arguments for rotate()')
            t = float(args[0]) * numpy.pi / 180.
            c = numpy.sin(t)
            s = numpy.sin(t)
            return numpy.matrix(
                [
                    [c, -s, 0.],
                    [s, c, 0.],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)
        elif f == u'skeyX':
            if len(args) != 1:
                raise Exception('invalid number of arguments for skewX()')
            t = float(args[0]) * numpy.pi / 180.
            ta = numpy.tan(t)
            return numpy.matrix(
                [
                    [1., ta, 0.],
                    [0., 1., 0.],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)
        elif f == u'skeyY':
            if len(args) != 1:
                raise Exception('invalid number of arguments for skewY()')
            t = float(args[0]) * numpy.pi / 180.
            ta = numpy.tan(t)
            return numpy.matrix(
                [
                    [1., 0., 0.],
                    [ta, 1., 0.],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)

class PathDataScanner(object):
    def __init__(self, iter, handler):
        self.iter = iter
        self.handler = handler
        self.current_position = (0, 0)
        self.last_qb_control_point = None
        self.last_cb_control_point = None
        self.next_op = None

    def scan_z(self, operand):
        if len(operand) > 0:
            raise Exception('closepath does not take any arguments')
        self.handler.close_path()
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    scan_Z = scan_z

    def scan_h(self, operand):
        if len(operand) == 0:
            raise Exception('horizontalline takes at least 1 argument')
        for oper in operand:
            x = self.current_position[0] + float(oper)
            self.handler.line_to(x, self.current_position[1])
            self.current_position = (x, self.current_position[1])
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_H(self, operand):
        if operand == 0:
            raise Exception('horizontalline takes at least 1 argument')
        for oper in operand:
            x = float(oper)
            self.handler.line_to(x, self.current_position[1])
            self.current_position = (x, self.current_position[1])
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_v(self, operand):
        if len(operand) == 0:
            raise Exception('verticalline takes at least 1 argument')
        for oper in operand:
            y = self.current_position[1] + float(oper)
            self.handler.line_to(self.current_position[0], y)
            self.current_position = (self.current_position[0], y)
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_V(self, operand):
        if len(operand) == 0:
            raise Exception('verticalline takes at least 1 argument')
        for oper in operand:
            y = float(oper)
            self.handler.line_to(self.current_position[0], y)
            self.current_position = (self.current_position[0], y)
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_m(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('moveto takes 2 * n arguments')
        i = iter(operand)
        try:
            x = self.current_position[0] + float(i.next())
            y = self.current_position[1] + float(i.next())
            self.handler.move_to(x, y)
            self.current_position = (x, y)
            while True:
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.line_to(x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_M(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('moveto takes 2 * n arguments')
        i = iter(operand)
        try:
            x = float(i.next())
            y = float(i.next())
            self.handler.move_to(x, y)
            self.current_position = (x, y)
            while True:
                x = float(i.next())
                y = float(i.next())
                self.handler.line_to(x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_l(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('lineto takes 2 * n arguments')
        i = iter(operand)
        try:
            while True:
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.line_to(x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_L(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('lineto takes 2 * n arguments')
        i = iter(operand)
        try:
            while True:
                x = float(i.next())
                y = float(i.next())
                self.handler.line_to(x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_t(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('curvetosmooth takes 2 * n arguments')
        i = iter(operand)
        try:
            while True:
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                if self.last_qb_control_point is None:
                    x1 = self.current_position[0]
                    y1 = self.current_position[1]
                else:
                    x1 = self.current_position[0] + (self.current_position[0] - self.last_qb_control_point[0])
                    y1 = self.current_position[1] + (self.current_position[1] - self.last_qb_control_point[1])
                self.handler.curve_to_qb(x1, y1, x, y)
                self.current_position = (x, y)
                self.last_qb_control_point = (x1, y1)
        except StopIteration:
            pass
        self.last_cb_control_point = None

    def scan_T(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('curvetosmooth takes 2 * n arguments')
        i = iter(operand)
        try:
            while True:
                x = float(i.next())
                y = float(i.next())
                if self.last_qb_control_point is None:
                    x1 = self.current_position[0]
                    y1 = self.current_position[1]
                else:
                    x1 = self.current_position[0] + (self.current_position[0] - self.last_qb_control_point[0])
                    y1 = self.current_position[1] + (self.current_position[1] - self.last_qb_control_point[1])
                self.handler.curve_to_qb(x1, y1, x, y)
                self.current_position = (x, y)
                self.last_qb_control_point = (x1, y1)
        except StopIteration:
            pass
        self.last_cb_control_point = None

    def scan_s(self, operand):
        if operand == 0 or len(operand) % 4 != 0:
            raise Exception('curvetosmooth takes 4 * n arguments')
        i = iter(operand)
        try:
            while True:
                if self.last_cb_control_point is None:
                    x1 = self.current_position[0]
                    y1 = self.current_position[1]
                else:
                    x1 = self.current_position[0] + (self.current_position[0] - self.last_cb_control_point[0])
                    y1 = self.current_position[1] + (self.current_position[1] - self.last_cb_control_point[1])
                x2 = self.current_position[0] + float(i.next())
                y2 = self.current_position[1] + float(i.next())
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.curve_to(x1, y1, x2, y2, x, y)
                self.current_position = (x, y)
                self.last_cb_control_point = (x2, y2)
        except StopIteration:
            pass
        self.last_qb_control_point = None

    def scan_S(self, operand):
        if operand == 0 or len(operand) % 4 != 0:
            raise Exception('curvetosmooth takes 4 * n arguments')
        i = iter(operand)
        try:
            while True:
                if self.last_cb_control_point is None:
                    x1 = self.current_position[0]
                    y1 = self.current_position[1]
                else:
                    x1 = self.current_position[0] + (self.current_position[0] - self.last_cb_control_point[0])
                    y1 = self.current_position[1] + (self.current_position[1] - self.last_cb_control_point[1])
                x2 = float(i.next())
                y2 = float(i.next())
                x = float(i.next())
                y = float(i.next())
                self.handler.curve_to(x1, y1, x2, y2, x, y)
                self.current_position = (x, y)
                self.last_cb_control_point = (x2, y2)
        except StopIteration:
            pass
        self.last_qb_control_point = None

    def scan_q(self, operand):
        if operand == 0 or len(operand) % 4 != 0:
            raise Exception('curvetoqb takes 4 * n arguments')
        i = iter(operand)
        try:
            while True:
                x1 = self.current_position[0] + float(i.next())
                y1 = self.current_position[1] + float(i.next())
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.last_qb_control_point = (x1, y1)
                self.handler.curve_to_qb(x1, y1, x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_cb_control_point = None

    def scan_Q(self, operand):
        if operand == 0 or len(operand) % 4 != 0:
            raise Exception('curvetoqb takes 4 * n arguments')
        i = iter(operand)
        try:
            while True:
                x1 = float(i.next())
                y1 = float(i.next())
                x = float(i.next())
                y = float(i.next())
                self.last_qb_control_point = (x1, y1)
                self.handler.curve_to_qb(x1, y1, x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_cb_control_point = None

    def scan_c(self, operand):
        if operand == 0 or len(operand) % 6 != 0:
            raise Exception('curveto takes 6 * n arguments')
        i = iter(operand)
        try:
            while True:
                x1 = self.current_position[0] + float(i.next())
                y1 = self.current_position[1] + float(i.next())
                x2 = self.current_position[0] + float(i.next())
                y2 = self.current_position[1] + float(i.next())
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.curve_to(x1, y1, x2, y2, x, y)
                self.current_position = (x, y)
                self.last_cb_control_point = (x2, y2)
        except StopIteration:
            pass
        self.last_qb_control_point = None

    def scan_C(self, operand):
        if operand == 0 or len(operand) % 6 != 0:
            raise Exception('curveto takes 6 * n arguments')
        i = iter(operand)
        try:
            while True:
                x1 = float(i.next())
                y1 = float(i.next())
                x2 = float(i.next())
                y2 = float(i.next())
                x = float(i.next())
                y = float(i.next())
                self.handler.curve_to(x1, y1, x2, y2, x, y)
                self.current_position = (x, y)
                self.last_cb_control_point = (x2, y2)
        except StopIteration:
            pass
        self.last_qb_control_point = None

    def scan_a(self, operand):
        if operand == 0 or len(operand) % 7 != 0:
            raise Exception('arc takes 7 * n arguments')
        i = iter(operand)
        try:
            while True:
                rx = float(i.next())
                ry = float(i.next())
                phi = float(i.next())
                largearc = bool(i.next())
                sweep = bool(i.next())
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.arc(rx, ry, phi, largearc, sweep, x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_cb_control_point = None
        self.last_qb_control_point = None

    def scan_A(self, operand):
        if operand == 0 or len(operand) % 7 != 0:
            raise Exception('arc takes 7 * n arguments')
        i = iter(operand)
        try:
            while True:
                rx = float(i.next())
                ry = float(i.next())
                phi = float(i.next())
                largearc = bool(i.next())
                sweep = bool(i.next())
                x = float(i.next())
                y = float(i.next())
                self.handler.arc(rx, ry, phi, largearc, sweep, x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_cb_control_point = None
        self.last_qb_control_point = None

    def __call__(self):
        fn = None
        operand = []
        for op in self.iter:
            next_fn = getattr(self, 'scan_' + op, None)
            if fn is not None:
                if next_fn is not None:
                    fn(operand)
                    fn = next_fn
                    operand = []
                else:
                    operand.append(op)
            else:
                fn = next_fn
        if fn is not None:
            fn(operand)

NUM_REGEX = ur'(-?(?:(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?))'

def tokenize_path_data(path):
    return (g.group(0) for g in re.finditer(NUM_REGEX + ur'|[A-Za-z_]+', path))

def parse_poly_data(poly):
    return ((float(g.group(1)), float(g.group(2))) for g in re.finditer(NUM_REGEX + ur'(?:\s+(?:,\s*)?|,\s*)' + NUM_REGEX, poly))

def transform_matrix_from_ticket_format(ticket_format):
    po = ticket_format.data.get("print_offset")
    if po:
        return translate(-as_user_unit(po.get('x', '0')), -as_user_unit(po.get('y', '0')))
    else:
        return None
