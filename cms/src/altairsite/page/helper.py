# -*- coding:utf-8 -*-
from markupsafe import Markup
from datetime import datetime
from altaircms.models import Performance


def performance_purchase_text(request, performance_id, url="", sale=u"購入はこちら", before=u"販売前", after=u"販売終了"):
    performance = request.allowable(Performance).filter(Performance.id == performance_id).first()
    now = datetime.now()

    if not performance:
        return ""

    salessegment = performance.salessegments[0]

    # 販売前
    if now < salessegment.start_on:
        return Markup(u"""<span class="btnO">{0}</span>""".format(before))

    # 販売終了
    if salessegment.end_on < now:
        return Markup(u"""<span class="btnN">{0}</span>""".format(after))

    # 公演終了
    if performance.start_on < now and not performance.end_on:
        return Markup(u"""<span class="btnN">{0}</span>""".format(after))

    # 公演終了（公演終了設定あり）
    if performance.end_on and performance.end_on < now:
        return Markup(u"""<span class="btnN">{0}</span>""".format(after))

    return Markup(u"""<a class='btnV' href='{0}'>{1}</a>""".format(url, sale))
