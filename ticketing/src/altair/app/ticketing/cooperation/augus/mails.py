# -*- coding: utf-8 -*-
import os
import csv
import logging
from email import Encoders
from email.Header import Header
from email.Utils import formatdate
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from pyramid.renderers import render_to_response
from altair.app.ticketing.core.models import (
    Mailer,
    AugusPerformance,
    AugusStockDetail,
    )

logger = logging.getLogger(__name__)


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
        self.sender = None
        self.recipients = []
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
        sender = self.sender
        recipients = self.recipients

        mailer = Mailer(self.settings)
        body = render_to_response('altair.app.ticketing:templates/cooperation/augus/mails/augus_distribution.html', params)
        mailer.create_message(
            sender=sender,
            recipient=recipients,
            subject=u'【オーガス連携】追券/配券連携のお知らせ',
            body=body.text,
        )
        mailer.send(sender, recipients)


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

    def send(self, recipients, sender):
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


class MultipartMailer(Mailer):
    def get_message_encoding(self):
        return self.settings['mail.message.encoding']

    def create_message(self,
                       sender=None,
                       recipient=None,
                       subject=None,
                       body=None,
                       html=None,
                       encoding=None,
                       filename=None,
                       filepath_or_object=None):
        encoding = self.get_message_encoding()
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


def send_venue_sync_request_mail(mailer, augus_account, path):
    title = ''
    filename = os.path.basename(path)
    with open(path, 'rb') as fp:
        reader = csv.reader(fp)
        reader.next()  # header
        row = reader.next()
        title = row[1].decode('cp932')

    sender = 'dev@ticketstar.jp'
    recipient = 'venue@ticketstar.jp'

    body = u'''会場図チーム各位

オーガス側から{}用の会場図データの連携要求がありました。
連携用のcsvを添付しますので
データの登録/更新をお願いします。

会場名
{}

登録/更新の登録が完了できましたら、
お手数ですが開発部までご連絡ください。

以上です。
'''.format(augus_account.name, title)
    encoding = mailer.get_message_encoding()
    try:
        body = body.encode(encoding)
    except UnicodeEncodeError as err:
        logger.warn(err)
        body = body.encode(encoding, errors='ignore')

    mailer.create_message(
        sender=sender,
        recipient=recipient,
        subject=u'【オーガス連携】会場図データ登録のお願い {}'.format(title),
        body=body,
        filename=filename,
        filepath_or_object=path,
    )
    mailer.send(sender, [recipient])
