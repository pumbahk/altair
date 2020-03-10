# -*- coding:utf-8 -*-
ahead_coms = {
    u"2s59875": u"楽天 KC",
    u"2R59875": u"楽天 KC",
    u"AR59875": u"楽天 KC",
    u"2a99661": u"JCB",
    u"2a99660": u"Diners",
    }


def get_pgw_ahead_com_name(code):
    return ahead_coms.get(code, u'不明な仕向先')
