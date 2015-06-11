# -*- coding: utf-8 -*-
import six
from unittest import (
    skip,
    TestCase,
    )
from datetime import (
    datetime,
    timedelta,
    )


if six.PY3:
    from unittest import mock
else:
    import mock  # noqa


class FamiPortOrderAutoCopleterTest(TestCase):
    def _get_target_class(self):
        from ..famiport_auto_complete import FamiPortOrderAutoCompleter as klass
        return klass

    def _get_target(self, *args, **kwds):
        klass = self._get_target_class()
        return klass(*args, **kwds)

    @mock.patch('altair.app.ticketing.famiport.scripts.famiport_auto_complete._get_now')
    def test_timepoint(self, _get_now):
        now = datetime.now()
        nine_minutes_ago = now - timedelta(minutes=90)
        _get_now.return_value = now
        session = mock.Mock()
        target = self._get_target(session)
        self.assertEqual(target.time_point, nine_minutes_ago)

    @mock.patch('altair.app.ticketing.famiport.scripts.famiport_auto_complete.FamiPortOrderAutoCompleter._fetch_target_famiport_receipts')
    @mock.patch('altair.app.ticketing.famiport.scripts.famiport_auto_complete.FamiPortOrderAutoCompleter._do_complete')
    def test_complete(self, _do_complete, _fetch_target_famiport_receipts):
        from ..famiport_auto_complete import AutoCompleterStatus
        session = mock.Mock()
        famiport_receipts = [mock.Mock() for ii in range(10)]
        _fetch_target_famiport_receipts.return_value = famiport_receipts
        target = self._get_target(session)
        res = target.complete()
        self.assertEqual(res, AutoCompleterStatus.success.value)

        do_complete_call_args_list = [call_args[0][0] for call_args in _do_complete.call_args_list]
        session_call_args_list = [call_args[0][0] for call_args in session.add.call_args_list]
        self.assertEqual(do_complete_call_args_list, famiport_receipts)
        self.assertEqual(session_call_args_list, famiport_receipts)

    @skip('not yet implemented')
    def test_do_complete(self):
        pass

    @skip('not yet implemented')
    def test_fetch_target_famiport_orders(self):
        pass
