#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import time
import shutil
import logging
import argparse
from pyramid.renderers import render_to_response
from pyramid.paster import (
    bootstrap,
    setup_logging,
    )
import transaction
from altair.augus.exporters import AugusExporter
from altair.augus.parsers import AugusParser
from altair.augus.protocols import AchievementRequest, VenueSyncRequest
from altair.app.ticketing.core.models import (
    Mailer,
    AugusPerformance,
    )
from ..exporters import AugusAchievementExporter
from .. import multilock


from email import Encoders
from email.Header import Header
from email.Utils import formatdate
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

class MultipartEmail(Mailer):
    def create_message(self,
                       sender=None,
                       recipient=None,
                       subject=None,
                       body=None,
                       html=None,
                       encoding=None,
                       filename=None,
                       filepath_or_object=None):
        encoding = self.settings['mail.message.encoding']
        if html:
            mime_type = 'html'
            mime_text = html
        else:
            mime_type = 'plain'
            mime_text = body

        msg = MIMEMultipart()
        msg['Subject'] = Header(subject, encoding)
        msg['From'] = sender
        msg['To'] = recipient
        msg['Date'] = formatdate()

        body = MIMEText(mime_text.encode(encoding, 'ignore'), mime_type, encoding)
        msg.attach(body)

        attachment = MIMEBase('text', 'csv')

        data = ''
        if hasattr(filepath_or_object, 'read'):
           cur = filepath_or_object.tell()
           data = filepath_or_object.read()
           filepath_or_object.seek(cur)
        else:
           with open(filepath_or_object, 'rb') as fp:
               data = fp.read()
        attachment.set_payload(data)
        Encoders.encode_base64(attachment)
        msg.attach(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        self.message = msg

logger = logging.getLogger(__name__)

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

import os.path
import csv
def send_request_mail(settings, path):
    mailer = MultipartEmail(settings)
    title = ''
    filename = os.path.basename(path)
    with open(path, 'rb') as fp:
        reader = csv.reader(fp)
        reader.next() # header
        row = reader.next()
        title = row[1].decode('cp932')

    sender = 'dev@ticketstar.jp'
    recipient = 'venue@ticketstar.jp'

    mailer = MultipartEmail(settings)
    body = u'''会場図チーム各位

オーガス側から会場図データの連携要求がありました。
連携用のcsvを添付しますので
データの登録/更新をお願いします。

会場名
{}

登録/更新の登録が完了できましたら、
お手数ですが嶋田までご連絡ください。

以上です。
'''.format(title)
    encoding = settings['mail.message.encoding']
    body = body.encode(encoding)

    mailer.create_message(
        sender=sender,
        recipient=recipient,
        subject=u'【オーガス連携】会場図データ登録のお願い {}'.format(title),
        body=body,
        filename=filename,
        filepath_or_object=path,
    )
    print 'SEND OK:', filename
    mailer.send(sender, [recipient])

def request_venue_sync(settings):
    rt_staging = settings['rt_staging']
    rt_pending = settings['rt_pending']
    mkdir_p(rt_staging)
    mkdir_p(rt_pending)

    target = VenueSyncRequest
    for name in filter(target.match_name, os.listdir(rt_staging)):
        time.sleep(2)
        path = os.path.join(rt_staging, name)
        logger.info('request augus venue sync: {}'.format(name))
        send_request_mail(settings, path)
        shutil.move(path, rt_pending)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    setup_logging(args.conf)
    env = bootstrap(args.conf)
    settings = env['registry'].settings

    try:
        with multilock.MultiStartLock('augus_venue_request'):
            request_venue_sync(settings)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))
        return

if __name__ == '__main__':
    main()
