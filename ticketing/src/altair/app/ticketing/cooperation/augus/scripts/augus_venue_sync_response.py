#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import logging
import datetime
import argparse
import transaction
from sqlalchemy import (
    and_,
    or_,
    )
from pyramid.paster import (
    bootstrap,
    setup_logging,
    )
from pyramid.renderers import render_to_response
from altair.app.ticketing.core.models import (
    Mailer,
    AugusVenue,
    )
from altair.augus.protocols import VenueSyncResponse
from altair.augus.exporters import AugusExporter
from altair.augus.types import Status
from altair import multilock

from ..exporters import AugusPutbackExporter
from ..errors import AugusDataImportError
from ..operations import AugusOperationManager
from ..config import get_var_dir

logger = logging.getLogger(__name__)

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def export_venue_sync_response_all(settings):
    consumer_id = int(settings['augus_consumer_id'])
    ko_staging = settings['ko_staging']

    mkdir_p(ko_staging)

    augus_venues = AugusVenue\
        .query\
        .filter(AugusVenue.reserved_at!=None)\
        .filter(or_(AugusVenue.notified_at==None,
                    and_(AugusVenue.notified_at!=None,
                         AugusVenue.reserved_at>AugusVenue.notified_at)))\
        .all()


    now = datetime.datetime.now()
    for augus_venue in augus_venues:
        venue_response = VenueSyncResponse(customer_id=consumer_id, venue_code=augus_venue.code)
        record = venue_response.record()
        record.venue_code = augus_venue.code
        record.venue_name = augus_venue.name
        record.status = Status.OK.value
        record.venue_version = augus_venue.version
        venue_response.append(record)

        path = os.path.join(ko_staging, venue_response.name)
        AugusExporter.export(venue_response, path)
        augus_venue.notified_at = now
        augus_venue.save()
    return augus_venues




def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    setup_logging(args.conf)
    env = bootstrap(args.conf)
    settings = env['registry'].settings
    augus_venues = []
    try:
        with multilock.MultiStartLock('augus_venue_sync_response'):
            augus_venues = export_venue_sync_response_all(settings)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))
    else:
        count = len(augus_venues)
        if 0 == count:
            return
        sender = settings['mail.augus.sender']
        recipient = settings['mail.augus.recipient.venue']

        mailer = Mailer(settings)
        params = {'augus_venues': augus_venues}
        body = render_to_response('altair.app.ticketing:templates/cooperation/augus/mails/augus_venue_sync_response.html', params)
        mailer.create_message(
            sender=sender,
            recipient=recipient,
            subject=u'【オーガス連携】会場連携通知完了のお知らせ',
            body=body.text,
        )
        mailer.send(sender, [recipient])
        transaction.commit()


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
        with multilock.MultiStartLock('augus_venue_sync_response'):
            mgr.venue_sync_response(mailer)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))
        return

if __name__ == '__main__':
    main()
