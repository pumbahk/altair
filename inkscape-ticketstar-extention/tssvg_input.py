# -*- coding:utf-8 -*-
#!/usr/bin/env python 

import platform
import sys
import os
sys.path.append(os.path.absname(os.path.dirname(__name__)))
from .tssvg import (
    TSSVGEffect, 
    ReplaceMapping, 
    Configrator,
    InternalFamilyNameResolver, 
    get_control
)

def control_factory():
    from ctypes import CDLL
    from ctypes.util import find_library
    def find_library2(x):
        return find_library(x) or find_library(x+"-0")
    configurator = Configrator(CDLL, find_library2)
    return get_control(configurator, platform.system())

if __name__ == '__main__':
    family_name_resolver = InternalFamilyNameResolver(control_factory=control_factory, cache={})
    convert = family_name_resolver.resolve
    target_keys = ["font-family", "-inkscape-font-specification"]
    e = TSSVGEffect(ReplaceMapping(target_keys, convert))
    e.add_befoure_output(family_name_resolver.clean)
    # e.affect([".samples/sample.win.xml"])
    e.affect()
