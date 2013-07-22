# encoding: utf-8

from unittest import TestCase
from altair.app.ticketing.testing import _setup_db, _teardown_db
from sqlalchemy.orm.exc import NoResultFound
import logging

class MyLogHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs) # old style class!
        self.last_record = None

    def emit(self, record):
        self.last_record = record

    def reset(self):
        self.last_record = None

class MailMagazineTest(TestCase):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.models',
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.mailmags.models',
            ])
        from .models import MailMagazine
        from altair.app.ticketing.core.models import Organization
        self.organization = Organization(name=u'test', short_name=u'test')
        self.magazine = MailMagazine(organization=self.organization)
        self.log_handler = MyLogHandler()
        logging.getLogger(MailMagazine.__module__).addHandler(self.log_handler)

    def tearDown(self):
        _teardown_db()

    def testSubscribeSuccess(self):
        from .models import MailMagazine, MailSubscription, MailSubscriptionStatus
        self.assertRaises(NoResultFound, lambda: MailSubscription.query.filter(MailSubscription.email == u'hoge1@example.com').one())
        new_subscription = self.magazine.subscribe(None, u'hoge1@example.com')
        self.assertTrue(new_subscription is not None)
        self.assertEqual(new_subscription, MailSubscription.query.filter(MailSubscription.email == u'hoge1@example.com').one())
        self.assertEqual(MailSubscriptionStatus.Subscribed.v, new_subscription.status)

    def testSubscribeAlreadySubscribed(self):
        from .models import MailMagazine, MailSubscription, MailSubscriptionStatus
        subscription1 = MailSubscription(segment=self.magazine, email=u'hoge1@example.com', status=None)
        self.session.add(subscription1)
        subscription2 = MailSubscription(segment=self.magazine, email=u'hoge2@example.com', status=MailSubscriptionStatus.Subscribed.v)
        self.session.add(subscription2)
        self.log_handler.reset()
        self.assertTrue(self.log_handler.last_record is None)
        _subscription1 = self.magazine.subscribe(None, u'hoge1@example.com')
        self.assertEqual(subscription1, _subscription1)
        self.assertTrue(self.log_handler.last_record is not None and self.log_handler.last_record.levelno == logging.WARN)
        self.log_handler.reset()
        self.assertTrue(self.log_handler.last_record is None)
        _subscription2 = self.magazine.subscribe(None, u'hoge2@example.com')
        self.assertEqual(subscription2, _subscription2)
        self.assertTrue(self.log_handler.last_record is not None and self.log_handler.last_record.levelno == logging.WARN)

    def testSubscribeReserved(self):
        from .models import MailMagazine, MailSubscription, MailSubscriptionStatus
        subscription = MailSubscription(segment=self.magazine, email=u'hoge1@example.com', status=MailSubscriptionStatus.Reserved.v)
        self.session.add(subscription)
        self.assertTrue(self.log_handler.last_record is None)
        _subscription = self.magazine.subscribe(None, u'hoge1@example.com')
        self.assertEqual(subscription, _subscription)
        self.assertTrue(self.log_handler.last_record is not None and self.log_handler.last_record.levelno == logging.WARN)

    def testUnsubscribe(self):
        from .models import MailMagazine, MailSubscription, MailSubscriptionStatus
        subscription = MailSubscription(segment=self.magazine, email=u'hoge1@example.com', status=MailSubscriptionStatus.Subscribed.v)
        self.session.add(subscription)
        self.magazine.unsubscribe(None, u'hoge1@example.com')
        self.session.flush()
        self.assertTrue(self.log_handler.last_record is None)
        _subscription = self.magazine.subscribe(None, u'hoge1@example.com')
        self.assertEqual(subscription, _subscription)
        self.assertTrue(self.log_handler.last_record is None)
        self.assertEqual(MailSubscriptionStatus.Subscribed.v, _subscription.status)
