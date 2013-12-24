#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import argparse
from altair.augus.protocols import (
    DistributionSyncRequest,
    DistributionSyncResponse,
    )
from altair.augus.parsers import AugusParser

def get_settings(conf=None): 
    if conf:
        raise NotImplementedError()
    else:
        from pit import Pit
        return Pit.get('augus_ftp',
                       {'require': {'staging': '',
                                    'pending': '',
                                    }})
def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', default=None)
    args = parser.parse_args()
    settings = get_settings(args.conf)
    staging = settings['staging']
    pending = settings['pending']
    
    mkdir_p(staging)
    mkdir_p(pending)

    for name in filter(DistributionSyncRequest.match_name, os.listdir(staging)):
        path = os.path.join(staging, name)
        request = AugusParser.parse(path)
        for record in request:
            pass
if __name__ == '__main__':
    main()
