#! /usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import os
import time
import traceback
import shutil
import logging
import argparse
from altair.augus.types import Status
from altair.augus.exporters import AugusExporter
from altair.augus.protocols import (
    DistributionSyncRequest,
    DistributionSyncResponse,
    )
from altair.augus.parsers import AugusParser
from pyramid.paster import bootstrap
import transaction
from ..importers import AugusDistributionImporter
from ..exporters import AugusDistributionExporter
from ..errors import AugusDataImportError

logger = logging.getLogger(__name__)

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    env = bootstrap(args.conf)
    settings = env['registry'].settings

    consumer_id = int(settings['augus_consumer_id'])
    rt_staging = settings['rt_staging']
    rt_pending = settings['rt_pending']
    ko_staging = settings['ko_staging']

    mkdir_p(rt_staging)
    mkdir_p(rt_pending)
    mkdir_p(ko_staging)

    importer = AugusDistributionImporter()
    exporter = AugusDistributionExporter()
    target = DistributionSyncRequest

    for name in filter(target.match_name, os.listdir(rt_staging)):
        time.sleep(1.5) # ファイル名/StockHolder名が含む日時をずらす為sleepを入れる

        logger.info('start import augus distribution: {}'.format(name))
        path = os.path.join(rt_staging, name)
        status = Status.NG
        request = AugusParser.parse(path)
        try:
            importer.import_(request)
            status = Status.OK
            logger.info('augus distribution: OK: {}'.format(path))
        except AugusDataImportError as err:
            logger.error('Illegal AugusDistribution format: {}: {}'.format(path, repr(err)))
        except Exception as err:
            logger.error('AugusDisrtibution cannot import: {}: {}'.format(path, repr(err)))

        try:
            exporter.export(ko_staging, request, status)
            shutil.move(path, rt_pending)
        except Exception:
            transaction.abort()
            raise
        else:
            if status == Status.OK:
                transaction.commit()
            else:
                transaction.abort()

if __name__ == '__main__':
    main()
