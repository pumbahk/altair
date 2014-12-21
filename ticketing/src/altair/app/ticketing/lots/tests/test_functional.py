# -*- coding:utf-8 
# import unittest


# def includeme(config):
#     """ setup testing config
#     """

#     from pyramid.session import UnencryptedCookieSessionFactoryConfig
#     session_factory = UnencryptedCookieSessionFactoryConfig("secret")
#     config.set_session_factory(session_factory)
#     config.include('pyramid_layout')

# class FunctinalTests(unittest.TestCase):
#     settings = {
#         'sqlalchemy.url': 'sqlite:///',
#         'mako.directories': ['altair.app.ticketing.lots:templates'],
#         'pyramid.includes': ['altair.app.ticketing.lots.tests.test_functional'],
#         'altair.auth.decider': 'altair.app.ticketing.lots:WhoDecider',
#         'altair.rakuten_auth.token_secret': 'very-secret',
#     }

#     def setUp(self):
#         from webtest import TestApp
#         from altair.app.ticketing.core.models import Event
#         from altair.app.ticketing.lots.models import Lot
#         from altair.app.ticketing.lots import main
#         import sqlahelper

#         self.session = sqlahelper.get_session()
#         self.session.remove()
#         app = main({}, **self.settings)
#         self.app = TestApp(app)
#         sqlahelper.get_base().metadata.create_all()

#     # def test_get_index_not_found(self):
#     #     res = self.app.get('/lots/events/1000/entry/1000', status=404)

#     def _add_lot(self, event_id, lot_id):
#         from altair.app.ticketing.core.models import Event, SalesSegment, Organization, StockType, Performance, Venue, Site
#         from altair.app.ticketing.users.models import MemberGroup, Membership
#         from altair.app.ticketing.lots.models import Lot

#         organization = Organization(short_name="testing")
#         site = Site()
#         event = Event(id=event_id, organization=organization)
#         membership = Membership(organization=organization)
#         membergroup = MemberGroup(membership=membership, is_guest=True)
#         sales_segment = SalesSegment(event=event, membergroups=[membergroup])
#         performances = []
#         for i in range(10):
#             p = Performance(name=u"パフォーマンス {0}".format(i))
#             v = Venue(performance=p, site=site, organization=organization)
#             self.session.add(p)
#             performances.append(p)
#         # stock_types
#         stock_types = []
#         for i in range(5):
#             s = StockType(name=u"席 {0}".format(i))
#             self.session.add(s)
#             stock_types.append(s)
#         lot = Lot(id=lot_id, event=event, sales_segment=sales_segment, limit_wishes=3, performances=performances, stock_types=stock_types)
#         self.session.add(event)
#         self.session.flush()

    # def test_get_index(self):
    #     self._add_lot(1000, 1001)
    #     res = self.app.get('/lots/events/1000/entry/1001')

    # def test_post_index(self):
    #     self._add_lot(2000, 2001)
    #     res = self.app.post('/lots/events/2000/entry/2001')

    # def test_get_confirm_without_session(self):
    #     self._add_lot(3000, 3001)
    #     res = self.app.get('/lots/events/3000/entry/3001/confirm')
    #     self.assertEqual(res.location, 'http://localhost/lots/events/3000/entry/3001')

    # def test_get_confirm(self):
    #     self._add_lot(3010, 3011)
    #     res = self.app.get('/lots/events/3010/entry/3011/confirm')

    # def test_post_confirm(self):
    #     self._add_lot(4000, 4001)
    #     res = self.app.post('/lots/events/4000/entry/4001/confirm')

    # def test_get_completion(self):
    #     self._add_lot(5000, 5001)
    #     res = self.app.get('/lots/events/5000/entry/5001/completion')
