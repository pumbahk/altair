#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import shutil
import argparse
import sqlalchemy as sa
import sqlalchemy.orm as orm
from pit import Pit
from altair.augus.exporters import AugusExporter
from altair.augus.protocols import (
    VenueSyncRequest,
    VenueSyncResponse,
    PerformanceSyncRequest,
    TicketSyncRequest,
    DistributionSyncRequest,
    DistributionSyncResponse,
    PutbackRequest,
    PutbackResponse,
    AchievementRequest,
    AchievementResponse,
    )

CUSTOMER_ID = 123456

def mkdir_p(path):
    try:
        os.makedirs(path)
    except (IOError, OSError):
        pass


def get_database(dbname):
    settings = Pit.get('database', {'require': {'username': '',
                                                'password': '',
                                                'dbengine': 'mysql',
                                                'driver': 'mysqldb',
                                                'host': 'localhost',
                                                }})
    account = settings['username']
    if settings['password']:
        account += ':' + settings['password']
    schema = settings['dbengine']
    if settings['driver']:
        schema += '+' + settings['driver']
    uri = '{}://{}@{}'.format(schema, account, settings['host'])
    engine = sa.create_engine(uri, pool_recycle=3600)
    connect = engine.connect()
    metadata = sa.MetaData(bind=engine)
    connect.execute('use {}'.format(dbname))
    return connect


def create_venue_data():
    connect = get_database('ticketing')
    get_venues = 'SELECT Venue.id, Site.name FROM Venue '\
                 'JOIN Site ON Site.id=Venue.site_id '\
                 'WHERE Venue.performance_id IS NULL '
    get_seats = 'SELECT Seat.id, Seat.name, Seat.seat_no, Seat.l0_id, Seat.group_l0_id, Seat.row_l0_id '\
                'FROM Seat WHERE Seat.venue_id={} '
    
    for venue_id, site_name in connect.execute(get_venues):
        site_name = site_name.decode('utf8') # Site.name is not unicode.
        request = VenueSyncRequest(customer_id=CUSTOMER_ID,
                                   venue_code=venue_id,
                                   )
        request.customer_id = CUSTOMER_ID
        request.venue_id = venue_id
        for s_id, s_name, s_no, s_l0_id, s_gl0_id, s_rl0_id in connect.execute(get_seats.format(venue_id)):
            s_name = s_name.decode('utf8') # Seat.name is not unicode
            record = request.record()
            record.venue_code = venue_id
            record.venue_name = site_name
            record.area_name = u'エリア-' + unicode(s_id)
            record.info_name = s_name
            record.doorway_name = u'出入口-' + unicode(s_id)
            record.priority = s_id
            record.floor = s_gl0_id
            record.column = s_rl0_id
            record.number = s_l0_id
            record.block = venue_id
            record.coordy = s_id + 1
            record.coordx = s_id + 2
            record.coordy_whole = s_id + 3
            record.coordx_whole = s_id + 4
            record.area_code = venue_id + 1
            record.info_code = venue_id + 2
            record.doorway_code = venue_id + 3
            record.venue_version = venue_id + 4
            request.append(record)
        export_dir = './data'
        mkdir_p(export_dir)
        try:
            AugusExporter.export(request, os.path.join(export_dir, request.name))
        except Exception as err:
            print 'NG: venue_id={}: {}'.format(venue_id, repr(err))

CMD_FUNC = {
    'venue': create_venue_data,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target')
    opts = parser.parse_args()

    func = CMD_FUNC[opts.target]
    print func()

if __name__ == '__main__':
    main()

