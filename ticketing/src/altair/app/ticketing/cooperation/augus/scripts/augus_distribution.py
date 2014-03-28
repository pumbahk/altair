#! /usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import os
import time
import traceback
import shutil
import logging
import argparse
from pyramid.renderers import render_to_response
from altair.app.ticketing.core.models import (
    Mailer,
    AugusPerformance,
    AugusStockDetail,
    )
from altair.augus.types import Status
from altair.augus.exporters import AugusExporter
from altair.augus.protocols import (
    DistributionSyncRequest,
    DistributionSyncResponse,
    )
from altair.augus.parsers import AugusParser
from pyramid.paster import (
    bootstrap,
    setup_logging,
    )
import transaction
from ..importers import AugusDistributionImporter
from ..exporters import AugusDistributionExporter
from ..errors import (
    IllegalImportDataError,
    AugusDataImportError,
    )
from .. import multilock

logger = logging.getLogger(__name__)

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

class DistributionExcutionError(Exception):
    pass



class AugusDistributionAdapter(object):
    def __init__(self):
        self.augus_performance = None
        self.augus_distribution_code = '-'
        self._count = 0

    @property
    def augus_event_name(self):
        return self.augus_performance.augus_event_name if self.augus_performance else u'事業コード: {}'.format(self.augus_event_code)

    @property
    def augus_performance_name(self):
        return self.augus_performance.augus_performance_name if self.augus_performance else u'公演コード: {}'.format(self.augus_performance_code)

    @property
    def augus_venue_name(self):
        return self.augus_performance.augus_venue_name if self.augus_performance else '-'

    @property
    def start_on(self):
        return self.augus_performance.start_on if self.augus_performance else '-'

    def load(self, event_code, performance_code, distribution_code):
        self.augus_performance = AugusPerformance\
            .query.filter(AugusPerformance.augus_event_code==event_code)\
                  .filter(AugusPerformance.augus_performance_code==performance_code)\
                  .first()
        if not self.augus_performance:
            self.augus_event_code = event_code
            self.augus_performance_code = performance_code
            self.augus_distribution_code = distribution_code

        self._count = len(AugusStockDetail.query.filter(
            AugusStockDetail.augus_distribution_code==distribution_code).all())
        self.augus_distribution_code = distribution_code

    def __len__(self):
        return self._count

class AugusDistributionFactory(object):
    @classmethod
    def _event_performance_distribution(cls, requests):
        for request in requests:
            for rec in request:
                yield (rec.event_code, rec.performance_code, rec.distribution_code)

    @classmethod
    def creates(cls, requests):
        event_performance_distribution = set([
            elm for elm in cls._event_performance_distribution(requests)])
        distributions = []
        for event_code, performance_code, distribution_code in event_performance_distribution:
            augus_distribution = AugusDistributionAdapter()
            augus_distribution.load(event_code, performance_code, distribution_code)
            distributions.append(augus_distribution)
        return distributions


class AugusDistributionMialer(object):
    def __init__(self, settings):
        self.settings = settings
        self.successes = []
        self.errors = []
        self.not_yets = []

    def _creates(self, requests):
        return AugusDistributionFactory.creates(requests)

    def add_success(self, request):
        self.successes.append(request)

    def add_error(self, request):
        self.errors.append(request)

    def add_not_yet(self, request):
        self.not_yets.append(request)

    def send(self):
        successes = self._creates(self.successes) # 配席成功
        errors = self._creates(self.errors) # 不正配席指示
        not_yets = self._creates(self.not_yets) # 未連携

        if len(successes) == 0 and len(errors) == 0 and len(not_yets) == 0:
            return

        params = {'successes': successes,
                  'errors': errors,
                  'not_yets': not_yets,
                  }
        sender = self.settings['mail.augus.sender']
        recipient = self.settings['mail.augus.recipient']

        mailer = Mailer(self.settings)
        body = render_to_response('altair.app.ticketing:templates/cooperation/augus/mails/augus_distribution.html', params)
        mailer.create_message(
            sender=sender,
            recipient=recipient,
            subject=u'【オーガス連携】追券/配券連携のお知らせ',
            body=body.text,
        )
        mailer.send(sender, [recipient])


def import_distribution_all(settings):
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
    err = DistributionExcutionError()
    mailer = AugusDistributionMialer(settings)

    try:
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
            except AugusDataImportError as err:# まだ連携できてないとかそういうの -> その場合はAugus側には通知せず次のターンで再度試みる
                logger.error('cannot import data: {}: {}'.format(path, repr(err)))
                transaction.abort()
                mailer.add_not_yet(request)
                continue
            except IllegalImportDataError as err:# 席が不正とかそういうの -> その場合はAugus側にエラーを通知
                logger.error('illegal data format: {}: {}'.format(path, repr(err)))
            except Exception as err: # 未知のエラーはそのまま上位に送出
                logger.error('AugusDisrtibution cannot import: {}: {}'.format(path, repr(err)))
                transaction.abort()
                raise

            try:
                exporter.export(ko_staging, request, status)
                shutil.move(path, rt_pending)
            except Exception:
                transaction.abort()
                raise
            else:
                if status == Status.OK:
                    transaction.commit()
                    mailer.add_success(request)
                else:
                    transaction.abort()
                    mailer.add_error(request)
                    raise err
    finally:
        mailer.send()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    setup_logging(args.conf)
    env = bootstrap(args.conf)
    settings = env['registry'].settings

    try:
        with multilock.MultiStartLock('augus_distribution'):
            import_distribution_all(settings)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))

if __name__ == '__main__':
    main()
