#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import shutil
import logging
import argparse
from altair.augus.protocols import TicketSyncRequest
from altair.augus.parsers import AugusParser
from pyramid.paster import bootstrap
import transaction
from ..importers import AugusTicketImpoter
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

    rt_staging = settings['rt_staging']
    rt_pending = settings['rt_pending']
    ko_staging = settings['ko_staging']

    mkdir_p(rt_staging)
    mkdir_p(rt_pending)
    mkdir_p(ko_staging)

    importer = AugusTicketImpoter()
    target = TicketSyncRequest
    paths = []
    try:
        for name in filter(target.match_name, os.listdir(rt_staging)):
            logger.info('start import AugusTicket: {}'.format(name))
            try:
                path = os.path.join(rt_staging, name)
                paths.append(path)
                request = AugusParser.parse(path)
                importer.import_(request)
            except AugusDataImportError as err:
                logger.error('Illegal AugusTIcket format: {}: {}'.format(path, repr(err)))
                raise
            except Exception as err:
                logger.error('AugusTicket cannot import: {}: {}'.format(path, repr(err)))
                raise
    except:
        transaction.abort()
        raise
    else:
        transaction.commit()
        for path in paths:
            shutil.move(path, rt_pending)

if __name__ == '__main__':
    main()
