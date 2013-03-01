# -*- coding: utf-8 -*-

from collections import OrderedDict

from paste.util.multidict import MultiDict
from sqlalchemy.sql.expression import or_

from ticketing.cart.helpers import format_number as _format_number
from ticketing.core.models import no_filter
from ticketing.models import record_to_multidict
from ticketing.mailmags.models import MailSubscription, MailMagazine, MailSubscriptionStatus

def format_number(value):
    return _format_number(float(value))

def _create_mailsubscription_cache(organization_id):
    D = dict()
    query = MailSubscription.query\
        .filter(MailSubscription.segment_id == MailMagazine.id)\
        .filter(or_(MailSubscription.status == None, MailSubscription.status == MailSubscriptionStatus.Subscribed.v))
    if organization_id:
        query = query.filter(MailMagazine.organization_id == organization_id)
    for ms in query:
        D[ms.email] = True
    return D

def one_or_empty(b):
    return '1' if b else ''

def encode_to_cp932(row):
    encoded = {}
    for key, value in row.items():
        if value:
            if not isinstance(value, unicode):
                value = unicode(value)
            value = value.encode('cp932')
        else:
            value = ''
        encoded[key.encode('cp932')] = value
    return encoded


class OrderCSV(object):
    order_value_filters = dict((k, format_number) for k in ['transaction_fee', 'delivery_fee', 'system_fee', 'total_amount'])

    EXPORT_TYPE_ORDER = 1
    EXPORT_TYPE_SEAT = 2

    # csv header
    order_header = OrderedDict([
        ('order_no', u'予約番号'),
        ('status', u'ステータス'),
        ('payment_status', u'決済ステータス'),
        ('created_at', u'予約日時'),
        ('paid_at', u'支払日時'),
        ('delivered_at', u'配送日時'),
        ('canceled_at', u'キャンセル日時'),
        ('total_amount', u'合計金額'),
        ('transaction_fee', u'決済手数料'),
        ('delivery_fee', u'配送手数料'),
        ('system_fee', u'システム手数料'),
        ('note', u'メモ'),
        ])
    user_profile_header = OrderedDict([
        ('last_name', u'姓'),
        ('first_name', u'名'),
        ('last_name_kana', u'姓(カナ)'),
        ('first_name_kana', u'名(カナ)'),
        ('nick_name', u'ニックネーム'),
        ('sex', u'性別'),
    ])
    membership_header = OrderedDict([
        ('name', u'会員種別名'),
    ])
    membergroup_header = OrderedDict([
        ('name', u'会員グループ名'),
    ])
    user_credential_header = OrderedDict([
        ('auth_identifier', u'会員種別ID'),
    ])
    shipping_address_header = OrderedDict([
        ('last_name', u'配送先姓'),
        ('first_name', u'配送先名'),
        ('last_name_kana', u'配送先姓(カナ)'),
        ('first_name_kana', u'配送先名(カナ)'),
        ('zip', u'郵便番号'),
        ('country', u'国'),
        ('prefecture', u'都道府県'),
        ('city', u'市区町村'),
        ('address_1', u'住所1'),
        ('address_2', u'住所2'),
        ('tel_1', u'電話番号1'),
        ('tel_2', u'電話番号2'),
        ('fax', u'FAX'),
        ('email_1', u'メールアドレス1'),
        ('email_2', u'メールアドレス2'),
    ])
    payment_method_header = OrderedDict([
        ('name', u'決済方法'),
    ])
    delivery_method_header = OrderedDict([
        ('name', u'引取方法'),
    ])
    event_header = OrderedDict([
        ('title', u'イベント')
    ])
    performance_header = OrderedDict([
        ('name', u'公演'),
        ('code', u'公演コード'),
        ('start_on', u'公演日'),
    ])
    venue_header = OrderedDict([
        ('name', u'会場'),
    ])
    ordered_product_header = OrderedDict([
        ('price', u'商品単価'),
        ('quantity', u'商品個数'),
    ])
    product_header = OrderedDict([
        ('name', u'商品名'),
    ])
    sales_segment_group_header = OrderedDict([
        ('name', u'販売区分'),
    ])
    product_item_header = OrderedDict([
        ('name', u'商品明細名'),
        ('price', u'商品明細単価'),
        ('quantity', u'商品明細個数'),
        ('print_histories', u'発券作業者'),
    ])
    attribute_header = OrderedDict([
        ('t_shirts_size', u'Tシャツサイズ'),
        ('publicity', u'公開可否'),
        ('mail_permission', u'メールマガジン受信可否'),
        ('cont', u'区分'),
        ('old_id_number', u'旧会員番号')
    ])
    seat_header = OrderedDict([
        ('name', u'座席名'),
    ])

    def __init__(self, orders, export_type=EXPORT_TYPE_ORDER, organization_id=None):
        self.export_type = int(export_type)
        self.organization_id = organization_id
        self._mailsubscription_cache = None
        self.header = self.order_header.values()\
                      + self.user_profile_header.values()\
                      + self.membership_header.values()\
                      + self.membergroup_header.values()\
                      + self.user_credential_header.values()\
                      + self.shipping_address_header.values()\
                      + self.payment_method_header.values()\
                      + self.delivery_method_header.values()\
                      + self.event_header.values()\
                      + self.performance_header.values()\
                      + self.venue_header.values()
        self.header = [column.encode('cp932') for column in self.header]
        self.rows = []
        for order in orders:
            self.rows += self._convert_to_csv(order)

    @property
    def mailsubscription_cache(self):
        if self._mailsubscription_cache is None:
            if "mail_permission_0" not in self.header:
                self.header.append("mail_permission_0")
            self._mailsubscription_cache = _create_mailsubscription_cache(self.organization_id)
        return self._mailsubscription_cache

    def get_row_data(self, header, data, filter=None):
        if not isinstance(data, MultiDict):
            data = record_to_multidict(data)
        if filter is None:
            filter = dict()
        return [(label, filter.get(column, no_filter)(data.get(column))) for column, label in header.items()]

    def add_row_data(self, header, data, filter=None):
        self.row_data += self.get_row_data(header, data, filter)

    def add_header_column(self, label, num1, num2=None):
        if self.export_type == self.EXPORT_TYPE_ORDER:
            if num2 is not None:
                label = u'%s_%s_%s' % (label, num1, num2)
            else:
                label = u'%s_%s' % (label, num1)
        label_str = label.encode('cp932')
        if not label_str in self.header:
            self.header.append(label_str)
        return label

    def add_row_data_with_header(self, header, data, num):
        result = []
        d = record_to_multidict(data)
        for column, label in header.items():
            label = self.add_header_column(label, num)
            result.append((label, d.get(column)))
        if self.export_type == self.EXPORT_TYPE_ORDER:
            self.row_data += result
        else:
            if num not in self.product_data:
                self.product_data[num] = []
            self.product_data[num] += result

    def get_product_item_data(self, ordered_product_item, num1, num2):
        d = record_to_multidict(ordered_product_item.product_item)
        result = []
        for column, label in self.product_item_header.items():
            label = self.add_header_column(label, num1, num2)
            value = ''
            if column == 'quantity':
                value = ordered_product_item.ordered_product.quantity
                if ordered_product_item.seats:
                    if self.export_type == self.EXPORT_TYPE_ORDER:
                        value = len(ordered_product_item.seats)
                    else:
                        value = 1
            elif column == 'print_histories':
                if ordered_product_item.issued_at:
                    value = ', '.join(list(set([(ph.operator.name) for ph in ordered_product_item.print_histories if ph.operator])))
            else:
                value = d.get(column)
            result.append((label, value))
        return result

    def get_booster_data(self, ordered_product_item, num2):
        result = []
        for column, label in self.attribute_header.items():
            value = ordered_product_item.attributes.get(column, None)
            if value is None:
                continue
            label = self.add_header_column(label, num2)

            if column == 'mail_permission':
                value = '' if value is None else value
            elif column == 'cont':
                value = u'新規' if value == 'no' else u'継続'
            result.append((label, value))
        return result

    def get_seat_data(self, ordered_product_item, num1):
        result = []
        for column, label in self.seat_header.items():
            label = self.add_header_column(label, num1)

            if column == 'name':
                if self.export_type == self.EXPORT_TYPE_ORDER:
                    seat_name = ''
                    if ordered_product_item.seats:
                        seat_name = ', '.join([(seat.name) for seat in ordered_product_item.seats if seat.name])
                    result.append((label, seat_name))
                else:
                    if ordered_product_item.seats:
                        for seat in ordered_product_item.seats:
                            result.append((label, seat.name))
                    else:
                        result.append((label, ''))
        return result

    def _convert_to_csv(self, order):
        self.row_data = []
        self.product_data = {}

        order_dict = record_to_multidict(order)
        order_dict.add('created_at', str(order.created_at))
        order_dict.add('status', order.status)
        order_dict.add('payment_status', order.payment_status)

        self.add_row_data(self.order_header, order_dict, self.order_value_filters)
        if order.user and order.user.user_profile:
            self.add_row_data(self.user_profile_header, order.user.user_profile)
        if order.user and order.user.user_credential:
            user_credential = order.user.user_credential[0]
            self.add_row_data(self.membership_header, user_credential.membership)
            self.add_row_data(self.user_credential_header, user_credential)
        if order.user and order.user.member:
            self.add_row_data(self.membergroup_header, order.user.member.membergroup)
        if order.shipping_address:
            self.add_row_data(self.shipping_address_header, order.shipping_address)
        self.add_row_data(self.payment_method_header, order.payment_delivery_pair.payment_method)
        self.add_row_data(self.delivery_method_header, order.payment_delivery_pair.delivery_method)
        self.add_row_data(self.event_header, order.performance.event)
        self.add_row_data(self.performance_header, order.performance)
        self.add_row_data(self.venue_header, order.performance.venue)

        product_item_data = {}
        seat_data = {}
        for i, ordered_product in enumerate(order.ordered_products):
            #if self.export_type == self.EXPORT_TYPE_SEAT and not ordered_product.product.seat_stock_type.is_seat:
            #    continue

            self.add_row_data_with_header(self.product_header, ordered_product.product, i)
            self.add_row_data_with_header(self.ordered_product_header, ordered_product, i)
            self.add_row_data_with_header(self.sales_segment_group_header, ordered_product.product.sales_segment.sales_segment_group, i)

            product_item_data[i] = {}
            seat_data[i] = {}
            for j, ordered_product_item in enumerate(ordered_product.ordered_product_items):
                buffer = self.get_product_item_data(ordered_product_item, i, j)
                buffer += self.get_booster_data(ordered_product_item, j)
                if self.export_type == self.EXPORT_TYPE_ORDER:
                    self.row_data += buffer
                else:
                    if j not in product_item_data[i]:
                        product_item_data[i][j] = []
                    product_item_data[i][j] = buffer

                buffer = self.get_seat_data(ordered_product_item, i)
                if self.export_type == self.EXPORT_TYPE_ORDER:
                    self.row_data += buffer
                else:
                    if j not in seat_data[i]:
                        seat_data[i][j] = []
                    seat_data[i][j] = buffer

        if self.export_type == self.EXPORT_TYPE_ORDER:
            row = dict(self.row_data)
            if u'メールアドレス1_1' in row and not row.get(u'メールマガジン受信可否_0'):
                row[u'メールマガジン受信可否_0'] = one_or_empty(self.mailsubscription_cache.get(row[u'メールアドレス1_1']) or\
                                                             self.mailsubscription_cache.get(row[u'メールアドレス1_2']))
            return [encode_to_cp932(row)]
        else:
            rows = []
            for i, product in self.product_data.iteritems():
                for j, seats in seat_data[i].iteritems():
                    for seat in seats:
                        row = dict(
                            self.row_data
                            + self.product_data[i]
                            + product_item_data[i][j]
                            + [seat]
                        )
                        if u'メールアドレス1_1' in row and not row.get(u'メールマガジン受信可否_0'):
                            row[u'メールマガジン受信可否_0'] = one_or_empty(self.mailsubscription_cache.get(row[u'メールアドレス1_1']) or\
                                                                         self.mailsubscription_cache.get(row[u'メールアドレス1_2']))
                        rows.append(encode_to_cp932(row))
            return rows
