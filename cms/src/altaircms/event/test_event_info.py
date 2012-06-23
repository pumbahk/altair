# -*- coding:utf-8 -*-
import unittest

"""
絞り込み検索の条件のテスト
"""

def setUpModule():
    import sqlahelper
    from sqlalchemy import create_engine
    import altaircms.page.models
    import altaircms.event.models
    import altaircms.models
    import altaircms.plugins.widget.summary.models
    import altaircms.widget.models
    engine = create_engine("sqlite:///")
    engine.echo = False
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()

def tearDownModule():
    import transaction
    transaction.abort()

class GetEventInfoTests(unittest.TestCase):
    ## ちょっと面倒なので結合テストのみ

    def tearDown(self):
        import transaction
        transaction.abort()

    def setUp(self):
        import sqlahelper
        self.session = sqlahelper.get_session()
        
    def _callFUT(self, *args, **kwargs):
        from altaircms.event.event_info import get_event_notify_info
        return get_event_notify_info(*args, **kwargs)

    def test_info_from_event(self):
        from altaircms.event.models import Event
        event = Event(ticket_payment=u"this-is-the-way-of-ticket-payment", 
                      notice=u"notice\nnotice\nnotice!")

        result = self._callFUT(event)["event"]

        self.assertEquals(result[0], dict(name="notice", content=u"notice<br/>notice<br/>notice!", label=u"注意事項"))
        self.assertEquals(result[1], dict(name="ticket_payment", content=u"this-is-the-way-of-ticket-payment", label=u"お支払い方法"))

    def test_info_from_summary_widget(self):
        import json
        from altaircms.event.models import Event
        from altaircms.page.models import Page
        from altaircms.plugins.widget.summary.models import SummaryWidget

        event = Event()
        page = Page(event=event)
        widget = SummaryWidget(page=page)
        widget.items = json.dumps([
                {"name": u"name", "content": u"this-is-summary-content", "label": u"見出し"}, 
                {"content": u"no-name", "label": u"見出し"}
                ])

        self.session.add(widget)
        self.session.flush()

        result = self._callFUT(event)["event"]
        self.assertEquals(result[0], {"name": u"name", "content": u"this-is-summary-content", "label": u"見出し"})
        self.assertEquals(result[1], {"content": u"no-name", "label": u"見出し", "name": u""})

if __name__ == "__main__":
    unittest.main()
