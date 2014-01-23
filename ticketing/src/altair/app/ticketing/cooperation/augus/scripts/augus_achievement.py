#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import argparse
from altair.augus.parsers import AugusParser
from altair.augus.protocols import AchievementRequest
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
    to_staging = settings['to_staging']
    to_pending = siettings['to_pending']
    from_staging = settings['from_staging']
    from_pending = siettings['from_pending']
    mkdir_p(to_staging)
    mkdir_p(to_pending)
    mkdir_p(from_staging)
    mkdir_p(from_pending)
    return to_staging, to_pending, from_staging, from_pending

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    to_staging, to_pending, from_staging, from_pending_= init_env(args.conf)
    exporter = AugusAchievementExporter()
    target = AchievementRequest
    try:
        for name in filter(target.match_name, os.listdir(staging)):
            path = os.path.join(staging, name)
            paths.append(path)
            request = AugusParser.parse(path)
            exporter.export(from_staging, request)
    except AugusDataImportError as err:
        transaction.abort()    
        raise
    except:
        transaction.abort()
        raise
    else:
        transaction.commit()
    for path in paths:
        shutil.move(path, to_pending)
    
if __name__ == '__main__':
    main()
