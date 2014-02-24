#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import time
import logging
import argparse
from pyramid.paster import bootstrap
import transaction
from altair.augus.exporters import AugusExporter
from altair.augus.parsers import AugusParser
from altair.augus.protocols import AchievementRequest
from altair.app.ticketing.core.models import AugusPerformance
from ..exporters import AugusAchievementExporter


logger = logging.getLogger(__name__)

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    parser.add_argument('--force', action='store_true', default=False)
    args = parser.parse_args()
    env = bootstrap(args.conf)
    settings = env['registry'].settings

    consumer_id = int(settings['augus_consumer_id'])
    ko_staging = settings['ko_staging']

    mkdir_p(ko_staging)

    exporter = AugusAchievementExporter()
    ag_performances = AugusPerformance.query
    if not args.force:
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
    transaction.commit()

if __name__ == '__main__':
    main()
