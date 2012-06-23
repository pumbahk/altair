# -*- coding:utf-8 -*-

import json
from ..page.models import Page
from ..plugins.widget.summary.models import SummaryWidget

__all__ = "get_event_notify_content"


## todo: 粗結合


### helper
from zope.interface import Interface
from zope.interface import Attribute
class IGetEventInfo(Interface):
    """購入ページ(cart)でイベント詳細情報を通知するために使われる"""
    target = Attribute("resource of event info")
    def get_event_info():
        """ event info:
        # [{"label": u"お問い合わせ先", "name": "contact", "content": u"お問い合わせ先は以下のとおりxxx-xxx-xx"}, 
           ...]
        """
        pass

class InfoAppender(object):
    def __init__(self):
        self.content = []

    def append(self, name, label, content, convert=lambda x : x):
        # {"label": u"お問い合わせ先", "name": "contact", "content": u"お問い合わせ先は以下のとおりxxx-xxx-xx"}
        if content:
            self.content.append(dict(label=label, name=name, content=convert(content)))
        return self


## adpaters

class EventGetEventInfoAdapter(object):
    def __init__(self, event):
        self.target = event

    def get_event_info(self):
        event = self.target
        nl_to_br = lambda s : s.replace("\n", "<br/>")

        appender = InfoAppender()
        appender.append("performer", u"出演者リスト", event.performers)
        appender.append("contact", u"お問い合わせ先", event.inquiry_for, nl_to_br)
        appender.append("notice", u"注意事項", event.notice, nl_to_br)
        appender.append("ticket_payment", u"お支払い方法", event.ticket_payment, nl_to_br)
        appender.append("ticket_pickup", u"チケット引き取り方法", event.ticket_pickup, nl_to_br)
        return {"event": appender.content}    


class SummaryWidgetGetEventInfoAdapter(object):
    def __init__(self, widget):
        self.target = widget

    def get_event_info(self):
        nl_to_br = lambda s : s.replace("\n", "<br/>")
        appender = InfoAppender()

        items = json.loads(self.target.items)
        for v in items:
            if v.get("notify"):
                appender.append(v.get("name", u""), v["label"], v["content"], nl_to_br)
        return {"event": appender.content}    

def get_event_notify_info(event):
    ## summary widgetで「購入ページのイベント詳細として利用する」の欄を有効にしたwidgetが購入画面(カート)
    ## のイベント詳細に利用される
    summary_widget = SummaryWidget.query.filter_by(bound_event=event).first()

    ## 本当はregistryのadaptersから引っ張る
    if summary_widget:
        return SummaryWidgetGetEventInfoAdapter(summary_widget).get_event_info()
    else:
        return EventGetEventInfoAdapter(event).get_event_info()

