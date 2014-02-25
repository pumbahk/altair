#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import shutil
import logging
import argparse
from altair.augus.protocols import PerformanceSyncRequest
from altair.augus.parsers import AugusParser
from pyramid.paster import bootstrap
import transaction
from ..importers import AugusPerformanceImpoter
from ..errors import AugusDataImportError

logger = logging.getLogger(__name__)

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def import_performance_all(settings):
    rt_staging = settings['rt_staging']
    rt_pending = settings['rt_pending']
    ko_staging = settings['ko_staging']

    mkdir_p(rt_staging)
    mkdir_p(rt_pending)
    mkdir_p(ko_staging)

    importer = AugusPerformanceImpoter()
    target = PerformanceSyncRequest
    paths = []
    try:
        for name in filter(target.match_name, os.listdir(rt_staging)):
            try:
                logger.info('start import augus performance: {}'.format(name))
                path = os.path.join(rt_staging, name)
                paths.append(path)
                request = AugusParser.parse(path)
                importer.import_(request)
            except AugusDataImportError as err:
                logger.error('Illegal AugusPerformance Format: {}: {}'.format(path, repr(err)))
                raise
            except Exception as err:
                logger.error('AugusPerformance Cannot Import: {}: {}'.format(path, repr(err)))
                raise
    except:
        transaction.abort()
        raise
    else:
        transaction.commit()
        for path in paths:
            shutil.move(path, rt_pending)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    env = bootstrap(args.conf)
    settings = env['registry'].settings
    import_performamce_all(settings)

if __name__ == '__main__':
    main()
