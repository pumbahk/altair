# -*- coding:utf-8 -*-
#!/usr/bin/env python 

import platform
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import inkex
from tssvg import (
    ReplaceMapping, 
    Configurator,
    InternalFamilyNameResolver, 
    StyleReplacer, 
    get_control
)

class TSSVGEffect(inkex.Effect):
    def __init__(self, mapping):
        inkex.Effect.__init__(self, mapping)
        self.replacer = StyleReplacer(mapping)
        self.before_output_callbacks = []

    def effect(self):
        for e in self.document.iter():
            if "style" in e.attrib:
                new_attrib = self.replacer(e.attrib["style"])
                e.attrib["style"] = new_attrib

    def add_befoure_output(self, fn):
        self.before_output_callbacks.append(fn)

    def output(self):
        """Serialize document into XML on stdout"""
        for cb in self.before_output_callbacks:
            cb(self)
        self.document.write(sys.stdout, encoding="utf-8")

def control_factory():
    from ctypes import CDLL
    from ctypes.util import find_library
    def find_library2(x):
        return find_library(x) or find_library(x+"-0")
    configurator = Configurator(CDLL, find_library2)
    return get_control(configurator, platform.system())

def getapp(cache):
    family_name_resolver = InternalFamilyNameResolver(control_factory=control_factory, cache=cache)
    convert = family_name_resolver.resolve
    target_keys = ["font-family", "-inkscape-font-specification"]
    e = TSSVGEffect(ReplaceMapping(target_keys, convert))
    e.add_befoure_output(family_name_resolver.clean)
    return e

if __name__ == '__main__':
    e = getapp({}) #tbd
    # e.affect([".samples/sample.win.xml"])
    e.affect()
