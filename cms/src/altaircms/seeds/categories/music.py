# -*- coding:utf-8 -*-
from ..mapping import IdNameLabelMapping
MUSIC_SUBCATEGORY_CHOICES = [
    ## name, label
    ("jpops-rock", u"Jポップス・ロック"), 
    ("pops-rock", u"海外ポップス・ロック"), 
    ("classic-opera", u"クラシック・オペラ"), 
    ("festival", u"フェスティバル"), 
    ("jazz-fusion", u"ジャズ・フュージョン"), 
    ("anime", u"アニメ音楽"), 
    ("enka-minyo", u"演歌・民謡"), 
    ("music-other", u"その他"), 
]
MusicSubCategoryMapping = IdNameLabelMapping.from_choices(MUSIC_SUBCATEGORY_CHOICES)
