#-*- coding: utf-8 -*-
import os
import datetime
import itertools
from StringIO import StringIO
from altair.app.ticketing.core.models import (
    Seat,
    Venue,
    Event,
    Performance,
    Stock,
    StockHolder,
    OrderedProductItem,
    AugusPerformance,
    AugusVenue,
    AugusTicket,
    AugusPutback,
    AugusSeat,
    AugusStockInfo,
    SeatStatusEnum,
    AugusSeatStatus,
    AugusPerformance,
    orders_seat_table,
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
    AchievementResponse,
    )
from altair.augus.exporters import AugusExporter
from .errors import (
    AugusDataExportError,
    )


class AugusPutbackExporter(object):
    def create_record(self, ag_putback):
        ag_stock_info = ag_putback.augus_stock_info
        ag_seat = ag_stock_info.augus_seat
        ag_performance = ag_stock_info.augus_performance
        seat = ag_putback.seat
        stock = seat.stock
        stock_type = stock.stock_type

        ag_ticket = AugusTicket.query.filter(AugusTicket.stock_type_id==stock_type.id).first()
        if not ag_ticket:
            raise AugusDataExportError('Stock type unlinked: StockType.id={}'.format(stock_type.id))

        record = PutbackResponseRecord()
        record.event_code = ag_performance.augus_event_code
        record.performance_code = ag_performance.augus_performance_code
        record.distribution_code = ag_stock_info.augus_distribution_code
        record.putback_code = ag_putback.augus_putback_code
        record.seat_type_code = ag_ticket.augus_seat_type_code
        record.unit_value_code = ag_ticket.unit_value_code
        record.date = ag_performance.start_on.strftime(DateType.FORMAT)
        record.start_on = ag_performance.start_on.strftime(HourMinType.FORMAT)
        record.block = ag_seat.block
        record.coordy = ag_seat.coordy
        record.coordx = ag_seat.coordx
        record.coordy_whole = ag_seat.coordy_whole
        record.coordx_whole = ag_seat.coordx_whole
        record.area_code = ag_seat.area_code
        record.info_code = ag_seat.info_code
        record.floor = ag_seat.floor
        record.column = ag_seat.column
        record.number = ag_seat.num
        record.seat_type_classif = ag_ticket.augus_seat_type_classif
        record.seat_count = ag_stock_info.quantity
        record.putback_status = ag_putback.putback_status
        record.putback_type = ag_putback.augus_putback_type
        return record

    def create_responses(self, putbacks=[]):
        if not putbacks:
            putbacks = AugusPutback.query.filter(AugusPutback.notified_at==None)\
                                         .filter(AugusPutback.reserved_at!=None)\
                                         .all()

        responses = []
        for event_code, putbacks_in_event in itertools.groupby(putbacks, lambda putback: putback.augus_stock_info.augus_performance.augus_event_code):
            response = PutbackResponse()
            response.event_code = event_code
            response.extend([self.create_record(putback) for putback in putbacks_in_event])
            responses.append(response)

        now = datetime.datetime.now()
        for putback in putbacks:
            putback.notified_at = now
            putback.save()
        return responses

    def export(self, path, customer_id):
        responses = self.create_responses()
        for response in responses:
            response.customer_id = customer_id
            resfile_path = os.path.join(path, response.name)
            AugusExporter.export(response, resfile_path)
        return responses

