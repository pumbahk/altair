#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import argparse
from altair.augus.protocols import TicketSyncRequest
from altair.augus.parsers import AugusParser
from pyramid.paster import bootstrap
import transaction
from ..importers import AugusTicketImpoter
from ..errors import AugusDataImportError


def get_settings(env=None):
    if env:
        return env['registry'].settings
    else: # DEBUG
        from pit import Pit
        return Pit.get('augus_ftp',
                       {'require': {'staging': '',
                                    'pending': '',
                                }})

def init_env(conf):
    env = None
    if conf:
        env = bootstrap(conf)
    settings = get_settings(env)
    staging = settings['to_staging']
    pending = settings['to_pending']
    mkdir_p(staging)
    mkdir_p(pending)
    return staging, pending


def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    staging, pending = init_env(args.conf)
    
    importer = AugusTicketImpoter()
    target = TicketSyncRequest
    paths = []
    try:
        for name in filter(target.match_name, os.listdir(staging)):
            path = os.path.join(staging, name)
            paths.append(path)
            request = AugusParser.parse(path)
            importer.import_(request)
    except AugusDataImportError as err:
        transaction.abort()        
        raise
    except:
        transaction.abort()
        raise
    else:
        transaction.commit()

    for path in paths:
        shutil.move(path, pending)
if __name__ == '__main__':
    main()
