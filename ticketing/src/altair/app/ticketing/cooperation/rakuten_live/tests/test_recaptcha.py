from unittest import TestCase

from altair.app.ticketing.cooperation.rakuten_live import recaptcha
from altair.app.ticketing.cooperation.rakuten_live.models import RakutenLiveSession
from mock import patch
from pyramid import testing


class ReCAPTCHAExemptTest(TestCase):
    PERFORMANCE_ID = 1100
    LOT_ID = 500

    def setUp(self):
        self.cart_request = testing.DummyRequest(matchdict={'performance_id': self.PERFORMANCE_ID})
        self.lot_request = testing.DummyRequest(matchdict={'lot_id': self.LOT_ID})

    @patch('{}.convert_type'.format(recaptcha.__name__))
    @patch('{}.get_r_live_session'.format(recaptcha.__name__))
    @patch('{}.has_r_live_session'.format(recaptcha.__name__))
    def test_recaptcha_exempt(self, mock_has_r_live_session, mock_get_r_live_session, mock_convert_type):
        mock_has_r_live_session.return_value = True
        mock_get_r_live_session.return_value = RakutenLiveSession(performance_id=self.PERFORMANCE_ID)
        mock_convert_type.return_value = self.PERFORMANCE_ID
        # assert the performance id from the route matchdict is the same as that in session
        self.assertTrue(recaptcha.recaptcha_exempt(self.cart_request))

        mock_get_r_live_session.return_value = RakutenLiveSession(lot_id=self.LOT_ID)
        mock_convert_type.return_value = self.LOT_ID
        # assert the lottery id from the route matchdict is the same as that in session
        self.assertTrue(recaptcha.recaptcha_exempt(self.lot_request))

    @patch('{}.convert_type'.format(recaptcha.__name__))
    @patch('{}.get_r_live_session'.format(recaptcha.__name__))
    @patch('{}.has_r_live_session'.format(recaptcha.__name__))
    def test_recaptcha_not_exempted(self, mock_has_r_live_session, mock_get_r_live_session, mock_convert_type):
        mock_has_r_live_session.return_value = True
        mock_get_r_live_session.return_value = RakutenLiveSession(performance_id=100)
        mock_convert_type.return_value = True
        # assert the performance id from the route matchdict is different from that in session
        self.assertFalse(recaptcha.recaptcha_exempt(self.cart_request))

        mock_get_r_live_session.return_value = RakutenLiveSession(lot_id=50)
        # assert the lottery id from the route matchdict is different from that in session
        self.assertFalse(recaptcha.recaptcha_exempt(self.lot_request))

        mock_get_r_live_session.return_value = RakutenLiveSession()
        # assert the performance id from the route matchdict is nothing in session
        self.assertFalse(recaptcha.recaptcha_exempt(self.cart_request))
