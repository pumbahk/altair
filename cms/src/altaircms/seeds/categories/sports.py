# -*- coding:utf-8 -*-
from ..mapping import IdNameLabelMapping
SPORTS_SUBCATEGORY_CHOICES = [
    ## name, label
    ("baseball", u"野球"), 
    ("soccer", u"サッカー"), 
    ("golf", u"ゴルフ"), 
    ("tennis", u"テニス"), 
    ("sumo", u"相撲・格闘技"), 
    ("skate", u"スケート・ウィンタースポーツ"), 
    ("malinesports", u"水泳・マリンスポーツ"), 
    ("sports-other", u"その他"), 
]
SportsSubCategoryMapping = IdNameLabelMapping.from_choices(SPORTS_SUBCATEGORY_CHOICES)
