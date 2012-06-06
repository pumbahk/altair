# -*- encoding:utf-8 -*-

import sys
import argparse
from datetime import datetime
import uuid

parser = argparse.ArgumentParser()
parser.add_argument("--dburl")
args = parser.parse_args()

from altaircms.page.models import Page, PageSet
from altaircms.event.models import Event
from altaircms.layout.models import Layout
from altaircms.models import Performance


def create_pageset(page, event):
    pageset = PageSet.get_or_create(page)
    pageset.name = page.title
    pageset.page = page
    pageset.event = event
    return pageset

def create_page(event, layout):
    return Page(
        title=event.title, 
        keywords=u"'チケット-演劇-クラシック-オペラ-コンサート-バレエ-ミュージカル-野球-サッカー-格闘技'", 
        description=u"チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサイトです。", 
        # structure=u'{}', 
        publish_begin=datetime(1900, 1, 1), 
        publish_end=datetime(2100, 1, 1), 
        layout = layout, 
        url = uuid.uuid4().hex #dummy
        )

def main(args):
    import sqlalchemy as sa
    import sqlahelper
    engine = sa.create_engine(args.dburl)
    sqlahelper.add_engine(engine)

    session = sqlahelper.get_session()
    qs = session.query(Event, Performance).filter(Event.title==Performance.title)


    layout = Layout.query.filter_by(template_filename="ticketstar.detail.mako").first()

    for event, perf in qs:
        perf.event = event
        if not event.pagesets:
            page = create_page(event, layout)
            pageset = create_pageset(page, event)
            event.pagesets.append(pageset)
            event.pages.append(page)
            session.add(page)

        session.add(perf)

    import transaction
    transaction.commit()

if __name__ == "__main__":
    main(args)
