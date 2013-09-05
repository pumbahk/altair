# -*- coding: utf-8 -*-

import csv
import logging
from standardenum import StandardEnum

from altair.app.ticketing import csvutils
from altair.app.ticketing.core.models import (\
    DBSession,
    Organization,
    Performance,
    Order,
    OrderedProduct,
    OrderedProductItem,
    ChannelEnum,
    PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod,
    SalesSegmentGroup,
    SalesSegment,
    Product,
    ProductItem,
    ShippingAddress,
    SeatStatusEnum,
    Seat,
    SeatStatus,
    SejOrder,
    StockStatus
)
from altair.app.ticketing.users.models import UserCredential, Membership
from altair.app.ticketing.users.api import get_or_create_user
from altair.app.ticketing.cart.reserving import NotEnoughAdjacencyException
from altair.app.ticketing.orders.export import japanese_columns

logger = logging.getLogger(__name__)


class TemporaryModel(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def attributes(self):
        attr = dict()
        for k in self.__dict__:
            v = getattr(self, k)
            logger.info('%s %s %s' % (k, type(v), v))
            if isinstance(v, int) or isinstance(v, long) or isinstance(v, unicode):
                attr[k] = v
        return attr


class TemporaryOrder(TemporaryModel):
    pass


class TemporaryOrderedProduct(TemporaryModel):
    pass


class TemporaryOrderedProductItem(TemporaryModel):
    pass


class TemporarySeat(TemporaryModel):
    pass


class TemporaryOrderedProductItemToken(TemporaryModel):
    pass


class TemporaryShippingAddress(TemporaryModel):
    pass


class TemporarySejOrder(TemporaryModel):
    pass


def price_to_number(string):
    if string is not None:
        string = string.replace(',', '')
    return string


def csv_reader(file):
    reader = csv.DictReader(file)
    columns = dict((v, k) for k, v in japanese_columns.iteritems())
    header = []
    for field in reader.fieldnames:
        field = unicode(field.decode('cp932'))
        header.append(columns.get(field))
    reader.fieldnames = header

    for row in reader:
        for k, v in row.iteritems():
            row[k] = unicode(v.decode('cp932'))
        yield row


class ImportTypeEnum(StandardEnum):
    Create = (1, u'新規登録')
    Update = (2, u'同じ予約番号を更新')


class OrderImporter():

    def __init__(self, context, performance_id, order_csv, import_type, seat_allocation):
        self.organization_id = context.organization.id
        self.performance = Performance.get(performance_id)
        self.import_type = None
        self.seat_allocation = seat_allocation
        self.orders = dict()
        self.error_orders = dict()
        self.error_reasons = []

        for e in ImportTypeEnum:
            if e.v[0] == import_type:
                self.import_type = e.v
        self.parse_import_file(order_csv.file)

    def parse_import_file(self, file):
        reader = csv_reader(file)
        for row in reader:
            # sales_segment
            sales_segment = self.get_sales_segment(row)

            # order: dict(order_no=order)
            order_no = row.get(u'order.order_no')
            order = self.orders.get(order_no)
            if order is None:
                order = self.create_temporary_order(row, sales_segment)

            # ordered_product: dict(product_id=ordered_product)
            product = self.get_product(row, sales_segment)
            op = order.ordered_product.get(product.id)
            if op is None:
                op = self.create_temporary_ordered_product(row, product)
                order.ordered_product[product.id] = op

            # ordered_product_item: dict(product_item_id=ordered_product_item)
            product_item = self.get_product_item(row, product)
            opi = op.ordered_product_item.get(product_item.id)
            if opi is None:
                opi = self.create_temporary_ordered_product_item(row, product_item)
                op.ordered_product_item[product_item.id] = opi
            else:
                opi.quantity += int(row.get(u'ordered_product_item.quantity'))

            # seat: dict(seat_id=seat)
            seat = self.get_seat(row)
            if seat:
                opi.seats.append(seat.id)

            self.orders[order_no] = order

    def get_sales_segment(self, row):
        ssg_name = row.get(u'ordered_product.product.sales_segment.sales_segment_group.name')
        try:
            sales_segment = SalesSegment.query.join(SalesSegmentGroup).filter(
                SalesSegment.performance_id == self.performance.id,
                SalesSegmentGroup.name == ssg_name,
            ).one()
        except Exception:
            raise
        return sales_segment

    def get_pdmp(self, row, sales_segment):
        payment_method_name = row.get(u'payment_method.name')
        delivery_method_name = row.get(u'delivery_method.name')
        try:
            pdmp = PaymentDeliveryMethodPair.query.filter(
                PaymentDeliveryMethodPair.sales_segment_group_id == sales_segment.sales_segment_group_id
            ).join(PaymentMethod).filter(
                PaymentMethod.name == payment_method_name
            ).join(DeliveryMethod).filter(
                DeliveryMethod.name == delivery_method_name
            ).one()
        except Exception:
            raise
        return pdmp

    def get_user(self, row):
        # Todo: membershipも条件にいれないとだめ？
        #row.get(u'membership.name')
        #row.get(u'membergroup.name')
        auth_identifier = row.get(u'user_credential.auth_identifier')
        logger.info(auth_identifier)
        try:
            credential = UserCredential.query.filter(
                UserCredential.auth_identifier == auth_identifier
            ).one()
        except Exception:
            raise
        return credential.user

    def get_product(self, row, sales_segment):
        product_name = row.get(u'ordered_product.product.name')
        try:
            product = Product.query.filter(
                Product.sales_segment_id == sales_segment.id,
                Product.name == product_name
            ).one()
        except Exception:
            raise
        return product

    def get_product_item(self, row, product):
        product_item_name = row.get(u'ordered_product_item.product_item.name')
        try:
            product = ProductItem.query.filter(
                ProductItem.product_id == product.id,
                ProductItem.name == product_item_name
            ).one()
        except Exception:
            raise
        return product

    def get_seat(self, row):
        seat_name = row.get(u'seat.name')
        if not seat_name:
            return None

        try:
            seat = Seat.query.filter(
                Seat.venue_id == self.performance.venue.id,
                Seat.name == seat_name
            ).one()
        except Exception:
            raise
        return seat

    def create_temporary_order(self, row, sales_segment):
        pdmp = self.get_pdmp(row, sales_segment)
        user = self.get_user(row)

        order = TemporaryOrder(
            order_no            = row.get(u'order.order_no'),
            total_amount        = price_to_number(row.get(u'order.total_amount')),
            system_fee          = price_to_number(row.get(u'order.system_fee')),
            transaction_fee     = price_to_number(row.get(u'order.transaction_fee')),
            delivery_fee        = price_to_number(row.get(u'order.delivery_fee')),
            paid_at             = row.get(u'order.paid_at'),
            delivered_at        = row.get(u'order.delivered_at'),
            canceled_at         = row.get(u'order.canceled_at'),
            created_at          = row.get(u'order.created_at'),
            note                = row.get(u'order.note'),
            card_brand          = row.get(u'order.card_brand'),
            card_ahead_com_code = row.get(u'order.card_ahead_com_code'),
            card_ahead_com_name = row.get(u'order.card_ahead_com_name'),
            performance_id      = self.performance.id,
            organization_id     = self.organization_id,
            channel             = ChannelEnum.INNER.v,
            sales_segment_id    = sales_segment.id,
            payment_delivery_method_pair_id = pdmp.id,
            branch_no           = 1,
            user_id             = user.id,
            shipping_address    = self.create_temporary_shipping_address(row),
            sej_order           = self.create_sej_order(row),
            ordered_product     = dict()
            #Todo:operator_id=,
        )
        logger.info(vars(order))
        return order

    def create_temporary_ordered_product(self, row, product):
        ordered_product = TemporaryOrderedProduct(
            price = price_to_number(row.get(u'ordered_product.price')),
            quantity = int(row.get(u'ordered_product.quantity')),
            product_id = product.id,
            ordered_product_item = dict()
        )
        return ordered_product

    def create_temporary_ordered_product_item(self, row, product_item):
        ordered_product_item = TemporaryOrderedProductItem(
            price = price_to_number(row.get(u'ordered_product_item.price')),
            quantity = int(row.get(u'ordered_product_item.quantity')),
            product_item_id = product_item.id,
            seats = []
        )
        return ordered_product_item

    def create_temporary_shipping_address(self, row):
        shipping_address    = TemporaryOrderedProduct(
            first_name      = row.get(u'shipping_address.first_name'),
            last_name       = row.get(u'shipping_address.last_name'),
            first_name_kana = row.get(u'shipping_address.first_name_kana'),
            last_name_kana  = row.get(u'shipping_address.last_name_kana'),
            zip             = row.get(u'shipping_address.zip'),
            country         = row.get(u'shipping_address.country'),
            prefecture      = row.get(u'shipping_address.prefecture'),
            city            = row.get(u'shipping_address.city'),
            address_1       = row.get(u'shipping_address.address_1'),
            address_2       = row.get(u'shipping_address.address_2'),
            tel_1           = row.get(u'shipping_address.tel_1'),
            tel_2           = row.get(u'shipping_address.tel_2'),
            fax             = row.get(u'shipping_address.fax'),
            email_1         = row.get(u'shipping_address.email_1'),
            email_2         = row.get(u'shipping_address.email_2'),
            sex             = row.get(u'user_profile.sex'),
            nick_name       = row.get(u'user_profile.nick_name')
        )
        return shipping_address

    def create_sej_order(self, row):
        sej_order = TemporarySejOrder(
            billing_number = row.get(u'sej_order.billing_number'),
            exchange_number = row.get(u'sej_order.exchange_number'),
        )
        return sej_order

    def allocate_seats(self, reserving):
        if not self.seat_allocation:
            return

        # 予約(ダミーOrder)単位で1件ずつおまかせ配席をしていく
        # 座席ステータスはインナー予約での座席確保と同じ状態にする
        order_no_list = self.orders.keys()
        for order_no in order_no_list:
            order = self.orders.get(order_no)
            status = True
            for op in order.ordered_product.values():
                for opi in op.ordered_product_item.values():
                    product_item = ProductItem.query.filter_by(id=opi.product_item_id).one()
                    try:
                        logger.info('product_item_id = %sm stock_id = %s, quantity = %s' % (product_item.id, product_item.stock_id, opi.quantity))
                        seats = reserving.reserve_seats(product_item.stock_id, int(opi.quantity), reserve_status=SeatStatusEnum.Keep)
                        opi.seats = [s.id for s in seats]
                        logger.info(opi.seats)
                    except NotEnoughAdjacencyException, e:
                        logger.info('cannot allocate seat (stock_id=%s, quantity=%s) %s' % (product_item.stock_id, opi.quantity, e))
                        status = False
                        self.error_reasons.append(
                            u'配席できません 予約番号: %s  商品明細: %s  個数: %s  stock_id: %s' % (order_no, product_item.name, opi.quantity, product_item.stock_id)
                        )
                        break
                if not status:
                    break
            if not status:
                self.error_orders[order_no] = self.orders.pop(order_no)

    def release_seats(self):
        if not self.seat_allocation:
            return

        for order in self.orders.values():
            for op in order.ordered_product.values():
                for opi in op.ordered_product_item.values():
                    for seat_id in opi.seats:
                        seat_status = SeatStatus.query.filter_by(seat_id=seat_id).one()
                        if seat_status.status == int(SeatStatusEnum.Keep):
                            logger.info('seat(%s) status Keep to Vacant' % seat_status.seat_id)
                            seat_status.status = int(SeatStatusEnum.Vacant)

    def get_order_per_product(self):
        order_per_product = dict()
        for order in self.orders.values():
            for op in order.ordered_product.values():
                p = Product.query.filter_by(id=op.product_id).one()
                if p not in order_per_product:
                    order_per_product[p] = 0
                order_per_product[p] += sum([int(opi.quantity) for opi in op.ordered_product_item.values()])
        return order_per_product

    def get_order_per_pdmp(self):
        order_per_pdmp = dict()
        for order in self.orders.values():
            pdmp = PaymentDeliveryMethodPair.query.filter_by(id=order.payment_delivery_method_pair_id).one()
            if pdmp not in order_per_pdmp:
                order_per_pdmp[pdmp] = 0
            order_per_pdmp[pdmp] += 1
        return order_per_pdmp

    def statistics(self):
        stats = dict()

        # インポート方法
        stats['import_type'] = self.import_type
        # 数受けの予約に座席を割り当てるかどうか
        stats['seat_allocation'] = self.seat_allocation
        # 登録予定の予約件数合計
        stats['total_order_count'] = len(self.orders)
        # 商品別の予約件数、席数
        stats['order_per_product'] = self.get_order_per_product()
        # 決済方法/引取方法ごとの予約券数、コンビニ引取があるなら発券開始日時
        stats['order_per_pdmp'] = self.get_order_per_pdmp()
        # 配席できない予約の数
        stats['error_order_count'] = len(self.error_orders)
        # 配席できない理由
        stats['error_reasons'] = self.error_reasons

        return stats

    def execute(self):
        # Todo: 予約生成処理、temp_to_order
        decrease_per_stock = dict()
        for temp_order in self.orders.values():
            # 新規追加ならorder_noを採番
            if self.import_type == ImportTypeEnum.Create.v:
                from altair.app.ticketing.core import api as c_api
                from altair.app.ticketing.utils import sensible_alnum_encode
                organization = Organization.query.filter_by(id=self.organization_id).one()
                base_id = c_api.get_next_order_no()
                order_no = organization.code + sensible_alnum_encode(base_id).zfill(10)
                temp_order.order_no = order_no
            #else:
            #    temp_order.branch_no = DBSession.query(Order.branch_no).filter(Order.order_no==order_no).scalar()

            # ShippingAddress
            temp_shipping_address = temp_order.shipping_address
            attr = temp_shipping_address.attributes()
            shipping_address = ShippingAddress(**attr)
            shipping_address.save()
            logger.info(vars(shipping_address))

            # Order
            attr = temp_order.attributes()
            attr.update({'shipping_address':shipping_address})
            order = Order(**attr)
            order.save()
            logger.info(vars(order))

            # SejOrder
            # Todo: Sejとの通信
            temp_sej_order = temp_order.sej_order
            attr = temp_sej_order.attributes()
            attr.update({'order_id':order.order_no})
            sej_order = SejOrder(**attr)
            sej_order.save()
            logger.info(vars(sej_order))

            for temp_ordered_product in temp_order.ordered_product.values():
                # OrderedProduct
                attr = temp_ordered_product.attributes()
                attr.update({'order':order})
                ordered_product = OrderedProduct(**attr)
                ordered_product.save()
                logger.info(vars(ordered_product))

                for temp_ordered_product_item in temp_ordered_product.ordered_product_item.values():
                    # OrderedProductItem
                    attr = temp_ordered_product_item.attributes()
                    attr.update({'ordered_product':ordered_product})
                    ordered_product_item = OrderedProductItem(**attr)

                    seats = []
                    for seat_id in temp_ordered_product_item.seats:
                        # update SeatStatus
                        seat_status = SeatStatus.query.filter_by(seat_id=seat_id).one()
                        logger.info('seat(%s) status Keep to Ordered' % seat_status.seat_id)
                        if seat_status.status != int(SeatStatusEnum.Keep):
                            logger.error('seat(%s) invalid status %s' % (seat_status.seat_id, seat_status.status))
                            raise Exception(u'invalid status')
                        seat_status.status = int(SeatStatusEnum.Ordered)
                        seats.append(seat_status.seat)

                        # for update StockStatus.quantity
                        stock_id = seat_status.seat.stock_id
                        if stock_id not in decrease_per_stock.keys():
                            decrease_per_stock[stock_id] = 0
                        decrease_per_stock[stock_id] += 1

                    ordered_product_item.seats = seats
                    ordered_product_item.save()
                    logger.info(vars(ordered_product_item))

        # StockStatus.quantity はまとめて減算
        for stock_id, quantity in decrease_per_stock.iteritems():
            stock_status = StockStatus.query.filter_by(stock_id=stock_id).one()
            stock_status.quantity -= quantity

        return
