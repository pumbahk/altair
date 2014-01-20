#-*- coding: utf-8 -*-
from altair.app.ticketing.core.models import (
    AugusPerformance,
    AugusVenue,
    )
from .errors import AugusDataImportError

class AugusPerformanceImpoter(object):
    def import_record(self, record):
        """
        record.event_code
        record.performance_code
        record.venue_code
        record.venue_name
        record.event_name
        record.performance_name
        record.date
        record.open_on
        record.start_on
        record.venue_version
        """
        
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
        ag_performances = []
        for record in records:
            ag_performance = self.import_record(record)
            ag_performances.append(ag_performance)
        return ag_performances

    def import_(self, protocol):
        return self.import_record_all(protocol)

