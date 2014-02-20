#-*- coding: utf-8 -*-
import os
import time
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
    DistributionSyncResponse,
    AchievementResponse,
    )
from altair.augus.exporters import AugusExporter
from .errors import (
    AugusDataExportError,
    )



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
            response.start_on = response[0].start_on
            resfile_path = os.path.join(path, response.name)
            AugusExporter.export(response, resfile_path)
        return responses

class AugusAchievementExporter(object):
    def create_record(self, stock_info):
        opitem = self.seat2opitem(stock_info.seat)
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
        res = AchievementResponse()
        res.event_code = augus_performance.augus_event_code
        res.date = augus_performance.start_on
        stock_infos = AugusStockInfo\
            .query\
            .filter(AugusStockInfo.augus_performance_id==augus_performance.id)\
            .filter(AugusStockInfo.putbacked_at!=None)\
            .all()

        for stock_info in stock_infos:
            # 未販売は出力しない
            if stock_info.seat.status in [SeatStatusEnum.NotOnSale.v, SeatStatusEnum.Vacant.v]:
                continue
            record = self.create_record(stock_info)
            res.append(record)
        return res



    def export_from_augus_event_code(self, augus_event_code):
        augus_performances = AugusPerformance\
            .query\
            .filter(AugusPerformance.augus_event_code==augus_event_code)\
            .all()
        res = AchievementResponse()
        res.event_code = augus_event_code

        if augus_performances:
            res.date = augus_performances[0].start_on

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
