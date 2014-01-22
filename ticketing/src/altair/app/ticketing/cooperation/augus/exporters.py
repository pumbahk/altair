#-*- coding: utf-8 -*-
from StringIO import StringIO
from altair.app.ticketing.core.models import (
    AugusPutback,
    )
from altair.augus.protocols.putback import (
    PutbackResponseRecord,
    PutbackResponse,
    )
from altair.augus.exporters import AugusExporter
from .errors import (
    AugusDataExportError,
    )

class AugusPutbackExporter(object):
    def create_record(self, ag_putback):
        ag_stock_info = ag_putback.augus_stock_info
        ag_seat = ag_stock_info.augus_seat
        ag_performance = ag_stock_info.augus_performane
        seat = ag_putback.seat
        stock = seat.stock
        stock_type = stock.stock_type
        ag_ticket = AugusTicket.get(stock_type_id=stock_type.id)
        if not ag_ticket:
            raise AugusDataExportError('Stock type unlinked: StockType.id={}'.format(stock_type.id))
        
        record = PutbackResponseRecord()
        record.event_code = ag_performance.augus_event_code
        record.performance_code = ag_performance.augus_performance_code
        record.distribution_code = ag_stock_info.augus_distribution_code
        record.putback_code = ag_putback.augus_putback_code
        record.seat_type_code = ag_ticket.augus_seat_type_code
        record.unit_value_code = ag_ticket.unit_value_code
        record.date = ag_performance.start_on # record側で日付にformatting
        record.start_on = ag_performance.start_on
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
    
    def create_response(self, putbacks=[]):
        response = PutbackResponse()
        if not putbacks:
            putbacks = AugusPutback.query.filter(AugusPutback.nortificated_at==None).all()
        response.extend([self.create_record(putback) for putback in putbacks])

    def export(self, path, customer_id):
        response = self.create_response()
        response.customer_id = customer_id
        AugusExporter.export(response, path)
        return response
        
