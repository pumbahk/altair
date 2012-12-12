# encoding: utf-8

from lxml import etree
from collections import namedtuple

from ..users.models import SexEnum
from .convert import as_user_unit
from .constants import SVG_NAMESPACE, TS_SVG_EXT_NAMESPACE
from datetime import datetime

def datetime_as_dict(dt):
    return {
        u'year': dt.year, u'month': dt.month, u'day': dt.day,
        u'hour': dt.hour, u'minute': dt.minute, u'second': dt.second,
        u'weekday': dt.weekday()
        } if dt is not None else None

class Japanese_Japan_Formatter(object):
    SEX_TO_STRING_MAP = {
        SexEnum.NoAnswer.v: u'未回答',
        SexEnum.Male.v: u'男性',
        SexEnum.Female.v: u'女性'
        }
    WEEK_NAMES = [u'月', u'火', u'水', u'木', u'金', u'土', u'日']

    def sex_as_string(self, sex):
        return self.SEX_TO_STRING_MAP[sex] 

    def format_date(self, date):
        return unicode(date.strftime('%Y年 %0m月 %0d日'), 'utf-8') + u' (%s)' % self.WEEK_NAMES[date.weekday()]

    def format_date_short(self, date):
        return unicode(date.strftime('%Y/%0m/%0d'), 'utf-8') + u' (%s)' % self.WEEK_NAMES[date.weekday()]

    def format_time(self, time):
        return unicode(time.strftime('%H時 %M分'), 'utf-8')

    def format_time_short(self, time):
        return unicode(time.strftime('%H:%M'), 'utf-8')

    def format_datetime(self, datetime):
        return self.format_date(datetime) + u' ' + self.format_time(datetime)

    def format_datetime_short(self, datetime):
        return self.format_date_short(datetime) + u' ' + self.format_time_short(datetime)

    def format_currency(self, dec):
        return u'{0:0,.0f}円'.format(dec)

