# -*- coding:utf-8 -*-
#!/usr/bin/env python 

import sys
import os
from functools import partial
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from tssvg import (
    TSSVGEffect, 
    ReplaceMapping, 
)



mapping = {
    "MS PGothic": u"ＭＳ Ｐゴシック"
}
def convert(familyname, mapping=mapping):
    if familyname in mapping:
        return mapping[familyname]
    else:
        return familyname

target_keys = ["font-family", "-inkscape-font-specification"]

def getapp(mapping=mapping):
    return TSSVGEffect(ReplaceMapping(target_keys, partial(convert, mapping=mapping)))

if __name__ == '__main__':
    e = getapp()
    # e.affect(["./sample.win.xml"])
    e.affect()
