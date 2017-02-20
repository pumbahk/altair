# -*- coding:utf-8 -*-
from markupsafe import Markup
from datetime import datetime
from altaircms.models import Performance


def performance_purchase_text(request, performance_id, url="", sale=u"購入はこちら", before=u"販売前", after=u"販売終了"):
    performance = request.allowable(Performance).filter(Performance.id == performance_id).first()
    now = datetime.now()

    if not performance:
        return ""

    salessegments = [s for s in performance.salessegments if s.publicp]

    if not salessegments:
        return ""

    # 公演終了
    if performance.start_on < now and not performance.end_on:
        return Markup(u"""<span class="btnN">{0}</span>""".format(after))

    # 公演終了（公演終了設定あり）
    if performance.end_on and performance.end_on < now:
        return Markup(u"""<span class="btnN">{0}</span>""".format(after))

    # １つも販売開始がなければ、販売前
    start = False
    for salessegment in salessegments:
        # 販売開始
        if now > salessegment.start_on:
            start = True

    if not start:
        # 販売前
        return Markup(u"""<span class="btnO">{0}</span>""".format(before))

    # 販売期間に当てはまったら販売中
    for salessegment in salessegments:
        if salessegment.start_on <= now <= salessegment.end_on:
            return Markup(u"""<a class='btnV' href='{0}'>{1}</a>""".format(url, sale))

    # これから販売の販売区分があると販売前
    for salessegment in salessegments:
        if now < salessegment.start_on:
            return Markup(u"""<span class="btnO">{0}</span>""".format(before))

    # それ以外は、販売終了（販売期間の狭間でも、販売終了）
    return Markup(u"""<span class="btnN">{0}</span>""".format(after))
