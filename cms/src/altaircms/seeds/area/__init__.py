# -*- coding:utf-8 -*-
from ..mapping import IdNameLabelMapping

AREA_CHOICES = [
    ## name, label
    ("hokkaido", u"北海道"),
    ("tohoku", u"東北"),
    ("kitakanto", u"北関東"), 
    ("shutoken", u"首都圏"), 
    ("koshinetsu", u"甲信越"), 
    ("hokuriku", u"北陸"), 
    ("tokai", u"東海"), 
    ("kinki", u"近畿"),
    ("chugoku", u"中国"),
    ("shikoku", u"四国"), 
    ("kyushu", u"九州"),
    ("okinawa", u"沖縄")
]

AreaMapping = IdNameLabelMapping.from_choices(AREA_CHOICES)
