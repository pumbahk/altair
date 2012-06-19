# -*- encoding:utf-8 -*-

import unittest
from datetime import datetime
from datetime import timedelta

"""
絞り込み検索の条件のテスト
"""

def setUpModule():
    import sqlahelper
    from sqlalchemy import create_engine
    import altaircms.page.models
    import altaircms.event.models
    import altaircms.models
    import altaircms.tag.models
    import altaircms.asset.models

    engine = create_engine("sqlite:///")
    engine.echo = False
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()

def tearDownModule():
    import transaction
    transaction.abort()


class BuildSolrDocTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()
        self.session.remove()

    def setUp(self):
        import transaction
        import sqlahelper
        transaction.abort()
        self.session = sqlahelper.get_session()
    
    def _callFUT(self, *args, **kwargs):
        from altaircms.page.api import  doc_from_page
        return doc_from_page(*args, **kwargs)

    def test_build_from_page_simple(self):
        from altaircms.page.models import Page
        page = Page()
        result = self._callFUT(page)
        self.assertEquals(sorted(["page_title", "page_description", "page_id"]), 
                         sorted(result.doc.keys()))

    def test_build_from_fullset(self):
        from altaircms.page.models import Page
        from altaircms.models import Performance
        from altaircms.page.models import PageSet
        from altaircms.event.models import Event
        from altaircms.tag.models import PageTag

        event = Event(title=u"this-is-event-title", 
                      description=u"this-is-event-description", 
                      subtitle=u"~event is event~")
        perf0 = Performance(event=event, 
                            title=u"this-is-performance-title", 
                            venue=u"this-is-performance-venue", 
                            backend_id=1, 
                            )
        pageset = PageSet(name=u"this-is-pageset-name", event=event)
        page = Page(name=u"this-is-page-name", pageset=pageset, event=event, 
                    title=u"this-is-page-title", 
                    description=u"this-is-description-of-page")
        page.tags.append(PageTag(label=u"this-is-page-tag-for-search", publicp=True))
        

        self.session.add(page)
        self.session.flush()

        result = self._callFUT(page).doc

        self.assertEquals(result["event_description"], "this-is-event-description")
        self.assertEquals(result["page_tag"], [u"this-is-page-tag-for-search"])
        self.assertEquals(result["event_title"], "this-is-event-title")
        self.assertEquals(result["page_description"], "this-is-description-of-page")
        self.assertEquals(result["performance_venue"], ["this-is-performance-venue"])
        self.assertEquals(result["page_title"], "this-is-page-title")
        self.assertEquals(result["event_subtitle"], "~event is event~")

        self.assertTrue(result["page_id"])
        self.assertTrue(result["pageset_id"])
        self.assertTrue(result["id"])
        self.assertEquals(result["id"], result["pageset_id"])

if __name__ == "__main__":
    unittest.main()
