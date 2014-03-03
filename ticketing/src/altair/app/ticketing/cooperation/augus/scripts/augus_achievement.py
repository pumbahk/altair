#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import time
import logging
import argparse
from pyramid.renderers import render_to_response
from pyramid.paster import bootstrap
import transaction
from altair.augus.exporters import AugusExporter
from altair.augus.parsers import AugusParser
from altair.augus.protocols import AchievementRequest
from altair.app.ticketing.core.models import (
    Mailer,
    AugusPerformance,
    )
from ..exporters import AugusAchievementExporter
from .. import multilock

logger = logging.getLogger(__name__)

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def export_achievement_all(settings, force=False):
    consumer_id = int(settings['augus_consumer_id'])
    ko_staging = settings['ko_staging']

    mkdir_p(ko_staging)

    ag_performance_ids = []
    exporter = AugusAchievementExporter()
    ag_performances = AugusPerformance.query
    if not force:
        ag_performances = ag_performances\
            .filter(AugusPerformance.is_report_target==True)
    for ag_performance in ag_performances.all():
        time.sleep(1.5)
        logger.info('Achievement export start: AugusPerformance.id={}'.format(ag_performance.id))
        res = exporter.export_from_augus_performance(ag_performance)
        res.customer_id = consumer_id
        path = os.path.join(ko_staging, res.name)
        logger.info('export: {}'.format(path))
        AugusExporter.export(res, path)
        ag_performance.is_report_target = False
        ag_performance.save()
        ag_performance_ids.append(ag_performance.id)
    transaction.commit()
    return ag_performance_ids


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    parser.add_argument('--force', action='store_true', default=False)
    args = parser.parse_args()
    env = bootstrap(args.conf)
    settings = env['registry'].settings

    ag_performance_ids = []
    try:
        with multilock.MultiStartLock('augus_achievement'):
            ag_performance_ids = export_achievement_all(settings, force=args.force)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))
        return

    sender = settings['mail.augus.sender']
    recipient = settings['mail.augus.recipient']

    mailer = Mailer(settings)

    augus_performances = AugusPerformance.query.filter(AugusPerformance.id.in_(ag_performance_ids)).all()
    params = {'augus_performances': augus_performances,
              }
    body = render_to_response('altair.app.ticketing:templates/cooperation/augus/mails/augus_achievement.html', params)

    mailer.create_message(
        sender=sender,
        recipient=recipient,
        subject=u'【オーガス連携】販売実績通知のお知らせ',
        body=body.text,
        )
    mailer.send(sender, [recipient])

if __name__ == '__main__':
    main()
