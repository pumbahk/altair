#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import shutil
import logging
import argparse
import transaction
from pyramid.paster import (
    bootstrap,
    setup_logging,
    )
from pyramid.renderers import render_to_response
from altair.app.ticketing.core.models import (
    Mailer,
    AugusPerformance,
    )
from altair.augus.protocols import PerformanceSyncRequest
from altair.augus.parsers import AugusParser
from ..importers import AugusPerformanceImpoter
from ..errors import AugusDataImportError
from .. import multilock

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
    augus_performance_ids = []

    try:
        for name in filter(target.match_name, os.listdir(rt_staging)):
            try:
                logger.info('start import augus performance: {}'.format(name))
                path = os.path.join(rt_staging, name)
                paths.append(path)
                request = AugusParser.parse(path)
                augus_performances = importer.import_(request)
                augus_performance_ids.extend([agp.id for agp in augus_performances])
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
    return augus_performance_ids

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    setup_logging(args.conf)
    env = bootstrap(args.conf)
    settings = env['registry'].settings
    augus_performance_ids = []

    try:
        with multilock.MultiStartLock('augus_performance'):
            augus_performance_ids = import_performance_all(settings)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))
        return

    if len(augus_performance_ids) == 0:
        return

    sender = settings['mail.augus.sender']
    recipient = settings['mail.augus.recipient']
    augus_performances = AugusPerformance.query.filter(AugusPerformance.id.in_(augus_performance_ids)).all()
    mailer = Mailer(settings)

    params = {'augus_performances': augus_performances,
              }
    body = render_to_response('altair.app.ticketing:templates/cooperation/augus/mails/augus_performance.html', params)

    mailer.create_message(
        sender=sender,
        recipient=recipient,
        subject=u'【オーガス連携】公演連携のお知らせ',
        body=body.text,
        )
    mailer.send(sender, [recipient])


if __name__ == '__main__':
    main()
