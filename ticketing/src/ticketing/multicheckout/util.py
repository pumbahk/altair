# -*- coding:utf-8 -*-

cart_prefixes = {
    u"AMEX": ["34", "37"],
    u"DINERS": ["30", "36", "38", "39"],
    u"MASTER": ["5"],
    u"VISA": ["4"],
    u"JCB": ["35"],
}

ahead_coms = {
    u"2s59875": u"楽天 KC",
    u"2R59875": u"楽天 KC",
    u"AR59875": u"楽天 KC",
    u"2a99661": u"JCB",
    u"2a99660": u"Diners",
    }

def detect_card_brand(card_number):
    """ 
    http://ja.wikipedia.org/wiki/%E3%82%AF%E3%83%AC%E3%82%B8%E3%83%83%E3%83%88%E3%82%AB%E3%83%BC%E3%83%89%E3%81%AE%E7%95%AA%E5%8F%B7
    """
    for brand, prefixes in cart_prefixes.items():
        for prefix in prefixes:
            if card_number.startswith(prefix):
                return brand

