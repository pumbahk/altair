# -*- coding:utf-8 -*-
from ..mapping import IdNameLabelMapping
MUSIC_SUBCATEGORY_CHOICES = [
    ## name, label
    ("pops-rock", u"ポップス・ロック"), 
    ("classic-opera", u"クラシック・オペラ"), 
    ("festival", u"フェスティバル"), 
    ("jazz-fusion", u"ジャズ・フュージョン"), 
    ("anime", u"アニメ音楽"), 
    ("enka-minyo", u"演歌・民謡"), 
    ("music-other", u"その他"), 
]
MusicSubCategoryMapping = IdNameLabelMapping.from_choices(MUSIC_SUBCATEGORY_CHOICES)
