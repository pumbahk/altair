#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import time
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
    target = DistributionSyncRequest
    request_success = []
    paths = []

    date = ''
    try:
        for name in filter(target.match_name, os.listdir(rt_staging)):
            try:
                logger.info('start import augus distribution: {}'.format(name))
                path = os.path.join(rt_staging, name)
                paths.append(path)
                request = AugusParser.parse(path)
                import pdb; pdb.set_trace()
                date = request.date
                success_records = importer.import_(request)
                request_success.append((request, success_records))
            except AugusDataImportError as err:
                logger.error('Illegal AugusDistribution format: {}: {}'.format(path, repr(err)))
                raise
            except Exception as err:
                logger.error('AugusDisrtibution cannot import: {}: {}'.format(path, repr(err)))
                raise
    except:
        transaction.abort()
        raise
    else:
        try:
            for request, success in request_success:
                response = DistributionSyncResponse(customer_id=consumer_id)
                import pdb; pdb.set_trace()
                response.date = date
                for record in request:
                    response.event_code = int(record.event_code)
                    res_record = response.record()
                    res_record.event_code = record.event_code
                    res_record.performance_code = record.performance_code
                    res_record.distribution_code = record.distribution_code
                    res_record.status = Status.OK.value if record in success else Status.NG.value
                    response.append(res_record)
                    name = response.name
                    path = os.path.join(ko_staging, name)
                    AugusExporter.export(response, path)
                time.sleep(2)
        except:
            transaction.abort()
            raise
        else:
            transaction.commit()
            for path in paths:
                shutil.move(path, rt_pending)

if __name__ == '__main__':
    main()
