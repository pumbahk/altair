# -*- coding:utf-8 -*-
from .mapping import IdNameLabelMapping

SALESKIND_CHOICES = [
    ## name, label
    ("first_lottery", u"最速抽選"),
    ("early_lottery", u"先行抽選"), 
    ("early_firstcome", u"先行先着"),
    ("normal", u"一般発売"), 
    ("added_sales", u"追加発売"),
    ("added_lottery", u"追加抽選"),
    ("vip", u"関係者"),
    ("other", u"その他")
]


SaleskindMapping = IdNameLabelMapping.from_choices(SALESKIND_CHOICES)
