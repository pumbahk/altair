# -*- coding: utf-8 -*-
import unittest
import mock
from pyramid import testing
from altair.app.ticketing.testing import DummyRequest


class ElectingTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from ..electing import Electing
        return Electing

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _set_publisher(self):
        from altair.mq.interfaces import IPublisher
        publisher = DummyPublisher()
        self.config.registry.registerUtility(publisher,
                                             IPublisher,
                                             'lots.election'
                                             )
        self.config.registry.registerUtility(publisher,
                                             IPublisher,
                                             'lots.rejection'
                                             )
        self.config.registry.registerUtility(publisher,
                                             IPublisher,
                                             'lots.election_mail'
                                             )
        self.config.registry.registerUtility(publisher,
                                             IPublisher,
                                             'lots.rejection_mail'
                                             )
        return publisher

    def test_it(self):
        from ..interfaces import IElecting
        from zope.interface.verify import verifyObject
        request = DummyRequest()
        lot = testing.DummyResource()
        target = self._makeOne(request, lot)

        verifyObject(IElecting, target)

    def test_elect_lot_entries(self):
        publisher = self._set_publisher()
        request = DummyRequest(registry=self.config.registry)
        mock_lot = mock.Mock(id=89889891)
        #elected_wishes = [mock.Mock(entry=mock_lot.entry)]
        #rejected_wishes = [mock.Mock(entry=mock_lot.entry)]
        #mock_lot.get_elected_wishes.return_value = elected_wishes
        #mock_lot.get_rejected_wishes.return_value = rejected_wishes
        mock_lot.electing_works = [
            mock.Mock(lot_entry_no='testing-entry-no',
                      wish_order=0),
        ]

        target = self._makeOne(mock_lot, request)

        target.elect_lot_entries()
        self.assertEqual(publisher.called,
                         [('publish',
                           {'body': '{"lot_id": 89889891, "entry_no": "testing-entry-no", "wish_order": 0}',
                            'properties': {'content_type': 'application/json'},
                            'routing_key': 'lots.election'})])

        #mock_lot.entry.elect.assert_called_with(elected_wishes[0])
        #mock_lot.entry.reject.assert_called_with()
        #mock_lot.finish_lotting.assert_called_with()

    @mock.patch('altair.app.ticketing.lots.electing.Electing.get_election_mail_target_lot_elected_entries')
    def test_send_election_mails(self, get_election_mail_target_lot_elected_entries):
        get_election_mail_target_lot_elected_entries.return_value = [
            mock.Mock(id=ii) for ii in range(1, 3)
            ]
        publisher = self._set_publisher()
        request = DummyRequest(registry=self.config.registry)
        mock_lot = mock.Mock(id=89889891)
        mock_lot.electing_works = [
            mock.Mock(lot_entry_no='testing-entry-no', wish_order=0),
            ]
        target = self._makeOne(mock_lot, request)
        target.send_election_mails()
        self.assertEqual(publisher.called, [
            ('publish', {'body': '{"lot_elected_entry_id": 1}',
                         'properties': {'content_type': 'application/json'},
                         'routing_key': 'lots.election_mail'}),
            ('publish', {'body': '{"lot_elected_entry_id": 2}',
                         'properties': {'content_type': 'application/json'},
                         'routing_key': 'lots.election_mail'}),
            ])

    @mock.patch('altair.app.ticketing.lots.electing.Electing.get_rejection_mail_target_lot_rejected_entries')
    def test_send_rejection_mails(self, get_rejection_mail_target_lot_rejected_entries):
        get_rejection_mail_target_lot_rejected_entries.return_value = [
            mock.Mock(id=ii) for ii in range(1, 3)
            ]
        publisher = self._set_publisher()
        request = DummyRequest(registry=self.config.registry)
        mock_lot = mock.Mock(id=89889891)
        mock_lot.electing_works = [
            mock.Mock(lot_entry_no='testing-entry-no', wish_order=0),
            ]
        target = self._makeOne(mock_lot, request)
        target.send_rejection_mails()
        self.assertEqual(publisher.called, [
            ('publish', {'body': '{"lot_rejected_entry_id": 1}',
                         'properties': {'content_type': 'application/json'},
                         'routing_key': 'lots.rejection_mail'}),
            ('publish', {'body': '{"lot_rejected_entry_id": 2}',
                         'properties': {'content_type': 'application/json'},
                         'routing_key': 'lots.rejection_mail'}),
            ])


class DummyPublisher(object):
    def __init__(self):
        self.called = []

    def publish(self, **kwargs):
        self.called.append(('publish', kwargs))
