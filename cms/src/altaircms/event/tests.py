# coding: utf-8
import unittest
from pyramid import testing
from altaircms import testing as a_testing

class ValidateAPIKeyTests(unittest.TestCase):
    def setUp(self):
        from altaircms.lib.testutils import _initTestingDB
        self.session = _initTestingDB()

    def tearDown(self):
        import transaction
        transaction.abort()
        self.session.remove()

    def _callFUT(self, *args, **kwargs):
        from .api import validate_apikey
        return validate_apikey(*args, **kwargs)

    def test_ok(self):
        from altaircms.auth.models import APIKey

        apikey = "hogehoge"
        d = APIKey(apikey=apikey)
        self.session.add(d)

        result = self._callFUT(apikey)

        self.assertTrue(result)

    def test_ng(self):
        apikey = "hogehoge"
        result = self._callFUT(apikey)

        self.assertFalse(result)

        

# class TestEventView(unittest.TestCase):
#     def setUp(self):
#         self.config = testing.setUp()
        
#     def tearDown(self):
#         testing.tearDown()
#         import transaction
#         transaction.abort()

#     def _getTarget(self):
#         from .views import EventRESTAPIView
#         return EventRESTAPIView

#     def _makeOne(self, request):
#         return self._getTarget()(request)

#     def test_create_invalid(self):
#         # null post
#         request = testing.DummyRequest()

#         target = self._makeOne(request)
#         result = target.create()

#         self.assertEqual(result.status_int, 400)

#     def test_create_valid(self):
#         self._fill_request_post()
#         request = testing.DummyRequest(POST=self._fill_request_post())

#         target = self._makeOne(request)
#         result = target.create()

#         self.assertEqual(result.status_int, 201)
#         self.assertEqual(result.message, None)

#     def test_read(self):
#         self._insert_event()

#         # list object
#         resp = EventRESTAPIView(self.request).read()
#         self.assertTrue(str(resp).startswith("{'events': ["))

#         # read object
#         resp = EventRESTAPIView(self.request, '1').read()
#         self.assertTrue(str(resp).startswith("{'inquiry_for':"))

#     def test_delete(self):
#         self._insert_event()

#         resp = EventRESTAPIView(self.request, '1').delete()
#         self.assertEqual(resp.status_int, 200)

#         resp = EventRESTAPIView(self.request, '999').delete()
#         self.assertEqual(resp.status_int, 400)

#     def _insert_event(self):


#     def _fill_request_post(self):
#         return dict(
#             (u'title', u'たいとる'),
#             (u'subtitle', u'サブタイトル'),
#             (u'description', u'説明'),
#             (u'event_open', u'2011-1-1 00:00:00'),
#             (u'event_close', u'2011-12-31 23:59:59'),
#             (u'deal_open', u'2011-12-31 23:59:59'),
#             (u'deal_close', u'2011-12-31 23:59:59'),
#             (u'is_searchable', u'y'),
#             )

class DummyValidator(object):
    def __init__(self, apikey):
        self.apikey = apikey
        self.called = []

    def __call__(self, apikey):
        self.called.append(('__call__', apikey))
        return self.apikey == apikey

class DummyEventRepositry(testing.DummyResource):
    def parse_and_save_event(self, data):
        self.called_data = data

class TestEventRegister(unittest.TestCase):
    
    def setUp(self):
        self.config = testing.setUp()


    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from .views import event_register
        return event_register(request)


    def test_event_register_ok(self):
        from .interfaces import IAPIKEYValidator, IEventRepositiry
        validator = DummyValidator('hogehoge')
        repository = DummyEventRepositry()
        self.config.registry.registerUtility(validator, IAPIKEYValidator)
        self.config.registry.registerUtility(repository, IEventRepositiry)

        headers = {'X-Altair-Authorization': 'hogehoge'}
        request = a_testing.DummyRequest(registry=self.config.registry,
                                         headers=headers,
                                         POST={'jsonstring': '{}'},
                                         )

        response = self._callFUT(request)

        self.assertEqual(response.status_int, 201)
        self.assertEqual(repository.called_data, {})


    def test_event_register_ng(self):
        from .interfaces import IAPIKEYValidator
        validator = DummyValidator('hogehoge')
        self.config.registry.registerUtility(validator, IAPIKEYValidator)
        # 認証パラメタなし
        request = a_testing.DummyRequest(POST={})

        response = self._callFUT(request)

        self.assertEqual(response.status_int, 403)

    def test_event_register_ng2(self):
        from .interfaces import IAPIKEYValidator
        validator = DummyValidator('hogehoge')
        self.config.registry.registerUtility(validator, IAPIKEYValidator)

        # 認証通過、必須パラメタなし
        headers = {'X-Altair-Authorization': 'hogehoge'}
        request = a_testing.DummyRequest(registry=self.config.registry,
                                       POST={}, 
                                       headers=headers)

        response = self._callFUT(request)

        self.assertEqual(response.status_int, 400)

    def test_event_register_ng3(self):
        from .interfaces import IAPIKEYValidator
        validator = DummyValidator('hogehoge')
        self.config.registry.registerUtility(validator, IAPIKEYValidator)

        # パースできないJSON
        headers = {'X-Altair-Authorization': 'hogehoge'}
        POST = {'jsonstring': 'aaaaaaaaaaa'}
        request = a_testing.DummyRequest(registry=self.config.registry,
                                         headers=headers,
                                         POST=POST)
        response = self._callFUT(request)

        self.assertEqual(response.status_int, 400)
