# -*- coding:utf-8 -*-
#!/usr/bin/env python 

import sys
import os
sys.path.append(os.path.absname(os.path.dirname(__name__)))
from .tssvg import (
    TSSVGEffect, 
    ReplaceMapping, 
)



mapping = {
    "MS PGothic": u"ＭＳ Ｐゴシック"
}
def convert(familyname):
    if familyname in mapping:
        return mapping[familyname]
    else:
        return familyname

target_keys = ["font-family", "-inkscape-font-specification"]


if __name__ == '__main__':
    e = TSSVGEffect(ReplaceMapping(target_keys, convert))
    # e.affect(["./sample.win.xml"])
    e.affect()
