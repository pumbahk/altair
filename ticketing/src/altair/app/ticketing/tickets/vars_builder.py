# -*- coding:utf-8 -*-
from lxml import etree
from altair.svg.constants import SVG_NAMESPACE
from datetime import datetime
from collections import namedtuple

def safe_format(formatter, target, default=u""):
    if target is None:
        return default
    return formatter(target)

def datetime_as_dict(dt):
    return {
        u'year': dt.year, u'month': dt.month, u'day': dt.day,
        u'hour': dt.hour, u'minute': dt.minute, u'second': dt.second,
        u'weekday': dt.weekday()
        } if dt is not None else None

def get_unique_string_for_qr_from_token(token):
    return u"発券時ユニークID: token.id={}".format(token.id)

DummyToken = namedtuple('DummyToken', 'serial seat')

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
                    u'住所': u"{shipping.zip}{shipping.prefecture}{shipping.city}{shipping.address_1}{shipping.address_2}".format(shipping=shipping_address),
                    u"氏名": shipping_address.full_name,
                    u"氏名カナ": shipping_address.full_name_kana,
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
        extra = self.ticket_dict_builder.build_dict_from_order_attributes(order.attributes, retval=extra)
        extra = self.ticket_dict_builder.build_dict_from_payment_delivery_method_pair(order.payment_delivery_method_pair, retval=extra)
        extra = self.build_dict_from_order_total_information(order, retval=extra)
        extra = self.build_dict_from_shipping_address_information(order.shipping_address, retval=extra)
        return extra

