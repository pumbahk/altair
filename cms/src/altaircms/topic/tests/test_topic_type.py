# -*- coding:utf-8 -*-
import unittest
import sqlalchemy as sa
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

class TopicTypeTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeObj(self, cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        DBSession.add(obj)
        return obj

    def test_is_global(self):
        target = self._makeObj(Topic, is_global=True)

        self.assertEquals(target.topic_type, "global")
        self.assertEquals(Topic.query.filter(Topic.has_global()).count(), 1)
        self.assertEquals(Topic.matched_topic_type().count(), 1)

    def test_is_not_global(self):
        target = self._makeObj(Topic, is_global=False)

        self.assertEquals(target.topic_type, None)
        self.assertEquals(Topic.query.filter(Topic.has_global()).count(), 0)
        self.assertEquals(Topic.matched_topic_type().count(), 0)

    def test_has_page(self):
        from altaircms.page.models import Page
        page = self._makeObj(Page, id=1)
        target = Topic(page=page)
        DBSession.flush()

        self.assertEquals(target.topic_type, "page:1")
        self.assertEquals(Topic.query.filter(Topic.same_page(page)).count(), 1)
        self.assertEquals(Topic.matched_topic_type(page=page).count(), 1)

    def test_has_not_page(self):
        from altaircms.page.models import Page
        page = self._makeObj(Page, id=1)
        target = Topic()
        DBSession.flush()

        self.assertNotEquals(target.topic_type, "page:1")
        self.assertEquals(Topic.query.filter(Topic.same_page(page)).count(), 0)
        self.assertEquals(Topic.matched_topic_type(page=page).count(), 0)

    def test_has_event(self):
        from altaircms.models import Event
        event = self._makeObj(Event, id=1)
        target = Topic(event=event)
        DBSession.flush()

        self.assertEquals(target.topic_type, "event:1")
        self.assertEquals(Topic.query.filter(Topic.same_event(event)).count(), 1)
        self.assertEquals(Topic.matched_topic_type(event=event).count(), 1)

    def test_has_not_event(self):
        from altaircms.models import Event
        event = self._makeObj(Event, id=1)
        target = Topic()
        DBSession.flush()

        self.assertNotEquals(target.topic_type, "event:1")
        self.assertEquals(Topic.query.filter(Topic.same_event(event)).count(), 0)
        self.assertEquals(Topic.matched_topic_type(event=event).count(), 0)

    # def test_has_category(self):
    #     target = self._makeObj(Topic, category="foo")

    #     self.assertEquals(target.topic_type, "foo")
    #     self.assertEquals(Topic.query.filter(Topic.has_category("foo")).count(), 1)
    #     self.assertEquals(Topic.matched_topic_type(category="foo").count(), 1)

    # def test_hasnot_matched_category(self):
    #     target = self._makeObj(Topic, category="boo")

    #     self.assertEquals(target.topic_type, "boo")
    #     self.assertEquals(Topic.query.filter(Topic.has_category("foo")).count(), 0)
    #     self.assertEquals(Topic.matched_topic_type(category="foo").count(), 0)

if __name__ == "__main__":
    unittest.main()

