# -*- coding:utf-8 -*-
from ..mapping import IdNameLabelMapping
OTHER_SUBCATEGORY_CHOICES = [
    ## name, label
    ("sircus", u"サーカス"), 
    ("fanevent", u"ショー・ファンイベント"), 
    ("festival", u"祭り・花火大会"), 
    ("bijutu", u"美術館・博物館"), 
    ("akurankai", u"博覧会・展示会"), 
    ("talkshow", u"講演会・トークショー"), 
    ("magic", u"マジック・イリュージョン"), 
    ("other-other", u"その他"), 
]
OtherSubCategoryMapping = IdNameLabelMapping.from_choices(OTHER_SUBCATEGORY_CHOICES)


