import unittest
from pyramid import testing

class TestIt(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_it(self):
        self.config.include('ticketing.tbview')

        def dummy_view(request):
            raise Exception('dummy error')

        self.config.add_route('top', '/')
        self.config.add_view(dummy_view, route_name='top')

        app = self.config.make_wsgi_app()

        from webob import Request
        request = Request.blank('/')
        res = request.get_response(app)
        res_parts = res.text.strip().split('\n')
        self.assertEqual(res_parts[0], u'Traceback (most recent call last):')
        self.assertEqual(res_parts[-1], u'Exception: dummy error')

    def test_with_excview(self):
        self.config.include('ticketing.tbview')

        class DummyException(Exception):
            pass

        def dummy_view(request):
            raise DummyException('dummy error')

        def dummy_exc_view(request):
            request.response.text = u'catched'
            return request.response

        self.config.add_route('top', '/')
        self.config.add_view(dummy_exc_view, context=DummyException)
        self.config.add_view(dummy_view, route_name='top')

        app = self.config.make_wsgi_app()

        from webob import Request
        request = Request.blank('/')
        res = request.get_response(app)
        self.assertEqual(res.text, u'catched')
