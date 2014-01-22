#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import argparse
from altair.augus.parsers import AugusParser
from pyramid.paster import bootstrap
import transaction
from ..exporters import AugusAchievementExporter
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
    staging = settings['from_staging']
    pending = siettings['from_pending']
    mkdir_p(staging)
    mkdir_p(pending)
    return staging, pending


def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

CUSTOMER_ID = 12345678

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    staging, pending = init_env(args.conf)
    exporter = AugusAchievementExporter()
    try:
        request = exporter.export(staging, CUSTOMER_ID)
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
