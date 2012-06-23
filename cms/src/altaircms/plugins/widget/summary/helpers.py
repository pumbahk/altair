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
            dict(label=u"説明／注意事項", name='notice', content=u"※未就学児童のご入場はお断りいたします。"), 
            ]

    return [ # todo: fixme
        dict(label=u"公演期間", name='performance_period', content=h.base.term(event.event_open, event.event_close)), 
        dict(label=u"販売期間", name="sales_period", content=h.base.term(event.deal_open,event.deal_close)), 
        dict(label=u"出演者", name="performer", content=event.performers), 
        dict(label=u"説明／注意事項", name='notice', content=event.notice), 
        dict(label=u"お支払い方法", name='ticket_payment', content=event.ticket_payment), 
        dict(label=u"チケット引き取り方法", name='ticket_pickup', content=event.ticket_pickup), 
        dict(label=u"お問い合わせ先", name='contact', content=event.inquiry_for),  
        ]
