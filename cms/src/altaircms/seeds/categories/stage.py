# -*- coding:utf-8 -*-
from ..mapping import IdNameLabelMapping
STAGE_SUBCATEGORY_CHOICES = [
    ## name, label
    ("engeki-stage", u"演劇・ステージ"), 
    ("musical-show", u"ミュージカル・ショー"), 
    ("ballet-dance", u"バレエ・ダンス"), 
    ("performance", u"パフォーマンス"), 
    ("owarai", u"お笑い"), 
    ("yose-engei", u"寄席・演芸"), 
    ("dentougeinou", u"伝統芸能"), 
    ("stage-other", u"その他"), 
]
StageSubCategoryMapping = IdNameLabelMapping.from_choices(STAGE_SUBCATEGORY_CHOICES)
