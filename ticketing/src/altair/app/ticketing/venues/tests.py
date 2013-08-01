import unittest
import mock
from pyramid import testing


# class get_drawingTests(unittest.TestCase):

#     def _callFUT(self, *args, **kwargs):
#         from .views import get_drawing
#         return get_drawing(*args, **kwargs)


#     @mock.patch('altair.app.ticketing.venues.views.Venue')
#     def test_no_venue(self, mock_Venue):
#         mock_Venue.get.return_value = None
#         request = testing.DummyRequest(matchdict=dict(venue_id='999999999'))
#         result = self._callFUT(request)
        
#         self.assertEqual(result.status_int, 404)
#         mock_Venue.get.assert_called_with(999999999)

#     @mock.patch('altair.app.ticketing.venues.views.Venue')
#     def test_no_site(self, mock_Venue):
#         mock_venue = mock_Venue.get.return_value
#         mock_venue.site = None
#         request = testing.DummyRequest(matchdict=dict(venue_id='999999999'))
#         result = self._callFUT(request)
        
#         self.assertEqual(result.status_int, 404)
#         mock_Venue.get.assert_called_with(999999999)

#     @mock.patch('altair.app.ticketing.venues.views.Venue')
#     def test_no_site_drawing_url(self, mock_Venue):
#         mock_venue = mock_Venue.get.return_value
#         mock_site = mock_venue.site
#         mock_site.drawing_url = None
#         request = testing.DummyRequest(matchdict=dict(venue_id='999999999'))
#         result = self._callFUT(request)
        
#         self.assertEqual(result.status_int, 404)
#         mock_Venue.get.assert_called_with(999999999)

#     @mock.patch('altair.app.ticketing.venues.views.Venue')
#     @mock.patch('altair.app.ticketing.venues.views.urlopen')
#     def test_it(self, mock_urlopen, mock_Venue):

#         mock_urlopen.return_value = ["testing"]

#         mock_venue = mock_Venue.get.return_value
#         mock_site = mock_venue.site
#         mock_site.drawing_url = 'http://testing/url'
#         request = testing.DummyRequest(matchdict=dict(venue_id='999999999'))

#         result = self._callFUT(request)
        
#         self.assertEqual(result.status_int, 200)
#         self.assertEqual(result.body, "testing")
#         mock_Venue.get.assert_called_with(999999999)
#         mock_urlopen.assert_called_with("http://testing/url")
