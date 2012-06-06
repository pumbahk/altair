# -*- coding:utf-8 -*-
from ..mapping import IdNameLabelMapping
OTHER_SUBCATEGORY_CHOICES = [
    ## name, label
    ("other-other", u"その他"), 
]
OtherSubCategoryMapping = IdNameLabelMapping.from_choices(OTHER_SUBCATEGORY_CHOICES)
