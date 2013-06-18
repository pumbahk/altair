# -*- encoding:utf-8 -*-
###
import codecs
import sys
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
import logging
logger = logging.getLogger(__name__)
###
import altaircms.helpers as h

def _items_from_page(page):
    try:
        event = page.event
        if event is None:
            return [
                dict(label=u"説明／注意事項", name='notice', content=u"※未就学児童のご入場はお断りいたします。", notify=True), 
                ]


        event_summary = [dict(label=u"公演期間", name='performance_period', content=h.term(event.event_open, event.event_close), notify=False)]
        sorted_sgs = sorted(event.salessegment_groups, key=lambda g: g.start_on)
        salessegments_summary = [dict(label=u"販売期間: %s" % g.master.label, name=u"salessegment:%s" % g.id, content=h.term(g.start_on, g.end_on)) for g in sorted_sgs]
        retval = []
        retval.extend(event_summary)
        retval.extend(salessegments_summary)
        retval.extend([
                dict(label=u"出演者", name="performer", content=event.performers, notify=True),  
                dict(label=u"説明／注意事項", name='notice', content=event.notice, notify=True),  
                dict(label=u"お支払い方法", name='ticket_payment', content=event.ticket_payment, notify=True),  
                dict(label=u"チケット引き取り方法", name='ticket_pickup', content=event.ticket_pickup, notify=True),  
                dict(label=u"お問い合わせ先", name='contact', content=event.inquiry_for, notify=True),   
                ])
        return retval
    except Exception, e:
        logger.exception(str(e))
        return []
