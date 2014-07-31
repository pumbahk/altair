# -*- coding: utf-8 -*-
from pyramid.renderers import render_to_response
from altair.app.ticketing.core.models import (
    Mailer,
    AugusPerformance,
    AugusStockDetail,
    )

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
