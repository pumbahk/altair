# coding: utf-8
import transaction

from pyramid import testing
from sqlalchemy.orm.exc import NoResultFound
from webob.multidict import MultiDict

from altaircms.lib.testutils import BaseTest
from altaircms.event.views import EventRESTAPIView
from altaircms.models import Event, DBSession

from .views import event_register

class TestEventView(BaseTest):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.request.method = "PUT"
        super(TestEventView, self).setUp()

    def tearDown(self):
        transaction.commit()

    def test_create_invalid(self):
        # null post
        self.request.POST = MultiDict([])

        resp = EventRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 400)

    def test_create_valid(self):
        self._fill_request_post()

        resp = EventRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 201)
        self.assertEqual(resp.message, None)

    def test_read(self):
        self._insert_event()

        # list object
        resp = EventRESTAPIView(self.request).read()
        self.assertTrue(str(resp).startswith("{'events': ["))

        # read object
        resp = EventRESTAPIView(self.request, '1').read()
        self.assertTrue(str(resp).startswith("{'inquiry_for':"))

    def test_delete(self):
        self._insert_event()

        resp = EventRESTAPIView(self.request, '1').delete()
        self.assertEqual(resp.status_int, 200)

        resp = EventRESTAPIView(self.request, '999').delete()
        self.assertEqual(resp.status_int, 400)

    def _insert_event(self):
        self._fill_request_post()
        resp = EventRESTAPIView(self.request).create()

    def _fill_request_post(self):
        self.request.POST = MultiDict([
            (u'title', u'たいとる'),
            (u'subtitle', u'サブタイトル'),
            (u'description', u'説明'),
            (u'event_open', u'2011-1-1 00:00:00'),
            (u'event_close', u'2011-12-31 23:59:59'),
            (u'deal_open', u'2011-12-31 23:59:59'),
            (u'deal_close', u'2011-12-31 23:59:59'),
            (u'is_searchable', u'y'),
        ])


class TestEventRegister(BaseTest):
    def test_event_register_ok(self):
        request = testing.DummyRequest()
        request.headers['X-Altair-Authorization'] = 'hogehoge'
        request.POST = MultiDict({'jsonstring': self.jsonstring})
        response = event_register(request)

        self.assertEqual(response.status_int, 201)
        self.assertTrue(DBSession.query(Event).filter_by(id=1).one())

        request = testing.DummyRequest()
        request.headers['X-Altair-Authorization'] = 'hogehoge'
        request.POST = MultiDict({'jsonstring': self.jsonstring_delete})
        response = event_register(request)

        self.assertEqual(response.status_int, 201)
        self.assertEqual(DBSession.query(Event).filter_by(id=1).count(), 0)

    def test_event_register_ng(self):
        # 認証パラメタなし
        request = testing.DummyRequest()
        request.POST = MultiDict({})
        response = event_register(request)

        self.assertEqual(response.status_int, 403)

        # 認証通過、必須パラメタなし
        request = testing.DummyRequest()
        request.headers['X-Altair-Authorization'] = 'hogehoge'
        request.POST = MultiDict({})
        response = event_register(request)

        self.assertEqual(response.status_int, 400)

        # パースできないJSON
        request = testing.DummyRequest()
        request.headers['X-Altair-Authorization'] = 'hogehoge'
        request.POST = MultiDict({'jsonstring': self.jsonstring + 'hogehoge'})
        response = event_register(request)

        self.assertEqual(response.status_int, 400)

    def setUp(self):
        from altaircms.models import DBSession
        from altaircms.auth.models import APIKey

        apikey = APIKey(name='hoge', apikey='hogehoge')
        DBSession.add(apikey)

        self.endpoint = '/api/event/register'
        self.valid_apikey = ''
        self.invalid_apikey = ''
        self.jsonstring_delete = '''{
  "created_at": "2012-01-10T13:42:00+09:00",
  "updated_at": "2012-01-11T15:32:00+09:00",
  "events": [
    {
      "id": 1,
      "deleted": true
    }
  ]
}'''
        self.jsonstring = '''{
  "created_at": "2012-01-10T13:42:00+09:00",
  "updated_at": "2012-01-11T15:32:00+09:00",
  "events": [
    {
      "id": 1,
      "name": "マツイ・オン・アイス",
      "start_on": "2012-03-15T19:00:00+09:00",
      "end_on": "2012-03-15T22:00:00+09:00",
      "performances": [
        {
          "id": 2,
          "name": "マツイ・オン・アイス 東京公演",
          "venue": "まついZEROホール",
          "open_on": "2012-03-15T17:00:00+09:00",
          "start_on": "2012-03-15T19:00:00+09:00",
          "close_on": "2012-03-15T22:00:00+09:00",
          "sales": [
            {
              "name": "presale",
              "start_on": "2012-01-12T19:00:00+09:00",
              "end_on": "2012-01-22T19:00:00+09:00",
              "tickets": [
                {
                  "name": "A席大人",
                  "seat_type": "A席",
                  "price": 5000
                },
                {
                  "name": "A席子供",
                  "seat_type": "A席",
                  "price": 3000
                },
                {
                  "name": "B席",
                  "seat_type": "B席",
                  "price": 3000
                }
              ]
            },
            {
              "name": "normal",
              "start_on": "2012-01-23T19:00:00+09:00",
              "end_on": "2012-01-31T19:00:00+09:00",
              "tickets": [
                {
                  "name": "A席大人",
                  "seat_type": "A席",
                  "price": 5000
                },
                {
                  "name": "A席子供",
                  "seat_type": "A席",
                  "price": 3000
                },
                {
                  "name": "B席",
                  "seat_type": "B席",
                  "price": 3000
                }
              ]
            }
          ]
        },
        {
          "id": 3,
          "name": "マツイ・オン・アイス 大阪公演",
          "venue": "心斎橋まつい会館",
          "open_on": "2012-03-16T17:00:00+09:00",
          "start_on": "2012-03-16T19:00:00+09:00",
          "close_on": "2012-03-16T22:00:00+09:00",
          "sales": [
            {
              "name": "presale",
              "start_on": "2012-01-12T19:00:00+09:00",
              "end_on": "2012-01-22T19:00:00+09:00",
              "tickets": [
                {
                  "name": "A席大人",
                  "seat_type": "A席",
                  "price": 5000
                },
                {
                  "name": "A席子供",
                  "seat_type": "A席",
                  "price": 3000
                },
                {
                  "name": "B席",
                  "seat_type": "B席",
                  "price": 3000
                }
              ]
            },
            {
              "name": "normal",
              "start_on": "2012-01-23T19:00:00+09:00",
              "end_on": "2012-01-31T19:00:00+09:00",
              "tickets": [
                {
                  "name": "A席大人",
                  "seat_type": "A席",
                  "price": 5000
                },
                {
                  "name": "A席子供",
                  "seat_type": "A席",
                  "price": 3000
                },
                {
                  "name": "B席",
                  "seat_type": "B席",
                  "price": 3000
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
'''
        super(TestEventRegister, self).setUp()

