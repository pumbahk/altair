#-*- coding: utf-8 -*-
from altair.app.ticketing.core.models import (
    AugusPerformance,
    AugusVenue,
    AugusTicket,
    )
from .errors import AugusDataImportError

class AugusPerformanceImpoter(object):
    def import_record(self, record):
        ag_venue = AugusVenue\
            .query.filter(AugusVenue.code==record.venue_code)\
                  .filter(AugusVenue.version==record.venue_version)\
                  .first()
        if not ag_venue:
            raise AugusDataImportError('Cannot import augus performance: '
                                       'no such AugusVenue: '
                                       'code={} version={}'.format(record.venue_code, record.venue_version)
                                       )
        
        ag_performance = AugusPerformance.query.get(augus_event_code=record.event_code,
                                                    augus_performance_code=record.performance_code,
                                                    )
        if not ag_performance:
            ag_performance = AugusPerformance()
            ag_performance.augus_event_code = record.event_code,
            ag_performance.augus_performance_code = record.performance_code
        ag_performance.augus_venue_code = record.venue_code
        ag_performance.augus_venue_name = record.venue_name
        ag_performance.augus_event_name = record.event_name
        ag_performance.augus_performance_name = record.performance_name
        ag_performance.open_on = record.open_on_datetime
        ag_performance.start_on = record.start_on_datetime
        ag_performance.augus_venue_version = record.venue_version
        ag_performance.save()
        return ag_performance
        
    def import_record_all(self, records):
        elms = []
        for record in records:
            elm = self.import_record(record)
            elms.append(elm)
        return elms

    def import_(self, protocol):
        return self.import_record_all(protocol)

class AugusTicketImpoter(object):
    def import_record(self, record):
        ag_ticket = AugusTicket.get(augus_event_code=record.event_code,
                                    augus_performance_code=record.performance_code,
                                    augus_seat_type_code=record.seat_type_code,
                                    )
        ag_performance = None
        if not ag_ticket:
            ag_ticket = AugusTicket()
            ag_performance = AugusPerformance.get(augus_event_code=record.event_code,
                                                  augus_performance_code=record.performance_code,
                                                  )
            if not ag_performance:
                raise AugusDataImportError('AugusPerformance not found: event_code={} performance_code'.format(
                    record.event_code, record.performance_code))
        else:
            ag_performance = ag_ticket.ag_performance
        ag_ticket.augus_venue_code = record.venue_code
        ag_ticket.seat_type_code = record.seat_type_code
        ag_ticket.seat_type_name = record.seat_type_name
        ag_ticket.unit_value_name = record.unit_value_name
        ag_ticket.augus_seat_type_classif = record.seat_type_classif
        ag_ticket.avlue = record.value
        ag_ticket.augus_performance_id = ag_performance.id
        ag_ticket.save()
        return ag_ticket
        
        
    def import_record_all(self, records):
        elms = []
        for record in records:
            elm = self.import_record(record)
            elms.append(elm)
        return elms

    def import_(self, protocol):
        return self.import_record_all(protocol)


class AugusDistributionImpoter(object):
    def import_record(self, record):
        ag_ticket = AugusTicket.get(augus_event_code=record.event_code,
                                    augus_performance_code=record.performance_code,
                                    augus_seat_type_code=record.seat_type_code,
                                    )
        ag_performance = None
        if not ag_ticket:
            ag_ticket = AugusTicket()
            ag_performance = AugusPerformance.get(augus_event_code=record.event_code,
                                                  augus_performance_code=record.performance_code,
                                                  )
            if not ag_performance:
                raise AugusDataImportError('AugusPerformance not found: event_code={} performance_code'.format(
                    record.event_code, record.performance_code))
        else:
            ag_performance = ag_ticket.ag_performance
        ag_ticket.augus_venue_code = record.venue_code
        ag_ticket.seat_type_code = record.seat_type_code
        ag_ticket.seat_type_name = record.seat_type_name
        ag_ticket.unit_value_name = record.unit_value_name
        ag_ticket.augus_seat_type_classif = record.seat_type_classif
        ag_ticket.avlue = record.value
        ag_ticket.augus_performance_id = ag_performance.id
        ag_ticket.save()
        return ag_ticket
        
        
    def import_record_all(self, records):
        elms = []
        for record in records:
            elm = self.import_record(record)
            elms.append(elm)
        return elms

    def import_(self, protocol):
        return self.import_record_all(protocol)

