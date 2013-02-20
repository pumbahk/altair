# -*- coding:utf-8 -*-
import unittest
from datetime import datetime
import sys
import os

try:
   from functional_tests import AppFunctionalTests, logout, login, get_registry, get_here
   from functional_tests import delete_models, find_form
except ImportError:
   sys.path.append(os.path.join(os.path.dirname(__name__), "../../"))
   from functional_tests import AppFunctionalTests, logout, login, get_registry, get_here
   from functional_tests import delete_models, find_form

## here. test_eventpage

def _create_api_key():
   from altaircms.models import DBSession
   from altaircms.auth.models import APIKey
   apikey = APIKey()
   apikey.apikey = apikey.generate_apikey()
   DBSession.add(apikey)
   return apikey

class NotifiedEventInfoFromBackendTests(AppFunctionalTests):
   def tearDown(self):
      from altaircms.event.models import Event
      from altaircms.auth.models import APIKey
      from altaircms.models import Performance, SalesSegment, Ticket
      delete_models([Performance, SalesSegment, Ticket, APIKey, Event])


   def test_403_if_hasnot_apikey(self):
      app = self._getTarget()
      response = app.post_json("/api/event/register", {}, [], status=403)
      self.assertEqual(response.status_int, 403)

   API_HEADER_NAME = 'X-Altair-Authorization'
   def test_403_if_invalid_apikey(self):
      invalid_api_header = (self.API_HEADER_NAME, "heke-heke-heke")
      app = self._getTarget()
      response = app.post_json("/api/event/register", {}, [invalid_api_header], status=403)
      self.assertEqual(response.status_int, 403)
      
   def test_400_if_access_with_correct_apikey_but_invalid_paramater(self):
      import json
      apikey = _create_api_key()
      correct_api_header = (self.API_HEADER_NAME, apikey.apikey)
      app = self._getTarget()

      response = app.post_json("/api/event/register", {}, [correct_api_header], status=400)
      self.assertEqual(response.status_int, 400)
      result = json.loads(response.ubody)

      self.assertEqual(result["apikey"], apikey.apikey)
      self.assertEqual(result["status"], "error")

   def test_200_access_with_correct_apikey(self):
      import json
      from altaircms.models import Ticket
      from altaircms.event.models import Event
      from altaircms.auth.models import Organization

      apikey = _create_api_key()
      correct_api_header = (self.API_HEADER_NAME, apikey.apikey)
      app = self._getTarget()

      params = json.loads(get_pushed_data_from_backend())
      response = app.post_json("/api/event/register", params, [correct_api_header])
      self.assertEqual(response.status_int, 201)


      event = Event.query.one()
      self.assertEqual(event.title, u"マツイ・オン・アイス")
      self.assertEqual(event.backend_id, 40020) #backend id
      self.assertEqual(event.event_open, datetime(2012, 3, 15, 10))
      self.assertEqual(event.event_close, datetime(2012, 3, 15, 13))
      self.assertNotEqual(event.organization_id, 1000)
      self.assertEqual(event.organization_id, Organization.query.filter_by(backend_id=1).one().id)
      self.assertEqual(len(event.performances), 2)

      performance = event.performances[0]
      self.assertEqual(performance.title, u"マツイ・オン・アイス(東京公演)")
      self.assertEqual(performance.backend_id, 40096)
      self.assertEqual(performance.venue, u"まついZEROホール")
      self.assertEqual(performance.open_on, datetime(2012, 3, 15, 8))
      self.assertEqual(performance.start_on, datetime(2012, 3, 15, 10))
      self.assertEqual(performance.end_on, datetime(2012, 3, 15, 13))

      ## todo:change
      self.assertEqual(len(performance.sales), 1)

      sale = performance.sales[0]
      self.assertEqual(sale.group.name, u"一般先行")
      self.assertEqual(sale.backend_id, 40039)
      self.assertEqual(sale.start_on, datetime(2012, 1, 12, 10))
      self.assertEqual(sale.end_on, datetime(2012, 1, 22, 10))

      self.assertEqual(Ticket.query.count(), 8)
      self.assertEqual(len(sale.tickets), 4)

      ticket = performance.sales[0].tickets[0]
      self.assertEqual(ticket.backend_id, 400599)
      self.assertEqual(ticket.name, u"S席大人")
      self.assertEqual(ticket.seattype, u"S席")
      self.assertEqual(ticket.price, 20000)


PUSHED_DATA_FROM_BACKEND = None
def get_pushed_data_from_backend():
   global PUSHED_DATA_FROM_BACKEND 
   if PUSHED_DATA_FROM_BACKEND:
      return PUSHED_DATA_FROM_BACKEND
   PUSHED_DATA_FROM_BACKEND = open(os.path.join(get_here(), "functional_tests/test-event-page-pushed-data-from-backend.json")).read()
   return PUSHED_DATA_FROM_BACKEND

if __name__ == "__main__":
   def setUpModule():
      from functional_tests import get_app
      get_app()
   unittest.main()
