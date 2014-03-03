#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import shutil
import logging
import argparse
import transaction
from pyramid.paster import bootstrap
from pyramid.renderers import render_to_response
from altair.app.ticketing.core.models import (
    Mailer,
    AugusPerformance,
    AugusTicket,
    )
from altair.augus.protocols import TicketSyncRequest
from altair.augus.parsers import AugusParser
from ..importers import AugusTicketImpoter
from ..errors import AugusDataImportError
from .. import multilock

logger = logging.getLogger(__name__)

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def import_ticket_all(settings):
    rt_staging = settings['rt_staging']
    rt_pending = settings['rt_pending']
    ko_staging = settings['ko_staging']

    mkdir_p(rt_staging)
    mkdir_p(rt_pending)
    mkdir_p(ko_staging)

    importer = AugusTicketImpoter()
    target = TicketSyncRequest
    paths = []

    augus_ticket_ids = []
    try:
        for name in filter(target.match_name, os.listdir(rt_staging)):
            logger.info('start import AugusTicket: {}'.format(name))
            try:
                path = os.path.join(rt_staging, name)
                paths.append(path)
                request = AugusParser.parse(path)
                augus_tickets = importer.import_(request)
                augus_ticket_ids.extend([agt.id for agt in augus_tickets])
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
    return augus_ticket_ids

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    env = bootstrap(args.conf)
    settings = env['registry'].settings

    augus_ticket_ids = []
    try:
        with multilock.MultiStartLock('augus_ticket'):
            augus_ticket_ids = import_ticket_all(settings)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))
    else:
        ticket_count = len(augus_ticket_ids)
        if 0 == ticket_count:
            return
        sender = settings['mail.augus.sender']
        recipient = settings['mail.augus.recipient']

        augus_performances = AugusPerformance\
            .query\
            .join(AugusTicket)\
            .filter(AugusTicket.id.in_(augus_ticket_ids))\
            .all()
        augus_performances = list(set(augus_performances))
        mailer = Mailer(settings)
        params = {'augus_performances': augus_performances,
                  'count': ticket_count,
                  }
        body = render_to_response('altair.app.ticketing:templates/cooperation/augus/mails/augus_ticket.html', params)
        mailer.create_message(
            sender=sender,
            recipient=recipient,
            subject=u'【オーガス連携】チケット連携のお知らせ',
            body=body.text,
        )
        mailer.send(sender, [recipient])


if __name__ == '__main__':
    main()
