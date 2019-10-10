#-*- coding: utf-8 -*-
import os
import time
import logging
import datetime
import sqlalchemy as sa
import itertools
from StringIO import StringIO
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import contains_eager, aliased
from pyramid.threadlocal import get_current_request
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import (
    Seat,
    Venue,
    Event,
    Performance,
    Stock,
    StockHolder,
    AugusAccount,
    AugusPerformance,
    AugusVenue,
    AugusTicket,
    AugusPutback,
    AugusSeat,
    AugusStockInfo,
    SeatStatus,
    SeatStatusEnum,
    AugusSeatStatus,
    AugusUnreservedSeatStatus,
    AugusPerformance,
    AugusStockDetail,
    Product,
    )
from altair.app.ticketing.orders.models import (
    orders_seat_table,
    OrderedProductItem,
    OrderedProduct,
    Order
    )
from altair.augus.types import (
    DateType,
    HourMinType,
    )
from altair.augus.protocols.putback import (
    PutbackResponseRecord,
    PutbackResponse,
    )
from altair.augus.protocols import (
    DistributionSyncResponse,
    AchievementResponse,
    )
from altair.augus.protocols.putback import PutbackWithNumberedTicketResponseRecord
from altair.augus.protocols.achievement import AchievementWithNumberedTicketResponse
from altair.augus.exporters import AugusExporter
from .errors import (
    AugusDataExportError,
    DuplicateFileNameError,
    )
from altair.augus.types import (
    SeatTypeClassif,
)
logger = logging.getLogger(__name__)
RETRY = 100

class AugusDistributionExporter(object):
    def create_response(self, request, status):
        response = DistributionSyncResponse()

        res_record_data = list(set(
            [(rec.event_code, rec.performance_code, rec.distribution_code)
             for rec in request]))

        response.customer_id = request.customer_id
        response.event_code = request.event_code
        response.date = request.date

        for event_code, performance_code, distribution_code in res_record_data:
            record = response.record()
            record.event_code = event_code
            record.performance_code = performance_code
            record.distribution_code = distribution_code
            record.status = status.value
            response.append(record)
        return response

    def export(self, path, request, status):
        response = self.create_response(request, status)
        resfile_path = os.path.join(path, response.name)
        AugusExporter.export(response, resfile_path)


