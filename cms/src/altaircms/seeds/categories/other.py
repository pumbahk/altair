# -*- coding:utf-8 -*-
from ..mapping import IdNameLabelMapping
OTHER_SUBCATEGORY_CHOICES = [
    ## name, label
    ("jazz", u"ジャズ・フュージョン"), 
    ("jpop", u"J-POP・ROCK"), 
    ("enka", u"演歌・邦楽"), 
    ("nursery_rhyme", u"童謡・日本のうた"), 
    ("anime", u"アニメ音楽"), 
    ("chanson", u"シャンソン"), 
    ("pop", u"海外ROCK・POPS"), 
    ("folk", u"民謡音楽"), 
    ("festival", u"フェスティバル"), 
    ("other", u"音楽その他"), 
]
OtherSubCategoryMapping = IdNameLabelMapping.from_choices(OTHER_SUBCATEGORY_CHOICES)
