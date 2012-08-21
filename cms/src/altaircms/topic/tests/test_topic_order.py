# -*- coding:utf-8 -*-
import unittest
import sqlalchemy as sa
from datetime import datetime
from altaircms.models import DBSession
from altaircms.models import Base
from altaircms.topic.models import Topic

def setUpModule():
    engine = sa.create_engine("sqlite://")
    Base.metadata.bind = engine
    DBSession.bind = engine
    Base.metadata.create_all()

def tearDown():
    Base.metadata.drop_all()
    DBSession.remove()

class PublishTermTest(unittest.TestCase):
    def _makeOne(self, b, a):
        return Topic(publish_open_on=b, publish_close_on=a)

    def _callFUT(self, start_on, end_on):
        topic = self._makeOne(start_on, end_on)
        DBSession.add(topic)
        return Topic.publishing

    def tearDown(self):
        import transaction
        transaction.abort()

    def test_before(self):
        """ [today] < open < close => 0"""
        publishing = self._callFUT(datetime(2011, 2, 1),datetime(2011, 5, 1))
        self.assertEquals(publishing(datetime(2011, 1, 1)).count(), 0)

    def test_on_open_on(self):
        """ [today] = open < close => 1"""
        publishing = self._callFUT(datetime(2011, 2, 1),datetime(2011, 5, 1))
        self.assertEquals(publishing(datetime(2011, 2, 1)).count(), 1)

    def test_on_in(self):
        """ open < [today] < close => 1"""
        publishing = self._callFUT(datetime(2011, 2, 1),datetime(2011, 5, 1))
        self.assertEquals(publishing(datetime(2011, 3, 1)).count(), 1)

    def test_on_close_on(self):
        """ open < [today] = close => 1"""
        publishing = self._callFUT(datetime(2011, 2, 1),datetime(2011, 5, 1))
        self.assertEquals(publishing(datetime(2011, 5, 1)).count(), 1)

    def test_on_after(self):
        """ open < close < [today] => 0"""
        publishing = self._callFUT(datetime(2011, 2, 1),datetime(2011, 5, 1))
        self.assertEquals(publishing(datetime(2011, 6, 1)).count(), 0)

class OrderTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeOne(self, b, a, display_order=None, id=None, is_vetoed=False):
        from altaircms.topic.models import Topic
        return Topic(publish_open_on=b, 
                     publish_close_on=a, 
                     id=id, display_order=display_order)

    def test_order(self):
        """ today:2/1 => 2/1;  today:10/1 => 4/1, 3/1, 2/1
        """
        DBSession.add(self._makeOne(datetime(2011, 2, 1),datetime(9999, 2, 1), id=1))
        DBSession.add(self._makeOne(datetime(2011, 4, 1), datetime(9999, 2, 1), id=3))
        DBSession.add(self._makeOne(datetime(2011, 3, 1), datetime(9999, 2, 1), id=2))

        qs = Topic.publishing(datetime(2011, 2, 1))
        self.assertEquals([q.id for q in qs], [1])
        qs = Topic.publishing(datetime(2011, 10, 1))
        self.assertEquals([q.id for q in qs], [3, 2, 1])

    def test_order_by_close_on(self):
        """ today:1/1, topics=[2/1~4/1, 3/1~5/1]; => []
        """
        DBSession.add(self._makeOne(datetime(2011, 2, 1),datetime(2011, 4, 1), id=1))
        DBSession.add(self._makeOne(datetime(2011, 3, 1), datetime(2011, 5, 1), id=2))

        qs = Topic.publishing(datetime(2011, 1, 1))
        self.assertEquals([q.id for q in qs], [])

    def test_order_by_close_on1(self):
        """ today:2/1, topics=[2/1~4/1, 3/1~5/1]; => [2/1~4/1]
        """
        DBSession.add(self._makeOne(datetime(2011, 2, 1),datetime(2011, 4, 1), id=1))
        DBSession.add(self._makeOne(datetime(2011, 3, 1), datetime(2011, 5, 1), id=2))

        qs = Topic.publishing(datetime(2011, 2, 1))
        self.assertEquals([q.id for q in qs], [1])

    def test_order_by_close_on2(self):
        """ today:3/1, topics=[2/1~4/1, 3/1~5/1]; => [3/1~5/1, 2/1~4/1]
        """
        DBSession.add(self._makeOne(datetime(2011, 2, 1),datetime(2011, 4, 1), id=1))
        DBSession.add(self._makeOne(datetime(2011, 3, 1), datetime(2011, 5, 1), id=2))

        qs = Topic.publishing(datetime(2011, 3, 1))
        self.assertEquals([q.id for q in qs], [2, 1])

    def test_order_by_close_on3(self):
        """ today:4/1, topics=[2/1~4/1, 3/1~5/1]; => [3/1~5/1, 2/1~4/1]
        """
        DBSession.add(self._makeOne(datetime(2011, 2, 1),datetime(2011, 4, 1), id=1))
        DBSession.add(self._makeOne(datetime(2011, 3, 1), datetime(2011, 5, 1), id=2))

        qs = Topic.publishing(datetime(2011, 4, 1))
        self.assertEquals([q.id for q in qs], [2, 1])

    def test_order_by_close_on4(self):
        """ today:5/1, topics=[2/1~4/1, 3/1~5/1]; => [3/1~5/1]
        """
        DBSession.add(self._makeOne(datetime(2011, 2, 1),datetime(2011, 4, 1), id=1))
        DBSession.add(self._makeOne(datetime(2011, 3, 1), datetime(2011, 5, 1), id=2))

        qs = Topic.publishing(datetime(2011, 5, 1))
        self.assertEquals([q.id for q in qs], [2])

    def test_sorted_by_display_order5(self):
        """ today:6/1, topics=[2/1~4/1, 3/1~5/1]; => []
        """
        DBSession.add(self._makeOne(datetime(2011, 2, 1),datetime(9999, 2, 1), id=1, display_order=1))
        DBSession.add(self._makeOne(datetime(2011, 2, 1), datetime(9999, 2, 1), id=3, display_order=100))
        DBSession.add(self._makeOne(datetime(2011, 2, 1), datetime(9999, 2, 1), id=2, display_order=50))

        qs = Topic.publishing(datetime(2011, 10, 1))
        self.assertEquals([q.id for q in qs], [1, 2, 3])


        def test_unpermission(self):
            """ is vetoed ? -> not found
            """
            DBSession.add(self._makeOne(datetime(10, 1, 1), datetime(9999, 1, 1), 
                                        is_vetoed=True))
            self.assetEquals(Topic.publishing.count(), 0)

        def test_permission(self):
            """ is not vetoed ? -> found"""
            DBSession.add(self._makeOne(datetime(10, 1, 1), datetime(9999, 1, 1), 
                                        is_vetoed=False))
            self.assetEquals(Topic.publishing.count(), 1)


if __name__ == "__main__":
    unittest.main()

