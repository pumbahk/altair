#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import argparse
from altair.augus.protocols import TicketSyncRequest
from altair.augus.parsers import AugusParser
from pyramid.paster import bootstrap
import transaction
from ..exporters import AugusPutbackExporter
from ..errors import AugusDataImportError
from .. import multilock


def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def export_putback_all(settings):
    consumer_id = int(settings['augus_consumer_id'])
    rt_staging = settings['rt_staging']
    rt_pending = settings['rt_pending']
    ko_staging = settings['ko_staging']

    mkdir_p(rt_staging)
    mkdir_p(rt_pending)
    mkdir_p(ko_staging)

    exporter = AugusPutbackExporter()
    try:
        request = exporter.export(ko_staging, consumer_id)
    except AugusDataImportError as err:
        transaction.abort()
        raise
    except:
        transaction.abort()
        raise
    else:
        transaction.commit()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    env = bootstrap(args.conf)
    settings = env['registry'].settings


    try:
        with multilock.MultiStartLock('augus_putback'):
            export_putback_all(settings)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))


if __name__ == '__main__':
    main()
