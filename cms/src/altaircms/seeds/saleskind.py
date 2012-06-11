# -*- coding:utf-8 -*-
from .mapping import IdNameLabelMapping

SALESKIND_CHOICES = [
    ## name, label
    ("first_lottery", u"最速抽選"),
    ("early_lottery", u"先行抽選"), 
    ("eary_fisrtcome", u"先行先着"), 
    ("normal", u"一般販売"), 
    ("added_lottery", u"追加抽選")
]

SaleskindMapping = IdNameLabelMapping.from_choices(SALESKIND_CHOICES)
