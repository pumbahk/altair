#-*- coding:utf-8 -*-
from altaircms.topic.models import Topic
from altaircms.topcontent.models import Topcontent
from pyramid.renderers import render

_topic_template_name = "altaircms.plugins.widget:topic/topic_render.mako"
def render_topics(widget, topics, N, display_global=True,request=None):
    if not display_global:
        topics = topics.filter(Topic.is_global == False)
    if topics.count() > N:
        topics = list(topics)[:N] ## todo:fixme
    return render(_topic_template_name, {"widget":widget, "topics":topics}, request)

_topcontent_template_name = "altaircms.plugins.widget:topic/topcontent_render.mako"
def render_topcontent(widget, topcontents, N, display_global=True,request=None):
    if not display_global:
        topcontents = topcontents.filter(Topcontent.is_global == False)
    if topcontents.count() > N:
        topcontents = list(topcontents)[:N] ## todo:fixme
    return render(_topcontent_template_name, {"widget":widget, "topcontents":topcontents}, request)

## demo
if __name__ == "__main__":
    from datetime import datetime
    import sqlalchemy as sa
    from altaircms.models import DBSession
    from altaircms.models import Base

    engine = sa.create_engine("sqlite://")
    Base.metadata.bind = engine
    DBSession.bind = engine
    Base.metadata.create_all()

    class DummyMaker(object):
        def _makeObj(self, cls, *args, **kwargs):
            obj = cls(*args, **kwargs)
            DBSession.add(obj)
            return obj

        def get_topics(self):
            self._makeObj(Topic, publish_open_on=datetime(2011, 1, 1),
                          publish_close_on=datetime(2013, 1, 1), 
                          title=u"1. オススメ!!! 最重要(begin 2011/1/1)  1", 
                          is_global=True, 
                          orderno=1)
            self._makeObj(Topic, publish_open_on=datetime(2011, 5, 1),
                          publish_close_on=datetime(2013, 1, 1), 
                          title=u"2. 何とか(begin 2011/5/1)               50", 
                          is_global=True, 
                          orderno=50)
            self._makeObj(Topic, publish_open_on=datetime(2011, 4, 1),
                          publish_close_on=datetime(2013, 1, 1), 
                          title=u"3. かんとか(begin 2011/4/1)             50", 
                          is_global=True, 
                          orderno=50)
            self._makeObj(Topic, publish_open_on=datetime(2011, 3, 1),
                          publish_close_on=datetime(2013, 1, 1), 
                          title=u"4. ふつうな感じの告知(begin 2011/3/1)   50", 
                          is_global=True, 
                          orderno=50)
            self._makeObj(Topic, publish_open_on=datetime(2011, 3, 1),
                          publish_close_on=datetime(2013, 1, 1), 
                          title=u"5. ちょっとどうでも良い(begin 2011/5/1) 100", 
                          is_global=True, 
                          orderno=100)
            return Topic.matched_qs(datetime(2011, 7, 1))

    import os
    from mako.template import Template
    here = os.path.abspath(os.path.dirname(__file__))
    template = Template(filename=os.path.join(here, "topic_render.mako"), 
                        input_encoding="utf-8")

    class h(object):
        class base(object):
            jdate = classmethod(lambda *args, **kwargs : "")
    ## global
    print template.render(topics=DummyMaker().get_topics(), h=h)
    ## unglobal
    print template.render(topics=DummyMaker().get_topics().filter(Topic.is_global==False), h=h)

