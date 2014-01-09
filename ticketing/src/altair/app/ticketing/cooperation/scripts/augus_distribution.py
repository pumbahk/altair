#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import time
import itertools
import transaction
import logging
from pyramid.paster import bootstrap
from altair.app.ticketing.core.models import (
    Performance,
    StockHolder,
    AugusPerformance,
    AugusSeat,
    AugusVenue,
    )
from altair.augus.protocols import (
    DistributionSyncRequest,
    DistributionSyncResponse,
    )
from altair.augus.parsers import AugusParser
from .utils import (
    mkdir_p,
    get_argument_parser,
    get_settings,
    )
logger = logging.getLogger()

class Importer(object):
    def import_(self, record):
        ap = AugusPerformance.query\
                .filter(AugusPerformance.event_code==record.event_code)\
                .filter(AugusPerformance.code==record.performance_code)\
                .one() # no exist error
        performance = ap.performance
        event = performance.event
        if not performance:
            raise 'NO PERFORMANCE'
        stock_holder = StockHolder()
        stock_holder
        style = '{"text": "\u8ffd", "text_color": "#a62020"}'

def main():
    parser = get_argument_parser()
    args = parser.parse_args()
    bootstrap(args.conf)    
    settings = get_settings(args.conf)
    staging = settings['staging']
    pending = settings['pending']
    
    mkdir_p(staging)
    mkdir_p(pending)
    _get_key = lambda rec: (rec.event_code, rec.performance_code)
    cannot_distributes = []
    
    for name in filter(DistributionSyncRequest.match_name, os.listdir(staging)):
        path = os.path.join(staging, name)
        request = AugusParser.parse(path)
        records = sorted(request, key=lambda rec: _get_key)
        for (ag_event_code, ag_performance_code), recs in itertools.groupby(records, _get_key):
            ap = AugusPerformance.query\
                     .filter(AugusPerformance.augus_event_code==ag_event_code)\
                     .filter(AugusPerformance.code==ag_performance_code)\
                     .one() # raise no exist error
            if not ap.performance:
                raise ValueError('No link to performance: AugusPerformance.code={}'\
                                 .format(ap.code))
            stock_holder = StockHolder()
            stock_holder.name = u'オーガス連携:' + time.strftime('%Y-%m-%d-%H-%M-%S')
            stock_holder.event_id = ap.performance.event.id
            stock_holder.stype = u'{"text": "\u8ffd", "text_color": "#a62020"}'
            stock_holder.account_id = 35
            stock_holder.save()
            
            for rec in recs:
                augus_venue = AugusVenue.query.filter(AugusVenue.venue_id==rec.venue_code).one()
                augus_seat = AugusSeat.query\
                                 .filter(AugusSeat.augus_venue_id==augus_venue.id)\
                                 .filter(AugusSeat.area_code==rec.area_code)\
                                 .filter(AugusSeat.info_code==rec.info_code)\
                                 .filter(AugusSeat.floor==rec.floor.decode('sjis'))\
                                 .filter(AugusSeat.column==rec.column==rec.column.decode('sjis'))\
                                 .filter(AugusSeat.number==rec.number.decode('sjis'))\
                                 .one()
                seat = Seat.query\
                           .filter(Seat.l0_id==augus_seat.seat.l0_id)\
                           .filter(Seat.venue_id==ap.performance.venue.id)\
                           .one()
                stock = seat.stock
                if stock.stock_holder_id is None:
                    stock.stock_holder_id = stock_holder.id
                    stock.save()
                else:
                    cannot_distributes.append(augus_seat)
    if cannot_distributes:
        transaction.abort()
        logger.warn('Cannot distribute seats: Seats are {}'.format(
            [unicode(augus_seat).encode('utf8') for augus_seat in cannot_distributes]))
    else:
        transaction.commit()

if __name__ == '__main__':
    main()