class DictBuilder(object):
    def __init__(self, formatter):
        self.formatter = formatter

    def build_user_profile_dict(self, data, user_profile):
        if user_profile is None:
            data['userProfile'] = {}
            return data
        data["userProfile"] = {
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
        retval.update({
            u'organization': {
                u'name': organization.name,
                u'code': organization.code
                },
            })
        return retval

    def build_dict_from_event(self, event, retval=None):
        retval = {} if retval is None else retval
        organization = event.organization
        retval = self.build_dict_from_organization(organization, retval=retval)
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
            u'イベント名': event.title,
            })
        return retval

    def build_dict_from_performance(self, performance, retval=None):
        retval = retval or {}
        event = performance.event
        retval = self.build_dict_from_event(event, retval=retval)
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
            u'開催日': self.formatter.format_date(performance.start_on),
            u'開催日s': self.formatter.format_date_short(performance.start_on),
            u'開場時刻': self.formatter.format_time(performance.open_on),
            u'開場時刻s': self.formatter.format_time_short(performance.open_on),
            u'開始時刻': self.formatter.format_time(performance.start_on),
            u'開始時刻s': self.formatter.format_time_short(performance.start_on),
            u'終了時刻': self.formatter.format_time(performance.end_on),
            u'終了時刻s': self.formatter.format_time_short(performance.end_on),
            })
        return retval
        
    def build_dict_from_venue(self, venue, retval=None):
        retval = {} if retval is None else retval
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
        
    def build_dict_from_seat(self, seat, ticket_number_issuer=None):
        retval = {}
        retval = self.build_dict_from_stock(seat.stock, retval)
        retval = self.build_dict_from_venue(seat.venue, retval)
        retval.update({
            u'seat': {
                u'l0_id': seat.l0_id,
                u'seat_no': seat.seat_no,
                u'name': seat.name,
                },
            u'seatAttributes': dict(seat.attributes),
            u'席番': seat.name,
            u'発券番号': ticket_number_issuer() if ticket_number_issuer else None
            })
        return retval

    def build_dict_from_product(self, product, retval=None):
        retval = retval or {}
        sales_segment = product.sales_segment

        retval.update({
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
            u'券種名': product.name,
            u'商品名': product.name,
            u'商品価格': self.formatter.format_currency(product.price),
            })
        return retval


    def build_dict_from_product_item(self, product_item):
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
            u'aux': dict(ticket_bundle.attributes) if ticket_bundle else {}, 
            u'券種名': product_item.name or product.name,
            u'商品名': product_item.name or product.name,
            u'商品価格': self.formatter.format_currency(product.price),
            u'チケット価格': self.formatter.format_currency(product_item.price),
            }

        retval = self.build_dict_from_stock(product_item.stock, retval)
        retval = self.build_dict_from_venue(product_item.performance.venue, retval)
        ## 不足分
        retval.update({
            u"席番": u"{{席番}}", 
            u'注文番号': u"{{注文番号}}",
            u'予約番号': u"{{予約番号}}", 
            u'発券番号': u"{{発券番号}}", 
            u"公演コード": u"xxx"
        })
        return retval

    def build_basic_dict_from_ordered_product_item(self, ordered_product_item, user_profile=None):
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
            u'orderedProductItemAttributes': dict(ordered_product_item.attributes),
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
            u'aux': dict(ticket_bundle.attributes) if ticket_bundle else {},
            u'券種名': product_item.name or product.name,
            u'商品名': product_item.name or product.name,
            u'商品価格': self.formatter.format_currency(ordered_product.price),
            u'チケット価格': self.formatter.format_currency(ordered_product_item.price),
            u'注文番号': order.order_no,
            u'注文日時': self.formatter.format_datetime(order.created_at),
            u'注文日時s': self.formatter.format_datetime_short(order.created_at),
            u'予約番号': order.order_no
            }

        self.build_shipping_address_dict(extra, shipping_address)
        self.build_user_profile_dict(extra, user_profile)
        return extra

    def build_dicts_from_ordered_product_item(self, ordered_product_item, user_profile=None, ticket_number_issuer=None):
        extra = self.build_basic_dict_from_ordered_product_item(ordered_product_item, user_profile)
        retval = []
        if ordered_product_item.product_item.stock.stock_type.quantity_only:
            for i in range(0, ordered_product_item.quantity):
                d = {}
                d = self.build_dict_from_stock(ordered_product_item.product_item.stock, d)
                d = self.build_dict_from_venue(ordered_product_item.product_item.performance.venue, d)
                d[u'発券番号'] = ticket_number_issuer() if ticket_number_issuer else None
                d.update(extra)
                retval.append((None, d))
        else:
            for seat in ordered_product_item.seats:
                d = self.build_dict_from_seat(seat, ticket_number_issuer)
                d.update(extra)
                retval.append((seat, d))
        return retval

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
            d.update(extra)
            return (ordered_product_item_token.seat, d) 
        else:
            d = {}
            d = self.build_dict_from_stock(ordered_product_item.product_item.stock, d)
            d = self.build_dict_from_venue(ordered_product_item.product_item.performance.venue, d)
            d[u'発券番号'] = ticket_number_issuer() if ticket_number_issuer else None
            d[u'serial'] = ordered_product_item_token.serial
            d.update(extra)
            return (None, d)

    def build_dict_from_ordered_product_item_token(self, ordered_product_item_token, user_profile=None, ticket_number_issuer=None):
        ordered_product_item = ordered_product_item_token.item
        extra = self.build_basic_dict_from_ordered_product_item(ordered_product_item, user_profile)
        return self._build_dict_from_ordered_product_item_token(extra, ordered_product_item, ordered_product_item_token, ticket_number_issuer)

    def build_dicts_from_carted_product_item(self, carted_product_item, payment_delivery_method_pair=None, ordered_product_item_attributes=None, user_profile=None, ticket_number_issuer=None):
        product_item = carted_product_item.product_item
        ticket_bundle = product_item.ticket_bundle
        carted_product = carted_product_item.carted_product
        cart = carted_product.cart
        product = carted_product.product
        shipping_address = cart.shipping_address
        payment_method = payment_delivery_method_pair and payment_delivery_method_pair.payment_method
        delivery_method = payment_delivery_method_pair and payment_delivery_method_pair.delivery_method
        sales_segment = product.sales_segment
        now = datetime.now()
        extra = {
            u'order': {
                u'total_amount': cart.total_amount,
                u'system_fee': cart.system_fee,
                u'transaction_fee': cart.transaction_fee,
                u'delivery_fee': cart.delivery_fee,
                u'order_no': cart.order_no
                },
            u'orderedProductItem': {
                u'price': product_item.price
                },
            u'orderedProductItemAttributes': ordered_product_item_attributes or {},
            u'orderedProduct': {
                u'price': product.price,
                u'quantity': carted_product.quantity
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
                } if payment_method else {},
            u'deliveryMethod': {
                u'name': delivery_method.name,
                u'fee': delivery_method.fee,
                u'fee_type': delivery_method.fee_type
                } if delivery_method else {},
            u'product': {
                u'name': product.name,
                u'price': product.price
                },
            u'productItem': {
                u'name': product_item.name,
                u'price': product_item.price,
                u'quantity': product_item.quantity
                },
            u'aux': dict(ticket_bundle.attributes) if ticket_bundle else {},
            u'券種名': product_item.name or product.name,
            u'商品名': product_item.name or product.name,
            u'商品価格': self.formatter.format_currency(product.price),
            u'チケット価格': self.formatter.format_currency(product_item.price),
            u'注文番号': cart.order_no,
            u'注文日時': self.formatter.format_datetime(now),
            u'注文日時s': self.formatter.format_datetime_short(now),
            u'予約番号': cart.order_no
            }

        self.build_shipping_address_dict(extra, shipping_address)
        self.build_user_profile_dict(extra, user_profile)

        retval = []
        if carted_product_item.product_item.stock.stock_type.quantity_only:
            for i in range(0, carted_product_item.quantity):
                d = {}
                self.build_dict_from_stock(carted_product_item.product_item.stock, d)
                self.build_dict_from_venue(carted_product_item.product_item.performance.venue, d)
                d[u'発券番号'] = ticket_number_issuer() if ticket_number_issuer else None
                d.update(extra)
                retval.append((None, d))
        else:
            for seat in carted_product_item.seats:
                d = self.build_dict_from_seat(seat, ticket_number_issuer)
                d.update(extra)
                retval.append((seat, d))
        return retval


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