class AugusPutbackExporter(object):
    def __init__(self):
        self._slave_session = get_db_session(get_current_request(), name="slave")

    def create_record(self, stock_detail, use_numbered_ticket_format=False, enable_unreserved_seat=False):
        ag_putback = stock_detail.augus_putback
        ag_stock_info = stock_detail.augus_stock_info
        # 自由席offで自由席の返券はない想定。万一自由席のデータがあっても
        # 後のag_seatがNone（自由席はAugusSeatを作らない）になりエラーが発生するので気づけるはず
        # ....
        # AugusStockDetailの席区分はなぜかintなのでstrに変換しないとSeatTypeClassifを取得できない。
        stock_detail_seat_type_classif = str(stock_detail.seat_type_classif)
        is_reserved_seat = \
            not (enable_unreserved_seat and SeatTypeClassif.FREE == SeatTypeClassif.get(stock_detail_seat_type_classif))
        ag_seat = stock_detail.augus_stock_info.augus_seat
        ag_performance = stock_detail.augus_putback.augus_performance
        ag_ticket = stock_detail.augus_ticket

        record = PutbackWithNumberedTicketResponseRecord() if use_numbered_ticket_format else PutbackResponseRecord()
        record.event_code = ag_performance.augus_event_code
        record.performance_code = ag_performance.augus_performance_code
        record.distribution_code = stock_detail.augus_distribution_code
        record.putback_code = stock_detail.augus_putback.augus_putback_code
        record.seat_type_code = stock_detail.augus_seat_type_code
        record.unit_value_code = stock_detail.augus_unit_value_code
        record.date = ag_performance.start_on.strftime(DateType.FORMAT)
        record.start_on = ag_performance.start_on.strftime(HourMinType.FORMAT)
        record.block = ag_seat.block if is_reserved_seat else 0  # 自由席は0固定
        record.coordy = ag_seat.coordy if is_reserved_seat else 0  # 自由席は0固定
        record.coordx = ag_seat.coordx if is_reserved_seat else 0  # 自由席は0固定
        record.coordy_whole = ag_seat.coordy_whole if is_reserved_seat else 0  # 自由席は0固定
        record.coordx_whole = ag_seat.coordx_whole if is_reserved_seat else 0 # 自由席は0固定
        record.area_code = ag_seat.area_code if is_reserved_seat else 0 # 自由席は0固定
        record.info_code = ag_seat.info_code if is_reserved_seat else 0 # 自由席は0固定
        record.floor = ag_seat.floor if is_reserved_seat else u'' # 自由席は空
        record.column = ag_seat.column if is_reserved_seat else u'' # 自由席は空
        record.number = ag_seat.num if is_reserved_seat else u'' # 自由席は空
        if use_numbered_ticket_format:
            record.ticket_number = ag_seat.ticket_number if is_reserved_seat else ''
        record.seat_type_classif = ag_ticket.augus_seat_type_classif
        if is_reserved_seat:
            # TKT-5866 指定席でもAugusStockDetailからcountを取得してもいいと思うが、念のため既存処理のままとする
            record.seat_count = ag_stock_info.quantity
        else:
            # TKT-5866 自由席の場合はAugusStockDetailからcountを取得する
            record.seat_count = stock_detail.quantity
        record.putback_status = stock_detail.augus_putback_status
        record.putback_type = ag_putback.augus_putback_type
        return record

    def create_responses(self, putbacks=[], customer_id=None):
        if not putbacks:
            qs = AugusPutback\
                .query\
                .filter(AugusPutback.notified_at==None)\
                .filter(AugusPutback.reserved_at!=None)
            if customer_id:
                qs = qs\
                    .join(AugusAccount)\
                    .filter(AugusAccount.code==customer_id)
            putbacks = qs.all()

        now = datetime.datetime.now()

        augus_account = \
            self._slave_session.query(AugusAccount)\
                .filter(AugusAccount.code == customer_id)\
                .one()
        use_numbered_ticket_format = augus_account.use_numbered_ticket_format if augus_account else False
        enable_unreserved_seat = augus_account.enable_unreserved_seat if augus_account else False

        responses = []
        for putback in putbacks:
            response = PutbackResponse()
            response.event_code = putback.augus_performance.augus_event_code
            response.date = putback.augus_performance.start_on
            response.extend([self.create_record(stock_detail,
                                                use_numbered_ticket_format=use_numbered_ticket_format,
                                                enable_unreserved_seat=enable_unreserved_seat)
                             for stock_detail in putback.augus_stock_details])
            responses.append(response)
            putback.notified_at = now
            putback.save()
        return responses

    def export(self, path, customer_id):
        responses = self.create_responses(customer_id=customer_id)
        for response in responses:
            if len(response) == 0:
                continue
            response.customer_id = customer_id
            response.start_on = response[0].start_on
            resfile_path = ''
            for ii in range(RETRY):
                response.created_at = time.localtime()
                resfile_path = os.path.join(path, response.name)
                if not os.path.exists(resfile_path):
                    break
                time.sleep(1)
            else:
                raise DuplicateFileNameError(resfile_path)
            AugusExporter.export(response, resfile_path)
        return responses


