# -*- coding:utf-8 -*-
from datetime import datetime
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


class TopicListingFull(unittest.TestCase):
    """ topicの表示のテスト
    """
    def _makeObj(self, cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        DBSession.add(obj)
        return obj

    def tearDown(self):
        import transaction
        transaction.abort()

    def getDump(self, qs):
        from StringIO import StringIO
        io = StringIO()
        for q in qs:
            io.write(q.title); io.write(u"\n")
        return io.getvalue()

    def test_it(self):
        """適切な形でトピックを取得できているか調べる

        以下のような形式で取り出したい。
        
        * まず、表示順序順に並べる 
        * 同じ表示順序の時は、開始日が最近であったものを先にする

        1. オススメ!!! 最重要(begin 2011/1/1)  1
        --------------------------------------------
        2. 何とか(begin 2011/5/1)               50
        3. かんとか(begin 2011/4/1)             50
        4. ふつうな感じの告知(begin 2011/3/1)   50
        --------------------------------------------
        5. ちょっとどうでも良い(begin 2011/5/1) 100
        """
        self._makeObj(Topic, publish_open_on=datetime(2011, 1, 1),
                      publish_close_on=datetime(2013, 1, 1), 
                      title=u"1. オススメ!!! 最重要(begin 2011/1/1)  1", 
                      is_global=True, 
                      display_order=1)
        self._makeObj(Topic, publish_open_on=datetime(2011, 5, 1),
                      publish_close_on=datetime(2013, 1, 1), 
                      title=u"2. 何とか(begin 2011/5/1)               50", 
                      is_global=True, 
                      display_order=50)
        self._makeObj(Topic, publish_open_on=datetime(2011, 4, 1),
                      publish_close_on=datetime(2013, 1, 1), 
                      title=u"3. かんとか(begin 2011/4/1)             50", 
                      is_global=True, 
                      display_order=50)
        self._makeObj(Topic, publish_open_on=datetime(2011, 3, 1),
                      publish_close_on=datetime(2013, 1, 1), 
                      title=u"4. ふつうな感じの告知(begin 2011/3/1)   50", 
                      is_global=True, 
                      display_order=50)
        self._makeObj(Topic, publish_open_on=datetime(2011, 3, 1),
                      publish_close_on=datetime(2013, 1, 1), 
                      title=u"5. ちょっとどうでも良い(begin 2011/5/1) 100", 
                      is_global=True, 
                      display_order=100)

        qs = Topic.matched_qs(datetime(2011, 7, 1)).all()
        self.assertEquals(self.getDump(qs), 
                         u"""\
1. オススメ!!! 最重要(begin 2011/1/1)  1
2. 何とか(begin 2011/5/1)               50
3. かんとか(begin 2011/4/1)             50
4. ふつうな感じの告知(begin 2011/3/1)   50
5. ちょっとどうでも良い(begin 2011/5/1) 100
""")

    def _makePageset(self, **kwargs):
        from altaircms.page.models import Page, PageSet
        pageset = PageSet()
        page = self._makeObj(Page, pageset=pageset, **kwargs)
        return pageset

    def test_multiple_items(self):
        """ 関連づいたtopicが取得できてるか調べる
        1. global
        2. eventに関連
        3. pageに関連
        渡された page, eventに関連していないtopicは取得しない
        """
        from altaircms.event.models import Event
        event0 = self._makeObj(Event)
        event1 = self._makeObj(Event)
        page0 = self._makePageset(event=event0)
        page1 = self._makePageset()

        self._makeObj(Topic, publish_open_on=datetime(2011, 1, 1),
                      publish_close_on=datetime(2013, 1, 1), 
                      title=u"global", 
                      display_order=1, 
                      is_global=True)
        self._makeObj(Topic, publish_open_on=datetime(2011, 5, 1),
                      publish_close_on=datetime(2013, 1, 1), 
                      title=u"event0", 
                      event=event0)
        self._makeObj(Topic, publish_open_on=datetime(2011, 5, 1),
                      publish_close_on=datetime(2013, 1, 1), 
                      title=u"event1", 
                      event=event1)
        self._makeObj(Topic, publish_open_on=datetime(2011, 5, 1),
                      publish_close_on=datetime(2013, 1, 1), 
                      title=u"page0", 
                      display_order=100, 
                      bound_page=page0)
        self._makeObj(Topic, publish_open_on=datetime(2011, 5, 1),
                      publish_close_on=datetime(2013, 1, 1), 
                      title=u"page1", 
                      display_order=100, 
                      bound_page=page1)

        qs = Topic.matched_qs(datetime(2011, 7, 1), page=page0, event=event0)
        self.assertEquals("global\n", self.getDump(qs))

        qs = Topic.matched_qs(datetime(2011, 7, 1), event=event0)
        self.assertEquals("global\nevent0\n", self.getDump(qs))

        qs = Topic.matched_qs(datetime(2011, 7, 1), page=page0)
        self.assertEquals("global\npage0\n", self.getDump(qs))

if __name__ == "__main__":
    unittest.main()

