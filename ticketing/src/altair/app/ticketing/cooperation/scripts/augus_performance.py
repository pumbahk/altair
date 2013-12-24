#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import argparse
from altair.augus.protocols import PerformanceSyncRequest
from altair.augus.parsers import AugusParser
from pyramid.paster import bootstrap
import transaction
from altair.app.ticketing.core.models import AugusPerformance


def get_settings(conf=None): 
    from pit import Pit
    return Pit.get('augus_ftp',
                   {'require': {'staging': '',
                                'pending': '',
                            }})
def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

class Importer(object):
    def import_(self, record):
        ap = AugusPerformance.get(code=record.performance_code) # ap = Augus Performance
        if not ap:
            ap = AugusPerformance()
        ap.code = record.performance_code
        ap.augus_event_code = record.event_code
        ap.save()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', default=None)
    args = parser.parse_args()
    env = bootstrap(args.conf)
    settings = get_settings(args.conf)
    staging = settings['staging']
    pending = settings['pending']
    mkdir_p(staging)
    mkdir_p(pending)
    print os.listdir(staging)
    importer = Importer()
    target = PerformanceSyncRequest
    try:
        for name in filter(target.match_name, os.listdir(staging)):
            path = os.path.join(staging, name)
            request = AugusParser.parse(path)
            for record in request:
                importer.import_(record)
                print 'IMPORT: AUGUS PERFORMANCE={}'.format(
                    record.performance_code)
    except:
        transaction.abort()
        raise
    else:
        transaction.commit()
    
if __name__ == '__main__':
    main()