class AugusAchievementExporter(object):
    def __init__(self, now=None):
        if now:
            now = datetime.datetime.strptime(now, '%Y/%m/%d_%H:%M:%S')
        else:
            now = datetime.datetime.now()

        self.now = now
        self.session = get_db_session(get_current_request(), name="slave")

    def create_record(self, seat, seat_status_checked=False, use_numbered_ticket_format=False):
        if not seat_status_checked and seat.status in [SeatStatusEnum.InCart.v, SeatStatusEnum.NotOnSale.v, SeatStatusEnum.Vacant.v, SeatStatusEnum.Canceled.v]:
            return

        try:
            augus_stock_detail = AugusStockDetail\
            .query\
            .join(AugusStockInfo)\
            .filter(AugusStockInfo.seat_id==seat.id)\
            .filter(AugusStockDetail.augus_putback_id==None)\
            .one() # MultiplFound: 多重配席, NoResultFound: 未配席
        except NoResultFound as err: # 未配席
            return None

        ordered_product_item = self.seat2opitem(seat)
        if ordered_product_item:
            augus_ticket = ordered_product_item.ordered_product.product.augus_ticket
            if not augus_ticket:
                raise AugusDataExportError(
                    'No cooperation product to augus: OrderedProductItem.id={} Product.id={}'.format(
                        ordered_product_item.id, ordered_product_item.ordered_product.product.id
                        )) # チケット連携されていない

        else:
            augus_ticket = augus_stock_detail.augus_ticket

        order = self.get_order(ordered_product_item)
        status = AugusSeatStatus.get_status(seat, order)

        try:
            record = AchievementWithNumberedTicketResponse.record() \
                if use_numbered_ticket_format else AchievementResponse.record()
            record.event_code = augus_stock_detail.augus_stock_info.augus_performance.augus_event_code
            record.performance_code = augus_stock_detail.augus_stock_info.augus_performance.augus_performance_code
            record.distribution_code = augus_stock_detail.augus_distribution_code
            record.seat_type_code = augus_ticket.augus_seat_type_code
            record.unit_value_code = augus_ticket.unit_value_code
            record.date = augus_stock_detail.augus_stock_info.augus_performance.start_on.strftime(DateType.FORMAT)
            record.start_on = augus_stock_detail.augus_stock_info.augus_performance.start_on.strftime(HourMinType.FORMAT)
            record.reservation_number = order.order_no if order else ''
            record.block = augus_stock_detail.augus_stock_info.augus_seat.block
            record.coordy = augus_stock_detail.augus_stock_info.augus_seat.coordy
            record.coordx = augus_stock_detail.augus_stock_info.augus_seat.coordx
            record.area_code = augus_stock_detail.augus_stock_info.augus_seat.area_code
            record.info_code = augus_stock_detail.augus_stock_info.augus_seat.info_code
            record.floor = augus_stock_detail.augus_stock_info.augus_seat.floor
            record.column = augus_stock_detail.augus_stock_info.augus_seat.column
            record.number = augus_stock_detail.augus_stock_info.augus_seat.num
            if use_numbered_ticket_format:
                record.ticket_number = augus_stock_detail.augus_stock_info.augus_seat.ticket_number
            record.seat_type_classif = augus_stock_detail.augus_stock_info.seat_type_classif
            record.seat_count = augus_stock_detail.quantity
            record.unit_value = augus_ticket.value
            #record.unit_value = self.get_unit_price(opitem) # こっちはaltairで実際に販売した単価(おおよそ (altairでは席の単価は厳密には出せない))
            record.processed_at = time.strftime('%Y%m%d%H%M%S')
            record.achievement_status = str(status)
        except ValueError as e:
            logger.info('order {}, seat id {} cause ValueError. Error Message: {}'.format(order.no, seat.id, e.message))
        return record

    def __create_record_of_unreserved_seat(self, augus_performance, order,
                                           ordered_product, use_numbered_ticket_format=False):
        augus_ticket = ordered_product.product.augus_ticket
        augus_stock_info = augus_ticket.augus_stock_infos[0]  # 自由席では複数存在しない想定

        # 自由席ではOrderedProduct単位でレコードを作る
        record = AchievementWithNumberedTicketResponse.record() \
            if use_numbered_ticket_format else AchievementResponse.record()
        record.event_code = augus_performance.augus_event_code
        record.performance_code = augus_performance.augus_performance_code
        record.distribution_code = augus_stock_info.augus_distribution_code
        record.seat_type_code = augus_ticket.augus_seat_type_code
        record.unit_value_code = augus_ticket.unit_value_code
        record.date = augus_performance.start_on.strftime(DateType.FORMAT)
        record.start_on = augus_performance.start_on.strftime(HourMinType.FORMAT)
        record.reservation_number = order.order_no
        record.block = 0   # 自由席は固定で0
        record.coordy = 0  # 自由席は固定で0
        record.coordx = 0  # 自由席は固定で0
        record.area_code = 0  # 自由席は固定で0
        record.info_code = 0  # 自由席は固定で0
        record.floor = u''  # 自由席は固定で空
        record.column = u''  # 自由席は固定で空
        record.number = u''  # 自由席は固定で空
        if use_numbered_ticket_format:
            record.ticket_number = u''  # 自由席は固定で空
        record.seat_type_classif = augus_stock_info.seat_type_classif
        record.seat_count = ordered_product.quantity
        record.unit_value = augus_ticket.value
        record.processed_at = time.strftime('%Y%m%d%H%M%S')
        record.achievement_status = str(AugusUnreservedSeatStatus.get_status(order))

        return record

    def export(self, performance):
        # tkt5866 このメソッドは使用されておらず、メンテもされていない
        import warnings
        warnings.warn('This is old and unsupported method.')
        res = AchievementResponse()
        for seat in performance.seats:
            record = self.create_record(seat)
            if record:
                res.append(record)
        return res

    def _create_record(self, stock_info):
        # tkt5866 このメソッドは使用されておらず、メンテもされていない
        import warnings
        warnings.warn('This is old and unsupported method.')

        opitem = self.seat2opitem(stock_info.seat)
        if not opitem:
            raise AugusDataExportError('No such OrderedProductItem: Seat.id={}'.formamt(stock_info.seat))

        record = AchievementResponse.record()
        record.event_code = stock_info.augus_performance.augus_event_code
        record.performance_code = stock_info.augus_performance.augus_performance_code
        record.distribution_code = stock_info.augus_distribution_code
        record.seat_type_code = stock_info.augus_ticket.augus_seat_type_code
        record.unit_value_code = stock_info.augus_ticket.unit_value_code

        record.date = stock_info.augus_performance.start_on.strftime(DateType.FORMAT)
        record.start_on = stock_info.augus_performance.start_on.strftime(HourMinType.FORMAT)

        record.reservation_number = self.get_order_no(opitem)
        record.block = stock_info.augus_seat.block
        record.coordy = stock_info.augus_seat.coordy
        record.coordx = stock_info.augus_seat.coordx
        record.area_code = stock_info.augus_seat.area_code
        record.info_code = stock_info.augus_seat.info_code
        record.floor = stock_info.augus_seat.floor
        record.column = stock_info.augus_seat.column
        record.number = stock_info.augus_seat.num
        record.seat_type_classif = stock_info.seat_type_classif
        record.seat_count = stock_info.quantity
        record.unit_value = stock_info.augus_ticket.value
        #record.unit_value = self.get_unit_price(opitem) # こっちはaltairで実際に販売した単価(おおよそ (altairでは席の単価は厳密には出せない))
        record.processed_at = time.strftime('%Y%m%d%H%M%S')
        record.achievement_status = str(AugusSeatStatus.get_status(stock_info.seat))
        return record

    def export_from_augus_performance(self, augus_performance):
        augus_account = self.session.query(
            AugusAccount
        ).filter(
            AugusAccount.id == augus_performance.augus_account_id
        ).one()
        use_numbered_ticket_format = augus_account.use_numbered_ticket_format if augus_account else False

        res = AchievementWithNumberedTicketResponse() if use_numbered_ticket_format else AchievementResponse()
        res.event_code = augus_performance.augus_event_code
        res.date = augus_performance.start_on
        unless_status = [SeatStatusEnum.InCart.v, SeatStatusEnum.NotOnSale.v, SeatStatusEnum.Vacant.v, SeatStatusEnum.Canceled.v]
        # 自由席はSeat, AugusSeatを作らないのでここでは取得されない。ここで取得されるのは指定席のみ
        seats = self.session.query(
            Seat
        ).join(
            SeatStatus,
            AugusStockInfo,
            AugusPerformance
        ).filter(
            AugusPerformance.id == augus_performance.id
        ).filter(
            ~SeatStatus.status.in_(unless_status)
        ).all()

        for seat in seats:
            record = self.create_record(seat, seat_status_checked=True,
                                        use_numbered_ticket_format=use_numbered_ticket_format)
            if record:
                res.append(record)

        # 自由席の販売実績連携
        orders_of_unreserved_seat = self.__get_orders_of_unreserved_seat(augus_account, augus_performance)
        for order in orders_of_unreserved_seat:
            map(lambda ordered_product: res.append(
                self.__create_record_of_unreserved_seat(augus_performance,
                                                        order,
                                                        ordered_product,
                                                        use_numbered_ticket_format=use_numbered_ticket_format)),
                order.items)

        return res

    def __get_orders_of_unreserved_seat(self, augus_account, augus_performance):
        if not augus_account.enable_unreserved_seat:
            return []

        # 自由席のAugusStockInfoは席種コード単位で生成されるため、配券済のAugusTicketは席種コードで一意に特定できる想定
        sub_query = self.session.query(
            AugusTicket.id,
            AugusTicket.augus_seat_type_code
        )\
            .join(AugusStockInfo, AugusStockInfo.augus_ticket_id == AugusTicket.id)\
            .filter(AugusTicket.augus_performance_id == augus_performance.id,
                    AugusTicket.augus_seat_type_classif == SeatTypeClassif.FREE.value.decode(),
                    AugusStockInfo.seat_type_classif == SeatTypeClassif.FREE.value.decode())\
            .subquery('augus_ticket_distributed')
        augus_ticket_distributed = aliased(AugusTicket, sub_query)

        orders = self.session.query(Order)\
            .join(OrderedProduct)\
            .join(Product,
                  Product.id == OrderedProduct.product_id)\
            .join(AugusTicket,
                  AugusTicket.id == Product.augus_ticket_id)\
            .join(augus_ticket_distributed,
                  augus_ticket_distributed.augus_seat_type_code == AugusTicket.augus_seat_type_code)\
            .join(AugusStockInfo,
                  AugusStockInfo.augus_ticket_id == augus_ticket_distributed.id) \
            .options(contains_eager(Order.items, OrderedProduct.product,
                                    Product.augus_ticket, AugusTicket.augus_stock_infos,
                                    AugusStockInfo.augus_ticket)) \
            .filter(Order.performance_id == augus_performance.performance_id,
                    Order.canceled_at.is_(None),
                    Order.refunded_at.is_(None),
                    AugusTicket.augus_seat_type_classif == SeatTypeClassif.FREE.value.decode(),
                    AugusStockInfo.seat_type_classif == SeatTypeClassif.FREE.value.decode())\
            .all()

        return orders if orders else []

    def seat2opitem(self, seat):
        try:
            opitem = self.session.query(OrderedProductItem).join(
                orders_seat_table, orders_seat_table.c.OrderedProductItem_id == OrderedProductItem.id
            ).join(
                OrderedProduct,
                Order
            ).filter(
                Order.canceled_at.is_(None)
            ).filter(
                orders_seat_table.c.seat_id == seat.id
            ).one()
        except NoResultFound:
            return None

        return opitem

    @staticmethod
    def get_unit_price(opitem):
        return opitem.price / len(opitem.seats)

    @staticmethod
    def get_order_no(opitem):
        return opitem.ordered_product.order.order_no

    @staticmethod
    def get_order(opitem):
        if opitem:
            return opitem.ordered_product.order
        else:
            return None

    def get_target_augus_performances(self, augus_account_id, all_):
        from datetime import timedelta
        # TKT-6488 パフォーマンスが終了していない期間だけ販売実績を送る
        qs = self.session.query(AugusPerformance).join(AugusPerformance.performance) \
            .filter(AugusPerformance.augus_account_id == augus_account_id) \
            .filter(
                sa.func.IF(
                    Performance.end_on == None,
                    Performance.start_on >= self.now + timedelta(days=-1),
                    Performance.end_on >= self.now + timedelta(days=-1)
                )
            )

        if not all_:
            qs = qs.filter(AugusPerformance.is_report_target == True)
        else:
            qs = qs.filter(AugusPerformance.stoped_at.is_(None))

        ag_performances = qs.all()
        return ag_performances
