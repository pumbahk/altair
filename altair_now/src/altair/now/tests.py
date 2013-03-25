import unittest
from pyramid import testing
import mock

class TestIt(unittest.TestCase):
    
    @mock.patch('altair.now.datetime')
    def test_it(self, mock_dt):
        from datetime import datetime, date
        mock_dt.now.return_value = datetime(2000, 12, 31, 13, 54, 32)
        from . import get_now, set_now, get_today
        request = testing.DummyRequest(session=dict())
        
        result = get_now(request)
        
        self.assertEqual(result, datetime(2000, 12, 31, 13, 54, 32))

        result = get_today(request)
        self.assertEqual(result, date(2000, 12, 31))

        set_now(request, datetime(2013, 3, 28, 14, 37))
        self.assertEqual(request.session['altair.now.use_datetime'], datetime(2013, 3, 28, 14, 37))
        result = get_now(request)
        
        self.assertEqual(result, datetime(2013, 3, 28, 14, 37))

        result = get_today(request)
        self.assertEqual(result, date(2013, 3, 28))

        set_now(request, None)
        self.assertNotIn('altair.now.user_datetime', request.session)