class AugusAchievementExporter(object):
    def create_record(self, stock_info):
        opitem = self.seat2opitem(stock_info.seat)
        record = AchievementResponse.record()
        record.event_code = stock_info.augus_performance.augus_event_code
        record.performance_code = stock_info.augus_performance.augus_performance_code
        record.trader_code = 1 # 業者コード
        record.distribution_code = stock_info.augus_distribution_code
        record.seat_type_code = stock_info.augus_ticket.augus_seat_type_code
        record.unit_value_code = stock_info.augus_ticket.unit_value_code
        record.date = stock_info.augus_performance.start_on
        record.start_on = stock_info.augus_performance.start_on
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
        record.unit_value = self.get_unit_price(opitem)
        record.processed_at = datetime.datetime.now()
        record.achievement_status = str(AugusSeatStatus.get_status(stock_info.seat))
        return record

    def export_from_augus_event_code(self, augus_event_code):
        augus_performances = AugusPerformance\
            .query\
            .filter(AugusPerformance.augus_event_code==augus_event_code)\
            .all()
        res = AchievementResponse()
        res.event_code = augus_event_code
        for ag_performance in augus_performances:
            stock_infos = AugusStockInfo\
                .query\
                .filter(AugusStockInfo.augus_performance_id==ag_performance.id)\
                .all()

            for stock_info in stock_infos:
                # 未販売は出力しない
                if stock_info.seat.status in [SeatStatusEnum.NotOnSale.v, SeatStatusEnum.Vacant.v]:
                    continue
                record = self.create_record(stock_info)
                res.append(record)
        return res


    # def create_record(self):
    #     ag_stock_info = ag_putback.augus_stock_info
    #     ag_seat = ag_stock_info.augus_seat
    #     ag_performance = ag_stock_info.augus_performane
    #     seat = ag_putback.seat
    #     stock = seat.stock
    #     stock_type = stock.stock_type
    #     ag_ticket = AugusTicket.get(stock_type_id=stock_type.id)

    #     if not ag_ticket:
    #         raise AugusDataExportError('Stock type unlinked: StockType.id={}'.format(stock_type.id))

    #     record = PutbackResponseRecord()
    #     record.event_code = ag_performance.augus_event_code
    #     record.performance_code = ag_performance.augus_performance_code
    #     record.distribution_code = ag_stock_info.augus_distribution_code
    #     record.putback_code = ag_putback.augus_putback_code
    #     record.seat_type_code = ag_ticket.augus_seat_type_code
    #     record.unit_value_code = ag_ticket.unit_value_code
    #     record.date = ag_performance.start_on # record側で日付にformatting
    #     record.start_on = ag_performance.start_on
    #     record.block = ag_seat.block
    #     record.coordy = ag_seat.coordy
    #     record.coordx = ag_seat.coordx
    #     record.coordy_whole = ag_seat.coordy_whole
    #     record.coordx_whole = ag_seat.coordx_whole
    #     record.area_code = ag_seat.area_code
    #     record.info_code = ag_seat.info_code
    #     record.floor = ag_seat.floor
    #     record.column = ag_seat.column
    #     record.number = ag_seat.num
    #     record.seat_type_classif = ag_ticket.augus_seat_type_classif
    #     record.seat_count = ag_stock_info.quantity
    #     record.putback_status = ag_putback.putback_status
    #     record.putback_type = ag_putback.augus_putback_type
    #     return record

    # def create_response(self, putbacks=[]):
    #     response = PutbackResponse()
    #     if not putbacks:
    #         putbacks = AugusPutback.query.filter(AugusPutback.nortificated_at==None).all()
    #     response.extend([self.create_record(putback) for putback in putbacks])

    # def export(self, path, request):
    #     response = AchievementResponse()
    #     for record in request:
    #         ag_performance = AugusPerformance.get(augus_event_code=record.event_code,
    #                                               augus_performance_code=record.performance_code,
    #                                               )
    #         if not ag_performance:
    #             raise AugusDataExportError(
    #                 'AugusPerformance not found: event_code={} performance_code={}'\
    #                 .format(record.event_code, record.performance_code))

    #         for ag_stock_info in ag_performance.augus_stock_infos:
    #             ag_seat = ag_stock_info.ag_seat
    #             ag_ticket = ag_stock_info.get_augus_ticket()
    #             if ag_ticket:
    #                 raise AugusDataExportError(
    #                     'AugusStockInfo is not linked: AugusStockInfo.id={}'\
    #                     .format(ag_stock_info.id))
    #             seat = ag_stock_info.get_seat()
    #             opitem = self.seat2opitem(seat)
    #             res_record = respnse.record()
    #             res_record.event_code = ag_performance.augus_event_code
    #             res_record.performance_code = ag_performance.augus_performance_code
    #             res_record.trader_code = 1 # 業者コード
    #             res_record.distribution_code = ag_stock_info.augus_distribution_code
    #             res_record.seat_type_code = ag_ticket.augus_seat_type_code
    #             res_record.unit_value_code = ag_ticekt.unit_value_code
    #             res_record.date = ag_performance.date
    #             res_record.start_on = ag_performance.start_on
    #             res_record.reservation_number = self.get_order_no(opitem)
    #             res_record.block = ag_seat.block
    #             res_record.coordy = ag_seat.coordy
    #             res_record.coordx = ag_seat.coordx
    #             res_record.area_code = ag_seat.area_code
    #             res_record.info_code = ag_seat.info_code
    #             res_record.floor = ag_seat.floor
    #             res_record.column = ag_seat.column
    #             res_record.number = ag_seat.num
    #             res_record.seat_type_classif = ag_stock_info.augus_seat_type_classif
    #             res_record.seat_count = ag_stock_info.quantity
    #             res_record.unit_value = self.get_unit_price(opitem)
    #             res_record.processed_at = datetime.datetime.now()
    #             res_record.achievement_status = AugusSeatStatus.get_status(seat)
    #             response.append(res_record)
    #     response.customer_id = customer_id
    #     AugusExporter.export(response, path)
    #     return response

    @staticmethod
    def seat2opitem(seat):
        qs = orders_seat_table.select(whereclause='seat_id={}'.format(seat.id))
        da = qs.execute()
        seatid_opitemid =da.fetchall()
        if len(seatid_opitemid) != 1:
            return None
        else:
            opitem_id = seatid_opitemid[0][1]
            return OrderedProductItem.get(opitem_id)

    @staticmethod
    def get_unit_price(opitem):
        return opitem.price / len(opitem.seats)

    @staticmethod
    def get_order_no(opitem):
        return opitem.ordered_product.order.order_no
