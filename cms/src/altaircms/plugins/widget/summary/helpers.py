# -*- encoding:utf-8 -*-
###
import codecs
import sys
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
###

def _items_from_page(page):
    import altaircms.helpers as h
    event = page.event
    if event is None:
        return [
            dict(label=u"説明／注意事項", attr='class=notice', content=u"※未就学児童のご入場はお断りいたします。"), 
            ]

    return [ # todo: fixme
        dict(label=u"公演期間", attr='class=performance_period', content=h.base.term(event.event_open, event.event_close)), 
        dict(label=u"出演者", attr="class=performer", content=event.performers), 
        dict(label=u"説明／注意事項", attr='class=notice', content=event.notice), 
        dict(label=u"お問い合わせ先", attr='class=contact', content=event.inquiry_for.replace("\n", " ")),  ##newline not supported
        dict(label=u"販売期間", attr="class=sales_period", content=h.base.term(event.deal_open,event.deal_close))
        ]
