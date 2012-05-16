# -*- coding:utf-8 -*-
from .mapping import IdNameLabelMapping

AREA_CHOICES = [
    ## name, label
    ("hokkaido", u"北海道"),
    ("tohoku", u"東北"),
    ("kanto", u"関東・甲信越"),##
    ("chubu", u"中部・東海"),##
    ("kinki", u"近畿・北陸"),##
    ("chugoku", u"中国・四国"),##
    ("kyushu", u"九州・沖縄"),
]

AreaMapping = IdNameLabelMapping.from_choices(AREA_CHOICES)
