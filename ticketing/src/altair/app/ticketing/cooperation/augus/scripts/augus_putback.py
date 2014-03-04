#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import argparse
import transaction
from pyramid.paster import bootstrap
from pyramid.renderers import render_to_response
from altair.app.ticketing.core.models import (
    Mailer,
    AugusPutback,
    )
from altair.augus.protocols import TicketSyncRequest
from altair.augus.parsers import AugusParser
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
    env = bootstrap(args.conf)
    settings = env['registry'].settings
    putback_codes = []
    try:
        with multilock.MultiStartLock('augus_putback'):
            putback_codes = export_putback_all(settings)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))
    else:
        count = len(putback_codes)
        if 0 == putback_codes:
            return
        sender = settings['mail.augus.sender']
        recipient = settings['mail.augus.recipient']

        augus_putbacks = AugusPutback\
            .query\
            .filter(AugusPutback.augus_putback_code.in_(putback_codes))\
            .order_by(AugusPutback.augus_performance_id)\
            .all()
        mailer = Mailer(settings)
        params = {'augus_putbacks': augus_putbacks}
        body = render_to_response('altair.app.ticketing:templates/cooperation/augus/mails/augus_putback.html', params)
        mailer.create_message(
            sender=sender,
            recipient=recipient,
            subject=u'【オーガス連携】返券のお知らせ',
            body=body.text,
        )
        mailer.send(sender, [recipient])

if __name__ == '__main__':
    main()