class TicketDictListBuilder(object):
    def __init__(self, builder):
        self.builder = builder

    def build_dicts_from_ordered_product_item(self, ordered_product_item, user_profile=None, ticket_number_issuer=None, return_tokens=False):
        if not return_tokens:
            return self._build_dicts_from_ordered_product_item(ordered_product_item, user_profile, ticket_number_issuer)
        else:
            return self._build_dicts_from_ordered_product_item2(ordered_product_item, user_profile, ticket_number_issuer)

    def _build_dicts_from_ordered_product_item(self, ordered_product_item, user_profile=None, ticket_number_issuer=None):
        builder = self.builder
        extra = builder.build_basic_dict_from_ordered_product_item(ordered_product_item, user_profile)
        retval = []
        if ordered_product_item.tokens:
            for token in ordered_product_item.tokens:
                d = builder._build_dict_from_ordered_product_item_token(extra, ordered_product_item, token, ticket_number_issuer=ticket_number_issuer)
                if d is not None:
                    d.update(extra)
                    retval.append((token.seat, d))
        elif ordered_product_item.product_item.stock.stock_type.quantity_only: #BC
            for i in range(0, ordered_product_item.quantity):
                d = extra.copy()
                d = builder.build_dict_from_stock(ordered_product_item.product_item.stock, d)
                d = builder.build_dict_from_venue(ordered_product_item.product_item.performance.venue, d)
                d[u'発券番号'] = ticket_number_issuer(ordered_product_item.product_item.id) if ticket_number_issuer else ""
                retval.append((None, d))
        else: #BC
            for seat in ordered_product_item.seats:
                d = builder.build_dict_from_seat(seat, ticket_number_issuer=ticket_number_issuer)
                d = builder.build_dict_from_stock(ordered_product_item.product_item.stock, d)
                d[u'発券番号'] = ticket_number_issuer(ordered_product_item.product_item.id) if ticket_number_issuer else ""
                d.update(extra)
                retval.append((seat, d))
        return retval

    def _build_dicts_from_ordered_product_item2(self, ordered_product_item, user_profile=None, ticket_number_issuer=None):
        builder = self.builder
        extra = builder.build_basic_dict_from_ordered_product_item(ordered_product_item, user_profile)
        retval = []
        for token in ordered_product_item.tokens:
            d = builder._build_dict_from_ordered_product_item_token(extra, ordered_product_item, token, ticket_number_issuer=ticket_number_issuer)
            if d is not None:
                d.update(extra)
                retval.append((token, d))
        return retval

    def build_dicts_from_carted_product_item(self, carted_product_item, payment_delivery_method_pair=None, ordered_product_item_attributes=None, user_profile=None, ticket_number_issuer=None, now=None, return_tokens=False):
        if not return_tokens:
            return self._build_dicts_from_carted_product_item(carted_product_item, payment_delivery_method_pair, ordered_product_item_attributes, user_profile, ticket_number_issuer, now)
        else:
            return self._build_dicts_from_carted_product_item2(carted_product_item, payment_delivery_method_pair, ordered_product_item_attributes, user_profile, ticket_number_issuer, now)

    def _build_dicts_from_carted_product_item(self, carted_product_item, payment_delivery_method_pair=None, ordered_product_item_attributes=None, user_profile=None, ticket_number_issuer=None, now=None):
        builder = self.builder
        extra = builder.build_basic_dict_from_carted_product_item(carted_product_item,
                                                               payment_delivery_method_pair=payment_delivery_method_pair,
                                                               ordered_product_item_attributes=ordered_product_item_attributes,
                                                               user_profile=user_profile,
                                                               now=now
                                                               )
        retval = []
        if carted_product_item.product_item.stock.stock_type.quantity_only:
            for i in range(0, carted_product_item.quantity):
                d = {}
                builder.build_dict_from_stock(carted_product_item.product_item.stock, d)
                d[u'発券番号'] = ticket_number_issuer(carted_product_item.product_item.id) if ticket_number_issuer else ""
                d.update(extra)
                retval.append((None, d))
        else:
            for seat in carted_product_item.seats:
                d = builder.build_dict_from_seat(seat, ticket_number_issuer=ticket_number_issuer)
                builder.build_dict_from_stock(carted_product_item.product_item.stock, d)
                d[u'発券番号'] = ticket_number_issuer(carted_product_item.product_item.id) if ticket_number_issuer else ""
                d.update(extra)
                retval.append((seat, d))
        return retval

    def _build_dicts_from_carted_product_item2(self, carted_product_item, payment_delivery_method_pair=None, ordered_product_item_attributes=None, user_profile=None, ticket_number_issuer=None, now=None):
        builder = self.builder
        extra = builder.build_basic_dict_from_carted_product_item(carted_product_item,
                                                               payment_delivery_method_pair=payment_delivery_method_pair,
                                                               ordered_product_item_attributes=ordered_product_item_attributes,
                                                               user_profile=user_profile,
                                                               now=now
                                                               )
        retval = []
        if carted_product_item.product_item.stock.stock_type.quantity_only:
            for i in range(0, carted_product_item.quantity):
                d = {}
                builder.build_dict_from_stock(carted_product_item.product_item.stock, d)
                d[u'発券番号'] = ticket_number_issuer(carted_product_item.product_item.id) if ticket_number_issuer else ""
                d.update(extra)
                retval.append((DummyToken(serial=i, seat=None), d))
        else:
            for seat in carted_product_item.seats:
                d = builder.build_dict_from_seat(seat, ticket_number_issuer=ticket_number_issuer)
                builder.build_dict_from_stock(carted_product_item.product_item.stock, d)
                d[u'発券番号'] = ticket_number_issuer(carted_product_item.product_item.id) if ticket_number_issuer else ""
                d.update(extra)
                retval.append((DummyToken(serial=None, seat=seat), d))
        return retval


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
            u"birthday": datetime_as_dict(user_profile.birthday),
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

        data.update({
            u'住所': u"{shipping.zip}{shipping.prefecture}{shipping.city}{shipping.address_1}{shipping.address_2}".format(shipping=shipping_address),
            u"氏名": shipping_address.full_name,
            u"氏名カナ": shipping_address.full_name_kana,
            u"電話番号": shipping_address.tel_1,
            u"メールアドレス": shipping_address.email_1 or shipping_address.email_2
        })

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
        setting = performance.setting
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
            u'開催日c': safe_format(self.formatter.format_date_compressed, performance.start_on),
            u'開催日s': safe_format(self.formatter.format_date_short, performance.start_on),
            u'開場時刻': safe_format(self.formatter.format_time, performance.open_on),
            u'開場時刻c': safe_format(self.formatter.format_time_compressed, performance.open_on),
            u'開場時刻s': safe_format(self.formatter.format_time_short, performance.open_on),
            u'開始時刻': safe_format(self.formatter.format_time, performance.start_on),
            u'開始時刻c': safe_format(self.formatter.format_time_compressed, performance.start_on),
            u'開始時刻s': safe_format(self.formatter.format_time_short, performance.start_on),
            u'終了時刻': safe_format(self.formatter.format_time, performance.end_on),
            u'終了時刻c': safe_format(self.formatter.format_time_compressed, performance.end_on),
            u'終了時刻s': safe_format(self.formatter.format_time_short, performance.end_on),
            u"公演名略称": performance.abbreviated_title if performance.abbreviated_title else u"",
            u"公演名副題": performance.subtitle if performance.subtitle else u"",
            u"公演名副題2": performance.subtitle2 if performance.subtitle2 else u"",
            u"公演名副題3": performance.subtitle3 if performance.subtitle3 else u"",
            u"公演名副題4": performance.subtitle4 if performance.subtitle4 else u"",
            u"公演名備考": performance.note if performance.note else u"",
            })
        return self.build_dict_from_performance_setting(setting, retval=retval)

    def build_dict_from_performance_setting(self, setting, retval=None):
        retval = {} if retval is None else retval
        if setting is None:
            return retval

        retval.update({
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
                    u'max_quantity': sales_segment.max_quantity,
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
                u'id': order.id, #hmm.(using svg_builder.SVGBuilder)
                u'total_amount': order.total_amount,
                u'system_fee': order.system_fee,
                u'special_fee': order.special_fee,
                u'special_fee_name': order.special_fee_name,
                u'transaction_fee': order.transaction_fee,
                u'delivery_fee': order.delivery_fee,
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
        retval = self.build_dict_from_order_attributes(order.attributes, retval=retval)
        retval = self.build_dict_from_payment_delivery_method_pair(payment_delivery_method_pair, retval=retval)
        return retval

    def build_dict_from_order_attributes(self, attributes, retval=None):
        retval = retval or {}
        if not attributes:
            return retval
        if u"memo_on_order1" in attributes:
            retval[u"予約時補助文言1"] = attributes["memo_on_order1"]
        if u"memo_on_order2" in attributes:
            retval[u"予約時補助文言2"] = attributes["memo_on_order2"]
        if u"memo_on_order3" in attributes:
            retval[u"予約時補助文言3"] = attributes["memo_on_order3"]
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

    def _build_dict_from_ordered_product_item_token(self, extra, ordered_product_item, ordered_product_item_token, ticket_number_issuer=None):
        if not ordered_product_item_token.valid:
            return None
        d = {}
        d[u'発券時ユニークID'] = get_unique_string_for_qr_from_token(ordered_product_item_token)
        d[u'serial'] = ordered_product_item_token.serial
        d[u'発券番号'] = ticket_number_issuer(ordered_product_item.product_item.id) if ticket_number_issuer else ""
        d = self.build_dict_from_stock(ordered_product_item.product_item.stock, d)
        if ordered_product_item_token.seat is not None:
            d = self.build_dict_from_seat(ordered_product_item_token.seat, retval=d, ticket_number_issuer=ticket_number_issuer)
        else:
            d = self.build_dict_from_venue(ordered_product_item.product_item.performance.venue, d)
        d.update(extra)
        return d

    def build_dict_from_ordered_product_item_token(self, ordered_product_item_token, user_profile=None, ticket_number_issuer=None):
        ordered_product_item = ordered_product_item_token.item
        extra = self.build_basic_dict_from_ordered_product_item(ordered_product_item, user_profile)
        return self._build_dict_from_ordered_product_item_token(extra, ordered_product_item, ordered_product_item_token, ticket_number_issuer=ticket_number_issuer)

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
                u'special_fee': cart.special_fee,
                u'special_fee_name': cart.special_fee_name,
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
