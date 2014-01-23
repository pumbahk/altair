#! /usr/bin/env python
#-*- coding: utf-8 -*-
import shutil
import argparse
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

def mkdir_p(path):
    try:
        shutil.makedirs(path)
    except (IOError, OSError):
        pass
        
class Exporter(list):
    def export(self, path):
        mkdir_p(path)


def create_venue_data():
    request = VenueSyncRequest(customer_id=123456789, venue_code=1)
    for ii in range(100):
        record = request.record()
        record.venue_code = 1
        record.venue_name = u'会場名'
        record.area_name = u'エリア名'
        record.info_name = u'付加情報名'
        record.doorway_name = u'出入り口名'
        record.priority = 1
        record.floor = 1
        record.column = 1
        record.number = ii
        record.block = 1
        record.coordy = 1
        record.coordx = 1
        record.coordy_whole = 1
        record.coordx_whole = 1
        record.area_code = 1
        record.info_code = 1
        record.doorway_code = 1
        record.venue_version = 1
        request.append(record)

    AugusExporter.export(request, request.name)


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

