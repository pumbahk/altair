#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import argparse
import logging
import transaction
from pyramid.paster import (
    bootstrap,
    setup_logging,
    )
from pyramid.renderers import render_to_response
from altair.app.ticketing.core.models import (
    Mailer,
    AugusPutback,
    )
from altair.augus.protocols import TicketSyncRequest
from altair.augus.parsers import AugusParser
from altair import multilock
from ..operations import AugusOperationManager
from ..exporters import AugusPutbackExporter
from ..config import get_var_dir
from ..errors import (
    IllegalImportDataError,
    AugusDataImportError,
    )

logger = logging.getLogger(__name__)

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
    putback_codes = []
    try:
        responses = exporter.export(ko_staging, consumer_id)
        putback_codes = [res[0].putback_code for res in responses if len(res)]
    except AugusDataImportError as err:
        transaction.abort()
        raise
    except:
        transaction.abort()
        raise
    else:
        transaction.commit()
    return putback_codes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    setup_logging(args.conf)
    env = bootstrap(args.conf)
    settings = env['registry'].settings
    var_dir = get_var_dir(settings)
    mailer = Mailer(settings)
    mgr = AugusOperationManager(var_dir=var_dir)
    try:
        with multilock.MultiStartLock('augus_putback'):
            mgr.putback(mailer)
            putback_codes = export_putback_all(settings)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))

if __name__ == '__main__':
    main()
